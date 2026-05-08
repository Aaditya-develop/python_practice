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

