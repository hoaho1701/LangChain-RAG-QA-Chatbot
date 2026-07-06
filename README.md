# LangChain-RAG-QA-Chatbot

A local, privacy-first RAG (Retrieval-Augmented Generation) chatbot. Upload documents, ask questions in natural language, get answers grounded in your own files — with source citations, conversation memory, and a self-correcting **agentic retrieval loop**.

Powered by LangChain (Core/LCEL), LangGraph, and Ollama, this project runs **100% locally**: no API keys required, no data leaves your machine, no usage costs.

---

### ✨ Key Features

- **Agentic RAG (Corrective RAG):** A LangGraph state machine that grades retrieved documents for relevance and automatically rewrites the query and retries when nothing relevant is found.
- **Two-Stage Retrieval:** Bi-encoder similarity search (top-20 candidates) followed by cross-encoder reranking (top-5) for higher-precision context.
- **Conversation Memory:** Follow-up questions ("What about that?") are rewritten into standalone questions using chat history before retrieval.
- **Source Citations:** Every answer links back to the exact file and page it was derived from.
- **Multi-Format Ingestion:** PDF, TXT, Markdown, DOCX, and direct URL scraping — all through one dispatcher.
- **Multi-File Management:** Additive indexing — add or remove individual files without rebuilding the whole vector database.
- **Streaming Responses:** Answers are streamed token-by-token for a responsive, ChatGPT-like UX.
- **LangSmith Tracing (optional):** Full pipeline observability with zero code changes — just set environment variables.
- **Evaluation Harness:** Retrieval metrics (Recall@k, MRR) and LLM-as-judge generation metrics (Correctness, Faithfulness), with a per-language breakdown to catch regressions instead of guessing.

---

### 🛠️ Tech Stack

| Component            | Technology                                  |
| --------------------- | -------------------------------------------- |
| **Orchestration**     | LangChain Core (LCEL) + LangGraph            |
| **LLM**               | Ollama (`qwen2.5:7b-instruct`)                |
| **Embedding Model**   | HuggingFace (`BAAI/bge-m3`)                   |
| **Reranker**          | Cross-Encoder (`BAAI/bge-reranker-v2-m3`)     |
| **Vector Database**   | ChromaDB (persistent, local)                  |
| **Interface**         | Streamlit                                     |
| **Tracing (optional)**| LangSmith                                     |
| **Language**          | Python 3.10+                                  |

---

### 🧠 How It Works

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
├── app.py                  # Streamlit UI
├── evaluate.py              # CLI: run the evaluation harness
├── src/
│   ├── config.py            # Constants + env vars
│   ├── prompts.py            # All ChatPromptTemplate definitions
│   ├── rag_pipeline.py       # RAGPipeline: ingestion, retrieval, agentic graph
│   └── evaluation.py         # Retrieval + generation evaluation metrics
├── eval/
│   └── dataset.json          # Q&A ground truth used by evaluate.py
├── documents/               # Uploaded source files (gitignored)
├── vector_db/               # ChromaDB persistent storage (gitignored)
├── .env.example             # Template for optional LangSmith tracing keys
├── requirements.txt
└── LICENSE
```

| File / Directory       | Description                                                          |
| ----------------------- | --------------------------------------------------------------------- |
| `app.py`                | Streamlit entry point — upload UI, chat UI, sidebar file management.  |
| `evaluate.py`           | CLI to run the evaluation harness and print/save a report.            |
| `src/config.py`         | Model names, chunking, retrieval/reranking parameters.                |
| `src/prompts.py`        | Prompt templates: contextualize, QA, document grading, query rewrite, evaluation judges. |
| `src/rag_pipeline.py`   | Ingestion (PDF/TXT/DOCX/URL), chunking, embeddings, ChromaDB, reranker, and the LangGraph agentic loop. |
| `src/evaluation.py`     | Recall@k/MRR (retrieval) and LLM-as-judge Correctness/Faithfulness (generation). |
| `eval/dataset.json`     | Hand-written Q&A ground truth, tagged by language, used to run `evaluate.py`. |

---

### 🚀 Installation and Setup

**Prerequisites:**
- Python 3.10+
- [Ollama](https://ollama.com/) installed and running

**Steps:**

1. **Install Ollama and pull the model:**
   ```bash
   ollama pull qwen2.5:7b-instruct
   ```

2. **Clone this repository:**
   ```bash
   git clone https://github.com/hoaho1701/LangChain-RAG-QA-Chatbot
   cd LangChain-RAG-QA-Chatbot
   ```

3. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install the required libraries:**
   ```bash
   pip install -r requirements.txt
   ```

5. **(Optional) Enable LangSmith tracing:**
   ```bash
   cp .env.example .env
   # then fill in your LANGCHAIN_API_KEY
   ```

6. **Run the application:**
   ```bash
   streamlit run app.py
   ```

---

### 📖 How to Use

1. **Add content:** Upload PDF/TXT/MD/DOCX files, or paste a URL, from the sidebar and click **"Process Documents"** / **"Add URL"**.
2. **Chat:** Ask a question in the chat box (e.g., *"Summarize the main methodology"*). Follow-up questions are understood in context.
3. **Check sources:** Expand **"Sources"** under any answer to see the exact file and page it came from.
4. **Manage files:** Remove individual indexed files from the sidebar without affecting the rest of the database.
5. **Reset:**
   - **Clear Chat History** — wipes the conversation only.
   - **Clear Workspace** — deletes all uploaded files and the vector database (requires confirmation).

---

### 📊 Evaluating the Pipeline

```bash
python evaluate.py                          # uses eval/dataset.json by default
python evaluate.py --dataset eval/other.json --report eval/other_report.md
```

Runs every question in the dataset through the retriever+reranker (Recall@k, MRR) and the full
agentic `chat()` pipeline (LLM-as-judge Correctness, Faithfulness), then prints a Markdown report
— including a breakdown by language — and saves it to `eval/last_report.md`.

See [`eval/Report.md`](eval/Report.md) for a committed snapshot of a real run.

---

### 🔮 Future Development

- [ ] **Multi-Modal:** Support asking questions about images/figures inside PDFs.
- [ ] **Persistent Chat History:** Save conversations across app restarts (currently in-memory per session).
- [ ] **Docker Support:** One-command containerized setup for Ollama + app.

---

### 📄 License

This project is licensed under the **MIT License**. See the `LICENSE` file for more details.

---

### 🙏 Acknowledgements

This project would not have been possible without the amazing open-source tools from the community:
- [LangChain](https://www.langchain.com/) & [LangGraph](https://www.langchain.com/langgraph)
- [Ollama](https://ollama.com/)
- [ChromaDB](https://www.trychroma.com/)
- [Streamlit](https://streamlit.io/)
