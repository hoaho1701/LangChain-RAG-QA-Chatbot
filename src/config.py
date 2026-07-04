# src/config.py

import os

# Prevent transformers from auto-loading TensorFlow/JAX — causes C++ mutex deadlock on macOS
# (TF is installed in this conda env but not needed; its C++ runtime conflicts with PyTorch)
os.environ.setdefault("USE_TF", "0")
os.environ.setdefault("USE_JAX", "0")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

# Ollama LLM model name
LLM_MODEL = "qwen2.5:7b-instruct"

# HuggingFace embedding model name
EMBEDDING_MODEL = "BAAI/bge-m3"

# Path to the directory containing documents
DOCUMENTS_PATH = "./documents"

# Path to the directory for the vector database
VECTOR_DB_PATH = "./vector_db"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Max number of messages (human + AI pairs) to keep in conversation history
MAX_CHAT_HISTORY_MESSAGES = 20

# Max times the agent may rewrite query and retry retrieval before giving up
MAX_REWRITE_ATTEMPTS = 2

# Reranker model name
RERANKER_MODEL = "BAAI/bge-reranker-v2-m3"

# Number of candidates retrieved before reranking (wider net)
RETRIEVER_TOP_K = 20

# Number of docs to keep after reranking (fed to LLM)
RERANKER_TOP_N = 5