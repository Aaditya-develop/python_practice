from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
    question: str
    documents: List[Document]
    answer: str
    is_retrieval: bool
    chat_history: List

llm = ChatOpenAI(model = "gpt-4o", temperature = 0)
embeddings = OpenAIEmbeddings(model = "text-embedding-3-small")


sample_texts = [
    "FastAPI is a modern web framework for building APIs with Python",
    "PostgreSQL is a powerful open source relational database system",
    "Docker is a platform for developing and running applications in containers",
    "Redis is an in-memory data structure store used as a cache and message broker"
]

documents = []
for text in sample_texts:
    documents.append(Document(page_content= text))

vectorstore = FAISS.from_documents(documents, embeddings)
retriever = vectorstore.as_retriever(search_kwargs = {"k":2})


def decide(state: AgentState) -> AgentState:
    question = state["question"]
    is_retrieval = state["is_retrieval"]
    chat_history = state["chat_history"]
    prompt = f"""You have this conversation history:
    {chat_history}

    New question: {question}

    Do you need to search external documents to answer this question, or can you answer from the conversation history alone?
    Answer with only Y (need documents) or N (can answer from history).
    Answer:"""    
    
    response = llm.invoke(prompt)
    
    if "y" in response.content.lower():
        is_retrieval = True
    else:
        is_retrieval = False
    return{**state, "is_retrieval": is_retrieval}

def retrieve(state: AgentState) -> AgentState:
    question = state["question"]
    rtrv = retriever.invoke(question)
    
    return{**state, "documents": rtrv}

def generate(state: AgentState) -> AgentState:
    question = state["question"]
    documents = state["documents"]
    chat_history = state["chat_history"]
    #prompt needs one full string of text, not a documents list thats why we combine it
    context = ""
    for doc in documents:
        context = context + doc.page_content + "\n\n"
    
    if context:
        prompt = f"""Use these documents to answer the question.
        Previous conversation:
        {chat_history}
        Documents: {context}
        Question: {question}
        Answer:"""
        
    else:
        prompt = f"""Answer the question using only the conversation history below.
        Previous conversation:
        {chat_history}
        Question: {question}
        Answer:"""
        
    response = llm.invoke(prompt)
    state["chat_history"].append({
        "question": question, 
        "answer": response.content
        })
    return{**state, "answer": response.content}
    
def should_retrieve(state: AgentState) -> str:
    is_retrieval = state["is_retrieval"]
    if is_retrieval == True:
        return "retrieve"
    else:
        return "generate"
    
workflow = StateGraph(AgentState)
workflow.set_entry_point("decide")
workflow.add_node("decide", decide)
workflow.add_node("retrieve", retrieve)
workflow.add_node("generate", generate)

workflow.add_conditional_edges(
    "decide",
    should_retrieve,
    {
        "retrieve": "retrieve",
        "generate": "generate"
    }
)

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
            "chat_history": chat_history
        }
    )
    
    chat_history = result["chat_history"]
    print("Agent:", result["answer"])
    print()