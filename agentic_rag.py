from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


import os
from dotenv import load_dotenv
load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(model = "gpt-4o", temperature = 0)
embeddings = OpenAIEmbeddings()

class AgentState(TypedDict):
    question: str
    documents: List[Document]
    answer: str
    needs_retrieval: bool
    
sample_texts = [
    "LangGraph is a library for building stateful, multi-factor applications with LLMS. It extends LangChain",
    "RAG (Retrieval Augmented Generation) is a technique that combines information retreival with text and utilization of vector DB to store vectors from different file formats",
    "Vector Databases store high - dimensional vectors and enable efficient similarity search. They are highly used with RAG",
    "Agentic systems are AI systems that can take actions, make decisions, and interact bwith their environment depending on what is happening"
]
###Sample Document and VcctorStore

documents = [Document(page_content=text) for text in sample_texts]

##Create vector store

vectorstore = FAISS.from_documents(documents,embeddings)
retriever = vectorstore.as_retriever(k=3)

def decide_retrieval(state: AgentState) -> AgentState:
    ##Decide if we need to retrieve documents based on the question
    question = state["question"]
    
    # Simple Heuristic: If question contains certain keywords, retrieve
    retrievel_keywords = ["what", "how", "explain", "describe", "tell me"]
    needs_retrieval = any(keyword in question.lower() for keyword in retrievel_keywords)
    
    return {**state, "needs_retrieval": needs_retrieval}

def retrieve_documents(state: AgentState) -> AgentState:
#Retrieve relevant documents based on the question

    question = state["question"]
    documents = retriever.invoke(question)
    
    return {**state, "documents": documents}

def generate_answer(state: AgentState) -> AgentState:
    question = state["question"]
    documents = state.get("documents", [])
    
    if documents:
        #RAG approach: use documents as context
        context = "\n\n".join([doc.page_content for doc in documents])
        prompt = f"""Based on the following content, answer the question:

Content:
{context}

Question: {question}

Answer:"""
    else:
        #Direct response without retrieval
        prompt = f"Answer the following question: {question}"
    
    response = llm.invoke(prompt)
    answer = response.content
    
    return {**state, "answer": answer}


def should_retrieve(state: AgentState) -> str:
    """
    Determine the next step based on retrieval decision
    """
    
    if state["needs_retrieval"]:
        return "retrieve"
    else:
        return "generate"

workflow = StateGraph(AgentState)

#Add Nodes
workflow.add_node("decide", decide_retrieval)
workflow.add_node("retrieve", retrieve_documents)
workflow.add_node("generate", generate_answer)

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
app

def ask_question(question: str):
    #Helper function to ask a question and get an answer
    
    initial_state = {
        "question": question,
        "documents": [],
        "answer": "",
        "needs_retrieval": False
    }
    
    result = app.invoke(initial_state)
    return result

question1 = "What is LangGraph?"
result1 = ask_question(question1)
print(result1["answer"])