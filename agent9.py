from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
from vectorstore import VectorStore

load_dotenv()

class AgentState(TypedDict):
    question: str
    documents: List[Document]
    answer: str
    is_retrieval: str
    chat_history: List
    tool_result: str
    documents_relevant: bool
    rewritten_query: str
    retry_count: int
    hallucination_count: int
    
llm = ChatOpenAI(model = "gpt-4o", temperature = 0)
vs = VectorStore()
search_tool = TavilySearch(max_results = 3)


def decide(state: AgentState) -> AgentState:
    question = state["question"]
    chat_history = state["chat_history"]
    prompt = f"""You are a router. Decide how to answer this question.

    Rules:
    - If the question is about a specific document, table, paper, or technical content → RETRIEVE
    - If the question needs current news or live information → SEARCH  
    - If the question is general knowledge or conversational → GENERATE

    Question: {question}
    Chat history: {chat_history}

    Respond with ONE word only: RETRIEVE, SEARCH, or GENERATE
    """
    response = llm.invoke(prompt)
    print("DEBUG decide:", repr(response.content))
    return{**state, "is_retrieval": response.content}


def retrieve(state: AgentState) -> AgentState:
    question = state["question"]
    rtrv = vs.search(question, 2) #Sarch vector DB store right documents here (Matching)
    for i, doc in enumerate(rtrv):
        print(f"\nQuestion: {question} \nDEBUG CHUNK: {i+1}:", doc.page_content[:200])
    return{**state, "documents": rtrv}

def tool_search(state: AgentState) -> AgentState:
    question = state["question"]
    search = search_tool.invoke(question)
    return {**state, "tool_result": search}

def should_route(state: AgentState) -> str:
    if "search" in state["is_retrieval"].lower():
        return "search"
    elif "retrieve" in state["is_retrieval"].lower():
        return "retrieve"
    else:
        return "generate"

def grade(state: AgentState) -> AgentState:
    question = state["question"]
    documents = state["documents"]
    rel_docs = []
    for doc in documents:
        prompt = f"""Is this specific document chunk relevant for this question?
        document chunk: {doc}
        question: {question}
        Answer with YES or NO"""
        response = llm.invoke(prompt)
        if "yes" in response.content.lower():
            rel_docs.append(doc)

    if len(rel_docs) > 0:
        print("DEBUG grade: docs relevant")  # add this
        return {**state, "documents": rel_docs, "documents_relevant": True}
    else:
        print("DEBUG grade: docs NOT relevant")  # add this
        return {**state, "documents_relevant": False}
  
def should_grade(state: AgentState) -> str:
    if state["documents_relevant"] == True:
        return "generate"
    elif state["retry_count"] < 1:
        return "rewrite"
    else:
        return "web_search"
    
def rewrite(state: AgentState) -> AgentState:
    question = state["question"]
    retry_count = state["retry_count"]
    prompt = f"""Rewrite this question to be more specific for document retrieval
    Make it more precide and use key technical terms.
    Original Question: {question}
    Rewritten Question:"""
    
    response = llm.invoke(prompt)
    rewritten = response.content
    
    return{**state, "question": rewritten, "rewritten_query": rewritten, "retry_count": retry_count + 1}

def hallucination_check(state: AgentState) -> AgentState:
    answer = state["answer"]
    documents = state["documents"]
    h_count = state["hallucination_count"]
    
    context = ""
    for doc in documents:
        context = context + doc.page_content
    
    prompt = f"""Does this answer actually get supported by these documents given here?
    Answer: {answer}
    documents: {context}
    Only Answer with the choices provided below.
    Answer YES if the answer is supported by the documents.
    Answer NO if the answer contains information not found in the documents.
    """
    response = llm.invoke(prompt)
    if "yes" in response.content.lower():
        print("DEBUG hallucination_check: PASSED")  # add
        return {**state, "hallucination_count": h_count}
    else:
        print("DEBUG hallucination_check: FAILED - regenerating")  # add
        return {**state, "hallucination_count": h_count+1}

def should_hallucinate(state: AgentState) -> str:
    if state["hallucination_count"] == 0:
        return "pass"    
    elif state["hallucination_count"] < 2:
        return "regenerate"
    else:
        return "pass"

def generate(state: AgentState) -> AgentState:
    question = state["question"]
    documents = state["documents"]
    is_retrieval = state["is_retrieval"].lower()
    chat_history = state["chat_history"]
    tool_result = state["tool_result"]
    rewritten_query = state["rewritten_query"]

    effective_question = rewritten_query if rewritten_query else question

    context = "".join(doc.page_content for doc in documents)

    if "search" in is_retrieval:
        prompt = f"""Generate a response using this content from the web as your information source.
        question: {effective_question}
        information: {tool_result}
        Answer: """
    elif "retrieve" in is_retrieval:
        prompt = f"""Generate a response using the document content below.
        The documents may contain raw table data — do your best to interpret it.
        If you can see numbers that likely answer the question, use them.
        Only say "I don't know" if the documents contain absolutely nothing related.

        Question: {effective_question}
        Documents: {context}
        Answer:"""
    else:
        prompt = f"""Generate a response using your knowledge and chat history.
        question: {effective_question}
        chat history: {chat_history}
        Answer: """

    response = llm.invoke(prompt)
    state["chat_history"].append({
        "question": question,
        "answer": response.content
    })
    return {**state, "answer": response.content}

workflow = StateGraph(AgentState)

workflow.add_node("decide", decide)
workflow.add_node("retrieve", retrieve)
workflow.add_node("tool_search", tool_search)
workflow.add_node("generate", generate)
workflow.add_node("grade", grade)
workflow.add_node("rewrite", rewrite)
workflow.add_node("hallucination_check", hallucination_check)


workflow.set_entry_point("decide")
workflow.add_conditional_edges(
    "decide",
    should_route, {
    "search": "tool_search",
    "retrieve": "retrieve",
    "generate": "generate"
    }
)
workflow.add_edge("retrieve", "grade")

workflow.add_conditional_edges(
    "grade",
    should_grade, {
        "generate": "generate",
        "rewrite": "rewrite",
        "web_search": "tool_search"
    }
)

workflow.add_edge("rewrite", "retrieve") #Loops back
workflow.add_edge("tool_search", "generate")
workflow.add_edge("generate", "hallucination_check")

workflow.add_conditional_edges(
    "hallucination_check",
    should_hallucinate, {
        "pass": END,
        "regenerate": "generate"
    }
)

app = workflow.compile()

def looped_run():
    chat_history = []
    while True:
        question = input("You: ")
        if "quit" in question.lower():
            break

        response = app.invoke({
            "question": question,
            "documents": [],
            "answer": "",
            "is_retrieval": "",
            "chat_history": chat_history,
            "tool_result": "",
            "documents_relevant": False,
            "rewritten_query": "",
            "retry_count": 0,
            "hallucination_count": 0
        })

        chat_history = response["chat_history"]
        print("Agent:", response["answer"])
        print()

looped_run()

