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
    
llm = ChatOpenAI(model = "gpt-4o", temperature = 0)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

sample_texts = [
    "Python is a high level programming language known for its simplicity and readability",
    "Machine learning is a subset of AI that enables systems to learn from data",
    "Neural networks are computing systems inspired by the human brain",
    "Deep learning uses multiple layers of neural networks to analyze data"
]

documents = []
for text in sample_texts:
    documents.append(Document(page_content = text))
#Store all texts from the document into documents 
#so we have just the text in one list


# takes documents, converts them to vectors using OpenAI embeddings, stores them in FAISS.
vectorstore = FAISS.from_documents(documents, embeddings)
retriever = vectorstore.as_retriever(search_kwargs = {"k": 2})
#k = how many documents to retrieve

##### DECISION PART
def decide(state: AgentState) -> AgentState:
    needs_retrieval = False
    question = state["question"]
    response = llm.invoke(f"Do you need documents to answer this question? Answer with Y/N Question: {question}")
    if "y" in response.content.lower():
        needs_retrieval = True
    else:
        needs_retrieval = False
    
    return{**state, "is_retrieval": needs_retrieval}
   #Bad way below, 
   # keywords = ["what", "how", "explain", "describe"] #See if prompt has these
   # needs_retrieval = False
   # for keyword in keywords:
   #     if keyword in state["question"].lower():
    #        needs_retrieval = True
    #        break
        
def retrieve(state: AgentState)-> AgentState:
    question = state["question"]
    rtrv = retriever.invoke(question)
    return {**state, "documents": rtrv}        

def generate(state: AgentState)-> AgentState:
    question = state["question"]
    documents = state["documents"]
    
    #we have list of documents right now, we need all of them in one string
    context = ""
    for doc in documents:
        context = context + doc.page_content + "\n\n"
    
    prompt = f""" Use these following documents to answer the question provided,
    Documents: {context} and you have the question, {question} use these to answer, Answer:
    """
    response = llm.invoke(prompt)
    
    return {**state, "answer": response.content}

def should_retrieve(state: AgentState) -> str:
    needs_retrieval = state["is_retrieval"]
    if needs_retrieval == True:
        return "retrieve"
    else:
        return "generate"

workflow = StateGraph(AgentState)
workflow.add_node("decide", decide)
workflow.add_node("retrieve", retrieve)
workflow.add_node("generate", generate)
workflow.set_entry_point("decide")

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

result = app.invoke(
    {
        "question": "What is RAG?",
        "documents": [],
        "answer": "",
        "is_retrieval": False
    }
)

print(result["answer"])