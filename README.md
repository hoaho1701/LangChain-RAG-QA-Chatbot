# RAG Research Assistant -  AI Research Assistant

Paper Navigator is a Q&A (Question & Answering) system built on the RAG (Retrieval-Augmented Generation) architecture. It allows users to ask questions in natural language and receive accurate answers from the content of a collection of scientific papers (in PDF format).

Powered by LangChain and Ollama, this project runs 100% locally on your machine, ensuring complete data privacy with no API costs.

---

### ✨ Key Features

-   **LangChain Powered:** Utilizes the flexible LCEL (LangChain Expression Language) architecture for a robust RAG pipeline.
-   **100% Local & Private:** Runs entirely on your hardware using Ollama (Llama 3) and local embeddings.
-   **Smart Processing:** Explicit two-step document processing:
    1.  **Load & Split:** Efficiently chunks PDF documents.
    2.  **Embed & Store:** Vectorizes data into a persistent ChromaDB.
-   **Safe Memory Management:** Optimized to handle database locking issues (using Garbage Collection & ChromaDB Reset API).
-   **User-Friendly Interface:** Clean Streamlit UI with chat history management and safe workspace clearing.

---

### 🛠️ Tech Stack

| Component         | Technology                              |
| ----------------- | --------------------------------------- |
| **Framework**     | LangChain (Community & Core)                           |
| **LLM**           | Ollama (Model: `llama3:8b`)             |
| **Embedding Model** | Hugging Face (`BAAI/bge-small-en-v1.5`) |
| **Vector Database** | ChromaDB (Local)                        |
| **Interface**     | Streamlit                               |
| **Language**      | Python 3.10+                            |

---

### 📂 Project Structure

The project is organized in a modular structure for easy management and scalability:

```
RAG-based-AI-Paper-Analyzer/
├── documents/
└── src/
    ├── config.py
    └── prompts.py
    └── rag_pipeline.py
├── vector_db/
├── .gitignore
├── app.py
├── LICENSE
├── README.md
├── requirements.txt
```

**Explanation of Key Components:**

| Directory / File    | Description                                                         |
| ------------------- | ------------------------------------------------------------------- |
| `documents/`        | Stores the scientific paper PDF files as input data.                |
| `src/`              | Contains all the core logic and source code of the application.     |
| `src/config.py`     | Defines constants and configurations like model names, file paths.  |
| `src/prompts.py`    | Defines custom prompt templates to guide the LLM for better responses. |
| `src/rag_pipeline.py` | The brain of the application, connecting all components to create the RAG pipeline. |
| `vector_db/`        | Stores the vector database generated from the documents.            |
| `app.py`            | The main file to launch the user interface with Streamlit.          |
| `LICENSE`           | The open-source license for the project (MIT License).              |
| `README.md`         | The documentation and introduction to the project.                  |
| `requirements.txt`  | A list of the necessary Python libraries to run the project.        |

---

### 🚀 Installation and Setup

**Prerequisites:**
-   Python 3.10+
-   [Ollama](https://ollama.com/) installed and running.

**Steps:**

1.  **Install Ollama and pull the model:**
    ```bash
    # After installing Ollama, run this command in your terminal
    ollama pull llama3:8b
    ```

2.  **Clone this repository:**
    ```bash
    git clone https://github.com/your-github-username/RAG-based-AI-Paper-Analyzer.git
    cd RAG-based-AI-Paper-Analyzer
    ```

3.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

4.  **Install the required libraries:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Run the application:**
    ```bash
    streamlit run app.py
    ```

---

### 📖 How to Use

1.  **Upload:** Open the sidebar, upload your PDF files, and click **"Process Documents"**.
2.  **Wait:** The system will load, split, and embed your documents. Watch the spinner!
3.  **Chat:** Once finished, type your question in the chat box (e.g., *"Summarize the main methodology"*).
4.  **Manage:**
    -   **Clear Chat History:** Wipes the conversation screen.
    -   **Clear Workspace:** Completely deletes the database and files (requires confirmation).

---

### 🔮 Future Development

Here are some potential features to improve and expand the project:

-   [ ] **Multi-Modal:** Support asking questions about images inside PDFs.
-   [ ] **Save Chat History:** Persist conversations so users can review them later.
-   [ ] **Source Citations:** Display the source (document name and page number) from which the answer was derived.

---

### 📄 License

This project is licensed under the **MIT License**. See the `LICENSE` file for more details.

---

### 🙏 Acknowledgements

This project would not have been possible without the amazing open-source tools from the community:
-   [LangChain](https://www.langchain.com/)
-   [Ollama](https://ollama.com/)
-   [Streamlit](https://streamlit.io/)
