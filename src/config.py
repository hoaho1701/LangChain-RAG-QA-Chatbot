# src/config.py

import os

# Avoid the HuggingFace tokenizers fork warning when this module is imported outside the entrypoints
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

# Ollama LLM model name
LLM_MODEL = "qwen3.5:9b"

# Ollama model that grades evaluation answers; keep it a different family than LLM_MODEL.
# Empty = the answering model grades itself.
JUDGE_MODEL = os.environ.get("JUDGE_MODEL", "gemma4:12b")

# Ollama server URL. Empty = ollama client default (localhost:11434, or OLLAMA_HOST).
# In Docker, point this at the host: http://host.docker.internal:11434
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "")

# Load HF models from the local cache only (no network). Set HF_LOCAL_FILES_ONLY=false
# to let the first run download them (e.g. into the Docker HF cache volume).
HF_LOCAL_FILES_ONLY = os.environ.get("HF_LOCAL_FILES_ONLY", "true").lower() != "false"

# HuggingFace embedding model name
EMBEDDING_MODEL = "BAAI/bge-m3"

# Everything the app writes (uploaded files, vector database, MLflow runs) lives in data/
# Path to the directory containing documents
DOCUMENTS_PATH = os.environ.get("DOCUMENTS_PATH", "./data/documents")

# Path to the directory for the vector database
VECTOR_DB_PATH = os.environ.get("VECTOR_DB_PATH", "./data/vector_db")

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Max number of messages (human + AI pairs) to keep in conversation history
MAX_CHAT_HISTORY_MESSAGES = 20

# Max times the agent may rewrite query and retry retrieval before giving up
MAX_REWRITE_ATTEMPTS = 1

# Reranker model name
RERANKER_MODEL = "BAAI/bge-reranker-v2-m3"

# Number of candidates retrieved before reranking (wider net)
RETRIEVER_TOP_K = 20

# Number of docs to keep after reranking (fed to LLM)
RERANKER_TOP_N = 5
