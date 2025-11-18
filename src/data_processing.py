# src/data_processing.py

import os
from llama_index.core import SimpleDirectoryReader
from src.config import DOCUMENTS_PATH

def load_documents():
    """Load documents from the specified directory."""
    
    # Check if the documents directory exists and contains PDF files
    if not os.path.exists(DOCUMENTS_PATH) or not any(f.endswith('.pdf') for f in os.listdir(DOCUMENTS_PATH)):
        # If not, raise an error with a helpful message
        raise FileNotFoundError(
            f"The directory '{DOCUMENTS_PATH}' does not exist or contains no PDF files. "
            "Please create the directory and add PDF documents to it."
        )
        
    print(f"Loading documents from {DOCUMENTS_PATH}")
    reader = SimpleDirectoryReader(DOCUMENTS_PATH)
    documents = reader.load_data()
    print(f"Loaded {len(documents)} document(s).")
    return documents