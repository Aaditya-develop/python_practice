from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from vectorstore import VectorStore

def ingest_pdf(pdf_path: str):
    loader = PyPDFLoader(pdf_path)
    #Just like how we used retriever.invoke() to search, 
    # loader.load() reads the PDF and returns a list of 
    # Document objects — one per page.
    documents = loader.load()
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 50
    )
    #Takes each page and splits it into smaller pieces. Why?
    #Because one page might be 3000 characters. 
    # That's too big to embed meaningfully. 
    # Smaller chunks = more precise search results.
    chunks = splitter.split_documents(documents)
    
    vs = VectorStore()
    vs.add_documents(chunks)
    print(f" Saved {len(chunks)} chunks to ChromaDB")
    
if __name__ == "__main__":
    ingest_pdf("attention.pdf")