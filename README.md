# Paper Navigator 📚 - Your AI Research Assistant

Paper Navigator is a Q&A (Question & Answering) system built on the RAG (Retrieval-Augmented Generation) architecture. It allows users to ask questions in natural language and receive accurate answers from the content of a collection of scientific papers (in PDF format).

This project runs 100% locally on your personal computer, with no need for paid APIs, ensuring privacy and accessibility.

---

### ✨ Key Features

-   **Synthesized & Intelligent Answers:** The chatbot doesn't just extract information; it synthesizes knowledge from multiple sources within the documents to provide comprehensive answers.
-   **Contextual Enhancement:** Utilizes advanced retrieval strategies to provide the LLM with a broader context of the query.
-   **100% Local:** Uses Ollama to run the large language model right on your machine.
-   **Interactive Interface:** A user-friendly chatbot interface that allows file uploads, data management, and clearing chat history.

---

### 🛠️ Tech Stack

| Component         | Technology                              |
| ----------------- | --------------------------------------- |
| **Framework**     | LlamaIndex                              |
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
    ├── data_processing.py
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
| `src/data_processing.py` | Responsible for loading and processing documents from the `documents` folder. |
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
    The first time you process documents, the system will need some time to build the vector database. Subsequently, you can continue to upload more documents to expand the system's knowledge base.

---

### 🔮 Future Development

Here are some potential features to improve and expand the project:

-   [ ] **Support for Multiple Formats:** Extend processing capabilities to include `.docx` and `.txt` files.
-   [ ] **Save Chat History:** Persist conversations so users can review them later.
-   [ ] **Source Citations:** Display the source (document name and page number) from which the answer was derived.

---

### 📄 License

This project is licensed under the **MIT License**. See the `LICENSE` file for more details.

---

### 🙏 Acknowledgements

This project would not have been possible without the amazing open-source tools from the community:
-   [LlamaIndex](https://www.llamaindex.ai/)
-   [Ollama](https://ollama.com/)
-   [ChromaDB](https://www.trychroma.com/)
-   [Streamlit](https://streamlit.io/)
