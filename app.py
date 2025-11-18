# app.py

import time
import streamlit as st
import os
from src.rag_pipeline import RAGPipeline
from src.config import DOCUMENTS_PATH

# --- App Configuration ---
st.set_page_config(
    page_title="Paper Navigator",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Ensure the documents directory exists
if not os.path.exists(DOCUMENTS_PATH):
    os.makedirs(DOCUMENTS_PATH)

# --- State Management ---
if "pipeline" not in st.session_state:
    print("Initializing RAG Pipeline for new session...")
    st.session_state.pipeline = RAGPipeline()

pipeline = st.session_state.pipeline

# --- Sidebar: Upload & Info ---
with st.sidebar:
    st.header("📚 Paper Navigator")
    st.write("Upload scientific papers (PDF) to start asking questions.")
    
    # --- File Uploader Logic ---
    uploaded_files = st.file_uploader(
        "Choose PDF files", 
        type=["pdf"], 
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:
        # The process button only appears when files are selected
        if st.button("Process and Load Data", use_container_width=True):
            with st.spinner("Processing documents... This may take a moment."):
                # Save files to the documents directory
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(DOCUMENTS_PATH, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                
                pipeline.reset_index()

                if "messages" not in st.session_state:
                    st.session_state.messages = []
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"🔄 **The system has been updated with {len(uploaded_files)} new document(s).** You can now continue asking questions."
                })

                st.toast(f"Successfully processed {len(uploaded_files)} file(s)!", icon="🎉")
                st.rerun()
    
    st.divider()
    st.header("Settings")

    # Clear chat history button
    if st.button("Clear Chat History", use_container_width=True):
        if "messages" in st.session_state:
            st.session_state.messages = []
        st.toast("Chat history cleared!", icon="🗑️")
        st.rerun()

    # Clear workspace button
    if st.button("Delete All Data", type="primary", use_container_width=True):
        st.session_state.confirm_delete = True

    if st.session_state.get("confirm_delete", False):
        st.warning(
            "This action will delete all uploaded files and the database. Are you sure?", 
            icon="⚠️"
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button("YES, DELETE NOW", use_container_width=True):
                with st.spinner("Deleting data..."):
                    pipeline.clear_workspace()
                    # st.session_state.messages = []
                    if "pipeline" in st.session_state:
                        del st.session_state.pipeline
                    if "messages" in st.session_state: 
                        del st.session_state.messages
                    st.session_state.confirm_delete = False
                    st.success("All data has been deleted!", icon="✅")
                    time.sleep(2)
                    st.rerun()
        with col2:
            if st.button("CANCEL", use_container_width=True):
                st.session_state.confirm_delete = False
                st.rerun()

# --- Main UI ---
st.title("Paper Navigator: Your AI Research Assistant")

# Get query engine (can be None if no data yet)
query_engine = pipeline.get_query_engine()

if query_engine is None:
    st.info("👋 Welcome! Please upload documents in the sidebar to get started.")
else:
    # Initialize chat history
    if "messages" not in st.session_state or not st.session_state.messages:
        st.session_state.messages = [
            {"role": "assistant", "content": "Hello! I'm ready to answer your questions about the documents."}
        ]

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle new question
    if prompt := st.chat_input("Ask about the document content..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
                
            with st.spinner("Thinking..."):
                try:
                    streaming_response = query_engine.query(prompt)
                    for text in streaming_response.response_gen:
                        full_response += text
                        message_placeholder.markdown(full_response + "▌")
                    message_placeholder.markdown(full_response)
                except Exception as e:
                    full_response = f"An error occurred: {e}"
                    message_placeholder.error(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

