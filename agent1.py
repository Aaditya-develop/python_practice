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

llm = ChatOpenAI(model = "gpt-4o", temperature = 0)

embeddings = OpenAIEmbeddings()
sample_texts = [
    "LangGraph is a library for building stateful multi-step applications with LLMs",
    "RAG combines information retrieval with text generation using vector databases",
    "Vector databases store high dimensional vectors and enable similarity search",
    "Agentic systems can take actions and make decisions based on their environment"
]

#Store relevant documents in documents, iterate over sample_texts and convert to Document object
documents = []
for text in sample_texts:
    documents.append(Document(page_content=text))

vectorstore = FAISS.from_documents(documents, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

#Line 2 → builds the filing cabinet
#Line 3 → hires the librarian to search it 

def retrieve(state: AgentState) -> AgentState:
    question = state["question"]
    rtrv = retriever.invoke(question)
    return {**state, "documents": rtrv}

def generate(state: AgentState) -> AgentState:
    question = state["question"]
    documents = state["documents"]
    
    context = ""
    for doc in documents:
        context = context + doc.page_content + "\n\n"
    
    prompt = f"""Use these following documents to answer the question
    
    Documents: {context}
    question: {question}
    
    Answer: """
    
    response = llm.invoke(prompt)
    return{**state, "answer": response.content}

workflow = StateGraph(AgentState)

workflow.add_node("retrieve", retrieve)
workflow.add_node("generate", generate)

workflow.set_entry_point("retrieve")

workflow.add_edge("retrieve", "generate")

workflow.add_edge("generate", END)

app = workflow.compile()

result = app.invoke({
    "question": "What is RAG?",
    "documents": [],
    "answer": ""
})

print(result["answer"])