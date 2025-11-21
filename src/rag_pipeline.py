# src/rag_pipeline.py

import os
import shutil
import gc
from typing import List, Generator
import chromadb
from chromadb.config import Settings

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from src.config import (LLM_MODEL, EMBEDDING_MODEL, DOCUMENTS_PATH,
                        VECTOR_DB_PATH, CHUNK_SIZE, CHUNK_OVERLAP)
from src.prompts import QA_TEMPLATE

class RAGPipeline:
    def __init__(self):
        """Initialize the RAG pipeline components."""

        # Set up LLM (Ollama)
        print(f"Loading LLM model: {LLM_MODEL}...")
        self.llm = ChatOllama(model=LLM_MODEL, temperature=0, keep_alive="5m")

        # Set up Embeddings
        print(f"Loading Embedding model: {EMBEDDING_MODEL}...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )

        # Setup ChromaDB Client (PERSISTENT)
        print("Initializing ChromaDB Client...")
        self.client = chromadb.PersistentClient(
            path=VECTOR_DB_PATH,
            settings=Settings(allow_reset=True)
        )

        self.vector_store = None
        self.chain = None

    def load_and_split_documents(self) -> List:
        """Load and split documents from the specified path."""
        if not os.path.exists(DOCUMENTS_PATH) or not any(f.endswith('.pdf') for f in os.listdir(DOCUMENTS_PATH)):
            print(f"No PDF documents found in {DOCUMENTS_PATH}. Please add documents and try again.")
            return []
        
        print(f"Loading documents from: {DOCUMENTS_PATH}...")
        loader = PyPDFDirectoryLoader(DOCUMENTS_PATH)
        docs = loader.load()
        print(f"Loaded {len(docs)} documents.")

        print("Splitting documents into chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = CHUNK_SIZE,
            chunk_overlap = CHUNK_OVERLAP,
            add_start_index = True
        )
        splits = text_splitter.split_documents(docs)
        print(f"Created {len(splits)} document chunks.")

        return splits
    
    def embed_and_store_documents(self, splits) -> bool:
        """Embed and store documents in the vector database."""
        if not splits:
            print("No splits to process.")
            return False
        
        print("Resetting database before ingestion...")
        try:
            self.client.reset()
        except Exception as e:
            print(f"Warning during reset: {e}")

        print(f"Embedding {len(splits)} chunks into ChromaDB...")
        self.vector_store = Chroma.from_documents(
            documents = splits,
            embedding = self.embeddings,
            client = self.client,
            collection_name = "paper_navigator_db"
        )
        print("Embedded and stored document chunks in the vector database.")

        self.setup_rag_chain()
        return True
    
    def load_existing_index(self) -> bool:
        """Load existing vector database index if available."""
        try:
            collections = self.client.list_collections()
            if not collections:
                print("No existing collections found in DB.")
                return False
        except Exception:
            return False
        
        print("Loading existing ChromaDB index...")
        self.vector_store = Chroma(
            embedding_function = self.embeddings,
            client = self.client,
            collection_name = "paper_navigator_db"
        )

        self.setup_rag_chain()
        return True
    
    def setup_rag_chain(self):
        """Set up the RAG chain with prompt templates and output parsers."""
        if not self.vector_store:
            raise ValueError("Vector store is not initialized.")
        
        retriever = self.vector_store.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        )
        
        prompt = QA_TEMPLATE

        def format_docs(docs: List) -> str:
            return "\n\n".join([doc.page_content for doc in docs])
        
        self.chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        print("RAG Chain initialized successfully.")

    def chat(self, question: str) -> Generator:
        """Process a user query through the RAG chain."""
        if not self.chain:
            raise ValueError("RAG chain is not initialized.")
        
        return self.chain.stream(question)


    def clear_workspace(self):
        """Clear the entire workspace including documents and vector database."""
        print("Clearing Vector DB...")
        try:
            self.client.reset()
            self.vector_store = None
            self.chain = None
        except Exception as e:
            print(f"Error resetting DB: {e}")

        if os.path.exists(DOCUMENTS_PATH):
            for f in os.listdir(DOCUMENTS_PATH):
                try:
                    os.remove(os.path.join(DOCUMENTS_PATH, f))
                except Exception as e:
                    print(f"Error deleting file {f}: {e}")
        print("Workspace cleared successfully.")