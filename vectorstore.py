from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from typing import List
from dotenv import load_dotenv
import os

load_dotenv()

class VectorStore:
    #Constructor
    def __init__(self, collection_name: str = "documents", persist_directory: str = "./data/vector_store"):
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings(model = "text-embedding-3-small")
        self.vectorstore = Chroma(
            collection_name = self.collection_name,
            embedding_function = self.embeddings,
            persist_directory = self.persist_directory
        )
        
    def add_documents(self, documents: List[Document]):
        self.vectorstore.add_documents(documents)
    
    def search(self, query: str, k: int = 2) -> List[Document]:        
        return self.vectorstore.similarity_search(query, k = k)

    