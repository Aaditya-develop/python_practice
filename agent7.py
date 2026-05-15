from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
from vectorstore import VectorStore


class AgentState(TypedDict):
    question: str
    documents: List[Document]
    answer: str
    is_retrieval: str
    chat_history: List
    tool_result: str
    documents_relevant: bool

llm = ChatOpenAI(model = "gpt-4o", temperature = 0)
vs = VectorStore()

search_tool = TavilySearch(max_results = 3)
    
def decide(state: AgentState)-> AgentState:
    question = state["question"]
    chat_history = state["chat_history"]
    
    prompt = f"""You are an AI assistant. You will decide whether we need to search the web, or retrieve documents or simply just generate.
    question: {question}
    if you need to generate, you have this chat history to answer with
    chat history: {chat_history}
    Respond only with SEARCH, GENERATE, RETRIEVE
    """
    
    response = llm.invoke(prompt)
    
    if "search" in response.content.lower():
        return {**state, "is_retrieval": "search"}
    elif "retrieve" in response.content.lower():
        return {**state, "is_retrieval": "retrieve"}
    else:
        return {**state, "is_retrieval": "generate"}

def tool_search(state: AgentState)-> AgentState:
    question = state["question"]
    response = search_tool.invoke(question)
    return{**state, "tool_result": response} #Return String attribute

def retrieve(state: AgentState) -> AgentState:
    question = state["question"]
    rtrv = vs.search(question, 2)
    #Debug, see chunks taken
    print("DEBUG")
    for i, doc in enumerate(rtrv):
        print(f"\n-- Chunk {i+1} --")
        print({doc.page_content})
    print("DEBUG\n\n")
    return{**state, "documents": rtrv}

def grade(state: AgentState) -> AgentState:
    question = state["question"]
    documents = state["documents"]
    rel_docs = []
    for doc in documents:
        prompt = f""" Is this specific document chunk relevant for this question?
        document chunk: {doc}
        question: {question}
        Answer with YES or NO"""
        
        response = llm.invoke(prompt)
        if "yes" in response.content.lower():
            rel_docs.append(doc)
    
    if len(rel_docs) > 0:
        return{**state, "documents": rel_docs, "documents_relevant": True}
    else:
        return {**state, "documents_relevant": False}

def should_grade(state: AgentState) -> str:
    if state["documents_relevant"] == True:
        return "generate"
    else:
        return "web_search"
    
def should_route(state: AgentState) -> str:
    if state["is_retrieval"] == "search":
        return "search"
    elif state["is_retrieval"] == "retrieve":
        return "retrieve"
    else:
        return "generate"

def generate(state: AgentState) -> AgentState:
    question = state["question"]
    documents = state["documents"]
    is_retrieval = state["is_retrieval"]
    chat_history = state["chat_history"]
    tool_result = state["tool_result"]
    
    context = ""
    for doc in documents:
        context = context + doc.page_content

    if "search" in is_retrieval:
        prompt = f""" Generate a response using this content from the web as your information source.
        question: {question}
        information: {tool_result}
        Answer: """
    elif "retrieve" in is_retrieval:
        prompt = f"""Generate a response using ONLY the document content below.
        If the answer is not in the documents say "I don't know based on the provided documents."
        Always cite which part of the document you used.

        Question: {question}
        Documents: {context}
        Answer:"""
    else:
        prompt = f""" Generate a response using your knowledge and chat history.
        question: {question}
        information: {chat_history}
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

workflow.set_entry_point("decide")
workflow.add_edge("retrieve", "grade")
workflow.add_conditional_edges(
    "decide",
    should_route,{
        "search": "tool_search",
        "retrieve": "retrieve",
        "generate": "generate"
    }
)
workflow.add_conditional_edges(
    "grade",
    should_grade, {
        "web_search": "tool_search",
        "generate": "generate"
    }
)

workflow.add_edge("tool_search", "generate")
workflow.add_edge("generate", END)

app = workflow.compile()

test_question = "In Table 3, what is the BLEU score for the model variation where d_k is 16?"
initial_state = app.invoke({
    "question": test_question,
    "documents": [],
    "answer": "",
    "is_retrieval": "",
    "chat_history": [], # Keep this empty to test retrieval in isolation
    "tool_result": "",
    "documents_relevant": False
})
result = app.invoke(initial_state)
for i, doc in enumerate(initial_state["documents"]):
    print(f"\n--- Chunk {i+1} Text Content ---")
    print(doc.page_content)

def looped_run():
    chat_history = []
    while True:
        question = input("You: ")
        if "quit" in question:
            break
        
        response = app.invoke({
            "question": question,
            "documents": [],
            "answer": "",
            "is_retrieval": "",
            "chat_history": chat_history,
            "tool_result": "",
            "documents_relevant": False
        })
        
        chat_history = response["chat_history"]
        print("Agent:", response["answer"])
        print()
    