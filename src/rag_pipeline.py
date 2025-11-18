# src/rag_pipeline.py

import chromadb
from chromadb.config import Settings as ChromaSettings
from llama_index.core import VectorStoreIndex, StorageContext, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.llms.ollama import Ollama
from llama_index.core.embeddings import resolve_embed_model
from src.config import LLM_MODEL, EMBEDDING_MODEL, VECTOR_DB_PATH, DOCUMENTS_PATH
from src.prompts import QA_TEMPLATE
from src.data_processing import load_documents
import os
import shutil

class RAGPipeline:
    def __init__(self):
        """Initializes the RAG pipeline components."""
        self.llm = Ollama(model=LLM_MODEL, request_timeout=120.0)
        self.embed_model = resolve_embed_model(f"local:{EMBEDDING_MODEL}")
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model
        self.index = None
        self.db_client = None

    def _get_db_client(self):
        """Creates or returns the database connection. Ensures only one connection exists."""
        if self.db_client is None:
            print("Creating new ChromaDB client...")
            self.db_client = chromadb.PersistentClient(path=VECTOR_DB_PATH, settings=ChromaSettings(allow_reset=True))
        return self.db_client

    def build_index(self):
        """Builds and persists the index from documents."""
        print("Building a new index with advanced chunking...")
        try:
            documents = load_documents()
        except FileNotFoundError:
            # If no files, do nothing and return False
            return False
            
        node_parser = SentenceSplitter(chunk_size=1024, chunk_overlap=20)

        # Create ChromaDB client
        client = self._get_db_client()
        chroma_collection = client.get_or_create_collection("paper_navigator")
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # Create index from documents
        self.index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            transformations = [node_parser],
            show_progress=True
        )
        print("Index built and persisted successfully.")
        return True

    def load_index(self):
        """Loads an existing index from storage."""
        if not os.path.exists(os.path.join(VECTOR_DB_PATH, "chroma.sqlite3")):
            return False

        print("Loading existing index from storage...")
        client = self._get_db_client()
        chroma_collection = client.get_or_create_collection("paper_navigator")
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        self.index = VectorStoreIndex.from_vector_store(vector_store)
        print("Index loaded successfully.")
        return True

    def get_query_engine(self):
        """Returns a query engine for the index. Initializes index if not loaded."""
        if self.index is None:
            # If loading fails (no index), try building a new one
            if not self.load_index():
                self.build_index()

        # If after both attempts there is still no index (due to no documents)
        if self.index is None:
            return None
        
        print("Creating query engine with custom prompt...")
        return self.index.as_query_engine(
            streaming=True,
            text_qa_template=QA_TEMPLATE,
            similarity_top_k=5
        )
    
    def reset_index(self):
        """Force rebuilds the index (Used when new files are uploaded)."""
        # Clear index from memory
        self.index = None
        client = self._get_db_client()
        try:
            # Delete existing collection from ChromaDB
            client.delete_collection(name="paper_navigator")
            print("Successfully deleted old collection from ChromaDB.")
        except Exception as e:
            # Ignore error if collection does not exist
            print(f"Could not delete collection (it might not exist): {e}")

        # Rebuild from scratch
        self.build_index()

    def clear_workspace(self):
        """Deletes all documents and the vector database, then resets the index."""
        print("Clearing workspace...")
        self.index = None

        client = self._get_db_client()
        client.reset()
        print("ChromaDB has been reset via API.")

        self.db_client = None
        
        if os.path.exists(DOCUMENTS_PATH):
            for filename in os.listdir(DOCUMENTS_PATH):
                if filename == '.gitkeep': continue
                file_path = os.path.join(DOCUMENTS_PATH, filename)
                if os.path.isfile(file_path): os.unlink(file_path)
        print("Documents folder cleared.")
        
        print("Workspace cleared.")