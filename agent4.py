from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_tavily import TavilySearch
from dotenv import load_dotenv
import os

load_dotenv()

class AgentState(TypedDict):
    question: str
    documents: List[Document]
    answer: str
    is_retrieval: str
    chat_history: List
    tool_result: str

llm = ChatOpenAI(model = "gpt-4o", temperature = 0)
embeddings = OpenAIEmbeddings(model = "text-embedding-3-small")

sample_texts = [
    "LangChain is a framework for building applications powered by large language models",
    "Vector embeddings represent text as numerical vectors for semantic search",
    "Retrieval Augmented Generation combines document retrieval with text generation",
    "LangGraph extends LangChain with stateful multi step agent workflows"
]

documents = []
for text in sample_texts:
    documents.append(Document(page_content = text))

#Our place we store our vectors right now
vectorstore = FAISS.from_documents(documents, embeddings)

#Search vector store according to the question and return 2 documents
retriever = vectorstore.as_retriever(search_kwargs = {"k": 2})

#means when the agent searches the web, return the top 3 results.
search_tool = TavilySearch(max_results = 3)

def decide(state: AgentState) -> AgentState:
    question = state["question"]
    is_retrieval = state["is_retrieval"]
    chat_history = state["chat_history"]
    
    prompt = f""" You are an AI with broad knowledge. 
    
    previous conversation: {chat_history}
    
    Question: {question}
    
    Decide how to answer:
    - Answer SEARCH if the question needs current/real time information from the web
    - Answer RETRIEVE if the question needs specific document knowledge
    - Answer GENERATE if you can answer from general knowledge or conversation history
    
    Answer only with the words SEARCH, RETRIEVE, GENERATE"""
    
    response = llm.invoke(prompt)
    content = response.content.upper().strip()
    
    if "RETRIEVE" in response.content:
        is_retrieval = "retrieve"
    elif "SEARCH" in response.content:
        is_retrieval = "search"
    else:
        is_retrieval = "generate"
    
    return{**state, "is_retrieval": is_retrieval}

def retrieve(state: AgentState) -> AgentState:
    question = state["question"]
    rtrv = retriever.invoke(question)
    #this line means find documents in retriever that relate to question
    
    return{**state, "documents": rtrv}

def tool_execute(state: AgentState) -> AgentState:
    question = state["question"]
    tool_search = search_tool.invoke(question)
    
    return {**state, "tool_result": tool_search}

def generate(state: AgentState) -> AgentState:
    question = state["question"]
    documents = state["documents"]
    chat_history = state["chat_history"]
    tool_result = state["tool_result"]
    context = ""
    for doc in documents:
        context = context + doc.page_content + "\n\n"
    
    if context:
        prompt = f"""Use these documents to answer this question.
        Documents: {context}
        Question: {question}
        Answer: """
    elif tool_result:
        prompt = f"""Use these web search results to answer the question
        Search Reesults: {tool_result}
        Question: {question}
        Answer: """
    else:
        prompt = f"""Answer using conversation history.
        History: {chat_history}
        Question: {question}
        Answer:"""
    
    response = llm.invoke(prompt)
    state["chat_history"].append({
        "question": question,
        "answer": response.content
    })
    return{**state, "answer": response.content}

def should_route(state: AgentState) -> str:
    is_retrieval = state["is_retrieval"]
    
    if is_retrieval == "search":
        return "search"
    elif is_retrieval == "retrieve":
        return "retrieve"
    else:
        return "generate"

workflow = StateGraph(AgentState)
workflow.set_entry_point("decide")
workflow.add_node("decide", decide)
workflow.add_node("retrieve", retrieve)
workflow.add_node("tool_execute", tool_execute)
workflow.add_node("generate", generate)
workflow.add_conditional_edges(    
    "decide",
    should_route,
    {
        "search": "tool_execute",
        "retrieve": "retrieve",
        "generate": "generate"
    }
)

workflow.add_edge("tool_execute", "generate")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", END)

app = workflow.compile()
chat_history = []

while True:
    question = input("You: ")
    if question == "quit":
        break
     
    result = app.invoke(
        {
            "question": question,
            "documents": [],
            "answer": "",
            "is_retrieval": "",
            "chat_history": chat_history,
            "tool_result": ""
        }
    )

    chat_history = result["chat_history"]
    print("Agent:", result["answer"])
    print()

