import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

CHROMA_DB_DIR = "./chroma_db"
embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

vector_db = Chroma(persist_directory=CHROMA_DB_DIR, embedding_function=embeddings_model)

def index_document(file_path: str, document_id: int):
    # Load document
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    
    # Chunking
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(pages)

    # Add metadata
    for chunk in chunks:
        chunk.metadata["document_id"] = document_id
        
    vector_db.add_documents(chunks)
    vector_db.persist()

def remove_document(document_id: int):
    # Retrieve points with document_id and delete
    # Chroma DB allows deleting by filter
    try:
        # Depending on Chromadb version it might be a bit different, but this usually works
        vector_db._collection.delete(where={"document_id": document_id})
        vector_db.persist()
    except Exception as e:
        print(f"Error removing document {document_id} from vector_db: {e}")

def search_documents(query: str):
    # Basic search
    results = vector_db.similarity_search(query, k=20)
    return results

def rerank_results(query: str, results: list):
    # Cross encoder rating
    try:
        from sentence_transformers import CrossEncoder
        cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        pairs = [[query, doc.page_content] for doc in results]
        scores = cross_encoder.predict(pairs)
        # sort based on scores
        scored_results = sorted(zip(scores, results), key=lambda x: x[0], reverse=True)
        return [res[1] for res in scored_results[:5]]
    except Exception as e:
        print(f"Reranking error: {e}")
        # Fallback to top 5 from similarity search 
        return results[:5]
