# LangChain-RAG-QA-Chatbot

A local, privacy-first RAG (Retrieval-Augmented Generation) chatbot. Upload documents, ask questions in natural language, get answers grounded in your own files — with source citations, conversation memory, and a self-correcting **agentic retrieval loop**.

Powered by LangChain (Core/LCEL), LangGraph, and Ollama, with a FastAPI backend and a React frontend, this project runs **100% locally**: no API keys required, no data leaves your machine, no usage costs.

![RAG QA Chatbot UI](docs/ui.png)

---

### ✨ Key Features

- **Agentic RAG (Corrective RAG):** A LangGraph state machine that grades retrieved documents for relevance and automatically rewrites the query and retries when nothing relevant is found.
- **Two-Stage Retrieval:** Bi-encoder similarity search (top-20 candidates) followed by cross-encoder reranking (top-5) for higher-precision context.
- **Conversation Memory:** Follow-up questions ("What about that?") are rewritten into standalone questions using chat history before retrieval.
- **Source Citations:** Every answer links back to the exact file and page it was derived from.
- **Multi-Format Ingestion:** PDF, TXT, Markdown, DOCX, and direct URL scraping — all through one dispatcher.
- **Multi-File Management:** Additive indexing — add or remove individual files without rebuilding the whole vector database.
- **Streaming Responses:** The API streams answers token-by-token over Server-Sent Events, and the React UI renders them as Markdown.
- **Evaluation Harness:** Retrieval metrics (Recall@k, MRR) and LLM-as-judge generation metrics (Correctness, Faithfulness), with a per-language breakdown. Runs can be logged to MLflow to compare configurations.
- **CI/CD:** GitHub Actions lints and tests the backend, lints and builds the frontend, and publishes Docker images to GHCR from `main`.

---

### 🛠️ Tech Stack

| Component            | Technology                                  |
| --------------------- | -------------------------------------------- |
| **Orchestration**     | LangChain Core (LCEL) + LangGraph            |
| **LLM**               | Ollama (`qwen2.5:7b-instruct`)                |
| **Embedding Model**   | HuggingFace (`BAAI/bge-m3`)                   |
| **Reranker**          | Cross-Encoder (`BAAI/bge-reranker-v2-m3`)     |
| **Vector Database**   | ChromaDB (persistent, local)                  |
| **Backend**           | FastAPI + Server-Sent Events                  |
| **Frontend**          | React 19 + Vite, served by nginx              |
| **Experiment Tracking** | MLflow                                      |
| **Packaging / CI**    | uv, Docker Compose, GitHub Actions            |
| **Language**          | Python 3.10, JavaScript                       |

---

### 🧠 How It Works

```
React (Vite / nginx) ──/api──▶ FastAPI ──▶ RAGPipeline
                                  │           ├─ Ollama (runs on the host)
                                  │           └─ ChromaDB (vector_db/)
evaluate.py ──▶ MLflow server
```

```
User question
    │
    ▼
[LangGraph agentic loop]
    ├── retrieve  → contextualize (if chat history) → top-20 → rerank → top-5
    ├── grade     → LLM checks which docs are actually relevant
    └── decide    ├── relevant docs found        → generate answer
                  └── none found (retry < 2)      → rewrite query → retrieve again
    ▼
Answer streamed token-by-token, with source citations (file + page)
```

---

### 📂 Project Structure

```
LangChain-RAG-QA-Chatbot/
├── api/
│   ├── main.py              # FastAPI app: documents, chat (SSE), health
│   └── schemas.py           # Request models
├── frontend/                # React + Vite app (Dockerfile + nginx.conf included)
├── src/
│   ├── config.py            # Constants + env vars
│   ├── prompts.py           # All ChatPromptTemplate definitions
│   ├── rag_pipeline.py      # RAGPipeline: ingestion, retrieval, agentic graph
│   ├── evaluation.py        # Retrieval + generation evaluation metrics
│   └── tracking.py          # Logs an evaluation run to MLflow
├── tests/                   # API tests (fake pipeline) + MLflow logging tests
├── eval/
│   ├── dataset.json         # Q&A ground truth used by evaluate.py
│   └── Report.md            # Committed snapshot of a real evaluation run
├── evaluate.py              # CLI: run the evaluation harness
├── Dockerfile.api           # Backend image
├── docker-compose.yml       # api + web + mlflow
├── .github/workflows/ci.yml # Lint, test, build, publish
├── documents/               # Uploaded source files (gitignored)
├── vector_db/               # ChromaDB persistent storage (gitignored)
├── pyproject.toml           # Dependencies (uv)
├── uv.lock                  # Locked versions
└── LICENSE
```

---

### 🚀 Installation and Setup

**Prerequisites:**
- [Ollama](https://ollama.com/) installed and running
- [uv](https://docs.astral.sh/uv/) (installs Python 3.10 for you)
- Node.js 22+ (only for the dev setup)
- Docker Desktop (only for the Docker setup)

**1. Pull the LLM and clone the repository**
```bash
ollama pull qwen2.5:7b-instruct
git clone https://github.com/hoaho1701/LangChain-RAG-QA-Chatbot
cd LangChain-RAG-QA-Chatbot
```

**2a. Run for development** (two terminals)
```bash
uv sync                                   # creates .venv from uv.lock

# Terminal 1 — backend. The first start downloads the embedding and reranker
# models (a few GB); later starts can run offline (HF_LOCAL_FILES_ONLY defaults to true).
HF_LOCAL_FILES_ONLY=false uv run uvicorn api.main:app --port 8000

# Terminal 2 — frontend (proxies /api to port 8000)
cd frontend && npm ci && npm run dev      # http://localhost:5173
```

**2b. Run with Docker Compose**
```bash
docker compose up --build
```
- App: http://localhost:8080
- MLflow: http://localhost:5001

Ollama keeps running on the host, and the containers reach it through `host.docker.internal`. The compose file mounts `~/.cache/huggingface`, so the models must already be in that cache (run the backend once as in 2a first).

---

### 📖 How to Use

1. **Add content:** Choose PDF/TXT/MD/DOCX files and click **"Process Documents"**, or paste a URL and click **"Add URL"**.
2. **Chat:** Ask a question in the chat box (Enter sends, Shift+Enter adds a new line). Follow-up questions are understood in context.
3. **Check sources:** Expand **"Sources"** under any answer to see the exact file and page it came from.
4. **Manage files:** Remove individual indexed files with ✕ in the sidebar without affecting the rest of the database.
5. **Reset:**
   - **Clear Chat History** — wipes the conversation only.
   - **Clear Workspace** — deletes all uploaded files and the vector database (requires confirmation).

Adding or removing documents starts a fresh conversation for the model; earlier messages stay on screen.

---

### 📊 Evaluating the Pipeline

```bash
uv run python evaluate.py                          # uses eval/dataset.json by default
uv run python evaluate.py --dataset eval/other.json --report eval/other_report.md
uv run python evaluate.py --mlflow                 # also log the run to MLflow
```

Runs every question in the dataset through the retriever+reranker (Recall@k, MRR) and the full
agentic `chat()` pipeline (LLM-as-judge Correctness, Faithfulness), then prints a Markdown report
— including a breakdown by language — and saves it to `eval/last_report.md`.

With `--mlflow`, set `MLFLOW_TRACKING_URI` to the server (for example `http://localhost:5001` when the compose stack is up); without it the run is written to `./mlruns`.

The dataset assumes the first 40 pages of two books are indexed, so run it against that index.
See [`eval/Report.md`](eval/Report.md) for a committed snapshot of a real run
(Recall@5 95%, MRR 0.90, Correctness 80%, Faithfulness 85%).

---

### 🧪 Tests and CI

```bash
uv run pytest -q          # API tests run with a fake pipeline: no Ollama or models needed
uv run ruff check . && uv run ruff format --check .
```

On every pull request GitHub Actions runs the backend lint and tests, the frontend lint, format check and build, and a trial build of both Docker images. Pushes to `main` also publish the images to GitHub Container Registry.

---

### 🔮 Future Development

- [ ] **Multi-Modal:** Support asking questions about images/figures inside PDFs.
- [ ] **Persistent Chat History:** Keep conversations across page reloads.
- [ ] **Answer language:** Reply in the language of the question, and measure it with out-of-document questions in the evaluation set.

---

### 📄 License

This project is licensed under the **MIT License**. See the `LICENSE` file for more details.

---

### 🙏 Acknowledgements

This project would not have been possible without the amazing open-source tools from the community:
- [LangChain](https://www.langchain.com/) & [LangGraph](https://www.langchain.com/langgraph)
- [Ollama](https://ollama.com/)
- [ChromaDB](https://www.trychroma.com/)
- [FastAPI](https://fastapi.tiangolo.com/) & [React](https://react.dev/)
- [MLflow](https://mlflow.org/)
