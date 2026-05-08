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
    
llm = ChatOpenAI(model = "gpt-4o", temperature = 0)
vs = VectorStore()

search_tool = TavilySearch(max_results = 3)

def decide(state: AgentState) -> AgentState:
    question = state["question"]
    chat_history = state["chat_history"]
    
    prompt = f"""You are an AI assistant with access to a PDF about the Attention mechanism and Transformers.

    Question: {question}

    Decide how to answer:
    - Answer RETRIEVE if the question is about attention mechanisms, transformers, neural networks, or anything that could be in a research paper
    - Answer SEARCH if the question needs current real-time information from the web
    - Answer GENERATE if it is a simple question you can answer directly like math or greetings

    Answer with only one word: RETRIEVE, SEARCH, or GENERATE"""
        
    response = llm.invoke(prompt)
    if "SEARCH" in response.content.upper().strip():
        return {**state, "is_retrieval": "search"}
    elif "RETRIEVE" in response.content.upper().strip():
        return {**state, "is_retrieval": "retrieve"}
    else:
        return {**state, "is_retrieval": "generate"}
    
def tool_search(state:AgentState) -> AgentState:
    question = state["question"]
    response = search_tool.invoke(question)
    return{**state, "tool_result": response}

def retrieve(state: AgentState) -> AgentState:
    question = state["question"]
    rtrv = vs.search(question, 2)
    return{**state, "documents": rtrv}

def generate(state: AgentState) -> AgentState:
    question = state["question"]
    documents = state["documents"]
    tool_search = state["tool_result"]
    is_retrieval = state["is_retrieval"]
    chat_history = state["chat_history"]
    
    context = ""
    for doc in documents:
        context = context + doc.page_content
    
    if "search" in is_retrieval:
        prompt = f""" Generate a response using this content from the web as your information source. 
        question: {question}
        information: {tool_search}
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
    return{**state, "answer": response.content}

def should_route(state: AgentState) -> str:
    if state["is_retrieval"] == "search":
        return "search"
    elif state["is_retrieval"] == "retrieve":
        return "retrieve"
    else:
        return "generate"

workflow = StateGraph(AgentState)

workflow.set_entry_point("decide")
workflow.add_node("decide", decide)
workflow.add_node("retrieve", retrieve)
workflow.add_node("tool_search", tool_search)
workflow.add_node("generate", generate)
workflow.add_conditional_edges(
    "decide",
    should_route, {
        "search": "tool_search",
        "retrieve": "retrieve",
        "generate": "generate"
    }
)


workflow.add_edge("tool_search", "generate")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

app = workflow.compile()
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
        "tool_result": ""
    }
    )
    
    chat_history = response["chat_history"]
    print("Agent:", response["answer"])
    print()