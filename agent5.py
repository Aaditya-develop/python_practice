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
    research: str
    report: str
    chat_history: List
    
llm = ChatOpenAI(model = "gpt-4o", temperature = 0)
embeddings = OpenAIEmbeddings(model = "text-embedding-3-small")

sample_texts = [
    "LangGraph is a library for building stateful multi-step agent workflows",
    "Multi-agent systems use specialized agents that hand off tasks to each other",
    "RAG systems combine document retrieval with LLM generation for accurate answers",
    "Production AI systems require evaluation, monitoring and proper data ingestion"
]
documents = []
for text in sample_texts:
    documents.append(Document(page_content=text))

vectorstore = FAISS.from_documents(documents, embeddings)
retriever = vectorstore.as_retriever(search_kwargs = {"k": 2})

search_tool = TavilySearch(max_results = 3)

def research_agent(state: AgentState) -> AgentState:
    question = state["question"]
    #String
    search_response = search_tool.invoke(question)
    #List
    retriever_response = retriever.invoke(question)

    doc_text = ""
    for doc in retriever_response:
        doc_text = doc_text + doc.page_content + "\n\n"
    combined = f"Web search results:\n{search_response}\n\nDocument results:\n{doc_text}"
    return{**state, "research": combined}

def writer_agent(state: AgentState) -> AgentState:
    question = state["question"]
    research = state["research"]
    prompt = f"""Generate the answer for this question using the research I have provided.
    Question: {question}
    Research: {research}
    Answer: """
    
    response = llm.invoke(prompt)
    state["chat_history"].append({
        "question": question,
         "answer": response.content
        })
    
    return{**state, "report": response.content}

workflow = StateGraph(AgentState)

workflow.set_entry_point("research")
workflow.add_node("research", research_agent)
workflow.add_node("report", writer_agent)

workflow.add_edge("research", "report")
workflow.add_edge("report", END)

chat_history = []
app = workflow.compile()


while True:
    question = input("You: ")
    
    if question == "quit":
        break
    
    result = app.invoke(
        {
        "question": question,
        "research": "",
        "report": "",
        "chat_history": chat_history
        }
    )
    
    chat_history = result["chat_history"]
    print("Agent:", result["report"])
    print()
