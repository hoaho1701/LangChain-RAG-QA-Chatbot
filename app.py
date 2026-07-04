# app.py

import os
# Must be set before any ML library is imported
# USE_TF=0 prevents transformers from auto-loading TensorFlow, which causes a
# C++ mutex deadlock on macOS when TF and PyTorch are both installed in the same env.
os.environ["USE_TF"] = "0"
os.environ["USE_JAX"] = "0"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"

from dotenv import load_dotenv
load_dotenv()  # load .env before any LangChain import so tracing vars are set in time

import time
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage

from src.rag_pipeline import RAGPipeline
from src.config import DOCUMENTS_PATH, MAX_CHAT_HISTORY_MESSAGES

# --- App Configuration ---
st.set_page_config(
    page_title="RAG QA Chatbot Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

if not os.path.exists(DOCUMENTS_PATH):
    os.makedirs(DOCUMENTS_PATH)


@st.cache_resource(show_spinner="Loading AI models... (first run may take a moment)")
def get_pipeline() -> RAGPipeline:
    """Load the RAG pipeline once and cache it across all Streamlit sessions."""
    print("Initializing RAG Pipeline...")
    p = RAGPipeline()
    p.load_existing_index()
    return p


# --- State Management ---
pipeline = get_pipeline()

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! Upload a PDF and ask me anything."}]

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Sidebar ---
with st.sidebar:
    st.header("📚 RAG QA Chatbot Assistant")
    st.write("Upload files or paste a URL to start asking questions.")

    uploaded_files = st.file_uploader(
        "Choose files",
        type=["pdf", "txt", "md", "docx"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:
        if st.button("Process Documents", use_container_width=True):
            with st.spinner("Processing documents... Please wait."):
                try:
                    added = 0
                    for uploaded_file in uploaded_files:
                        file_path = os.path.join(DOCUMENTS_PATH, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        splits = pipeline.load_and_split_file(file_path)
                        if splits:
                            pipeline.embed_and_store_documents(splits)
                            added += 1
                    if added:
                        st.session_state.chat_history = []
                        st.toast(f"Added {added} file(s) successfully!", icon="✅")
                    else:
                        st.error("No valid content found in uploaded files.")
                except Exception as e:
                    st.error(f"Error processing documents: {e}")

    st.divider()
    st.subheader("🌐 Add from URL")
    url_input = st.text_input("Paste a URL", placeholder="https://...", label_visibility="collapsed")
    if url_input and st.button("Add URL", use_container_width=True):
        with st.spinner("Fetching URL..."):
            try:
                splits = pipeline.load_and_split_url(url_input)
                if splits:
                    pipeline.embed_and_store_documents(splits)
                    st.session_state.chat_history = []
                    st.toast("URL added successfully!", icon="✅")
                else:
                    st.error("Could not extract content from URL.")
            except Exception as e:
                st.error(f"Error fetching URL: {e}")

    # --- Indexed Files ---
    indexed = pipeline.list_indexed_files()
    if indexed:
        st.divider()
        st.subheader("📂 Indexed Files")
        for filepath in indexed:
            is_url = "://" in filepath
            display = filepath if is_url else os.path.basename(filepath)
            icon = "🌐" if is_url else "📄"
            col1, col2 = st.columns([5, 1])
            with col1:
                st.caption(f"{icon} {display}")
            with col2:
                if st.button("✕", key=f"rm_{filepath}", help=f"Remove {display}"):
                    pipeline.remove_document(filepath)
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    st.session_state.chat_history = []
                    st.toast(f"Removed {display}", icon="🗑️")
                    time.sleep(0.5)
                    st.rerun()

    st.divider()
    st.header("Settings")

    # --- LangSmith Tracing Status ---
    tracing_on = os.environ.get("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    if tracing_on:
        project = os.environ.get("LANGCHAIN_PROJECT", "default")
        st.success(f"🔍 LangSmith tracing active\n\nProject: `{project}`")
    else:
        st.caption("🔍 LangSmith tracing: off — see `.env.example` to enable")

    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.chat_history = []
        st.toast("Chat history cleared!", icon="🧹")
        time.sleep(1)
        st.rerun()

    if st.button("Clear Workspace", type="primary", use_container_width=True):
        st.session_state.show_confirm_dialog = True

    if st.session_state.get("show_confirm_dialog", False):
        st.warning("⚠️ Are you sure? This will delete all uploaded files and the database.")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Yes, Delete All", type="primary", use_container_width=True):
                pipeline.clear_workspace()
                st.session_state.messages = []
                st.session_state.chat_history = []
                st.session_state.show_confirm_dialog = False
                st.toast("Workspace deleted successfully!", icon="🗑️")
                time.sleep(1)
                st.rerun()

        with col2:
            if st.button("Cancel", use_container_width=True):
                st.session_state.show_confirm_dialog = False
                st.rerun()

# --- Main UI ---
st.title("RAG QA Chatbot Assistant 📚")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander("📄 Sources"):
                for src in message["sources"]:
                    st.markdown(f"- **{src['file']}** — page {src['page']}")

if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        sources = []

        if pipeline.chain is None:
            message_placeholder.error("⚠️ Please upload and process documents first.")
            full_response = "Please upload and process documents first."
        else:
            with st.spinner("Thinking..."):
                try:
                    # Trim history to avoid exceeding context window
                    trimmed_history = st.session_state.chat_history[-MAX_CHAT_HISTORY_MESSAGES:]
                    stream = pipeline.chat(prompt, trimmed_history)

                    for chunk in stream:
                        # First chunk contains the retrieved source documents
                        if "context" in chunk:
                            sources = chunk["context"]
                        # Subsequent chunks stream the answer text
                        if "answer" in chunk:
                            full_response += chunk["answer"]
                            message_placeholder.markdown(full_response + "▌")

                    message_placeholder.markdown(full_response)

                except Exception as e:
                    message_placeholder.error(f"Error: {e}")
                    full_response = f"Error: {e}"

        # Display source citations
        unique_sources = []
        seen = set()
        for doc in sources:
            filename = os.path.basename(doc.metadata.get("source", "Unknown"))
            page = doc.metadata.get("page", 0) + 1  # Convert to 1-indexed
            key = (filename, page)
            if key not in seen:
                seen.add(key)
                unique_sources.append({"file": filename, "page": page})

        if unique_sources:
            with st.expander("📄 Sources"):
                for src in unique_sources:
                    st.markdown(f"- **{src['file']}** — page {src['page']}")

    # Update LangChain-format chat history
    st.session_state.chat_history.extend([
        HumanMessage(content=prompt),
        AIMessage(content=full_response),
    ])

    # Save to display history (with sources for re-render)
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response,
        "sources": unique_sources,
    })
