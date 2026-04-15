import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# AI Imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS  # Using FAISS for perfect Windows stability
from flashrank import Ranker, RerankRequest

# --- DATABASE SETUP ---
DB_URL = "sqlite:///./finance_system.db"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    hashed_password = Column(String)
    role = Column(String) 

class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    company_name = Column(String)
    doc_type = Column(String)
    uploaded_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# --- RAG PIPELINE ---
class FinancialRAG:
    def __init__(self):
        # 1. Initialize Embeddings
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # 2. Setup Reranker and Text Splitter
        self.ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2")
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=100)
        
        # 3. Vector store initialized as None
        self.vector_store = None

    def process_document(self, content: str, doc_id: int, title: str):
        """Indexes documents using FAISS"""
        chunks = self.text_splitter.split_text(content)
        metadatas = [{"doc_id": doc_id, "title": title} for _ in chunks]
        
        if self.vector_store is None:
            self.vector_store = FAISS.from_texts(chunks, self.embeddings, metadatas=metadatas)
        else:
            self.vector_store.add_texts(chunks, metadatas=metadatas)

    def search_with_reranking(self, query: str):
        """Perform semantic search + FlashRank reranking with JSON-safe scores"""
        if self.vector_store is None:
            return []

        # 1. Retrieve Top 20 (Retrieval Stage)
        initial_docs = self.vector_store.similarity_search(query, k=20)
        
        # 2. Format for Reranker
        passages = [
            {"id": i, "text": d.page_content, "meta": d.metadata} 
            for i, d in enumerate(initial_docs)
        ]
        
        # 3. Rerank (Relevance Stage)
        rerank_req = RerankRequest(query=query, passages=passages)
        results = self.ranker.rerank(rerank_req)
        
        # 4. FIX: Convert numpy.float32 to standard Python float for JSON serialization
        final_results = []
        for res in results[:5]:
            res['score'] = float(res['score']) # This line fixes the 500 error
            final_results.append(res)
            
        return final_results

rag_engine = FinancialRAG()