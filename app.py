# app.py

import time
import streamlit as st
import os
from src.rag_pipeline import RAGPipeline
from src.config import DOCUMENTS_PATH

# --- App Configuration ---
st.set_page_config(
    page_title="RAG Research Assistant",
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
    st.session_state.pipeline.load_existing_index()

pipeline = st.session_state.pipeline

# --- Sidebar: Upload and Information ---
with st.sidebar:
    st.header("📚 RAG Research Assistant")
    st.write("Upload PDF files to start asking questions.")
    
    # --- File Uploader Logic ---
    uploaded_files = st.file_uploader(
        "Choose PDF files", 
        type=["pdf"], 
        accept_multiple_files=True,
        label_visibility="collapsed"
    )

    if uploaded_files:
        # The process button only appears when files are selected
        if st.button("Process Documents", use_container_width=True):
            with st.spinner("Processing documents... Please wait."):
                try:
                    # Save files to the documents directory
                    for uploaded_file in uploaded_files:
                        file_path = os.path.join(DOCUMENTS_PATH, uploaded_file.name)
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                    
                    # Load and split documents
                    splits = pipeline.load_and_split_documents()
                    
                    if splits:
                        # Embed and store documents
                        pipeline.embed_and_store_documents(splits)
                        st.toast("Documents processed successfully!", icon="✅")
                    else:
                        st.error("Could not load documents. No valid PDF content found.")
                except Exception as e:
                    st.error(f"Error processing documents: {e}")
    
    st.divider()
    st.header("Settings")

    # Clear chat history button
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.toast("Chat history cleared!", icon="🧹")
        time.sleep(1)
        st.rerun()

    # Clear workspace button
    if st.button("Clear Workspace", type="primary", use_container_width=True):
        st.session_state.show_confirm_dialog = True

    if st.session_state.get("show_confirm_dialog", False):
        st.warning("⚠️ Are you sure? This will delete all uploaded files and the database.")

        col1, col2 = st.columns(2)
        
        # Button YES (Confirm)
        with col1:
            if st.button("Yes, Delete All", type="primary", use_container_width=True):
                pipeline.clear_workspace()
                st.session_state.messages = [] # Clear chat history
                st.session_state.show_confirm_dialog = False # Close dialog
                st.toast("Workspace deleted successfully!", icon="🗑️")
                time.sleep(1) # Pause briefly to show toast
                st.rerun()
        
        # Button NO (Cancel)
        with col2:
            if st.button("Cancel", use_container_width=True):
                st.session_state.show_confirm_dialog = False # Close dialog
                st.rerun()

# --- Main UI ---
st.title("RAG Research Assistant 📚")

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hello! Upload a PDF and ask me anything."}]

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("Ask a question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
            
        if pipeline.chain is None:
            message_placeholder.error("⚠️ Please upload and process documents first.")
            full_response = "Please upload and process documents first."
        else:
            with st.spinner("Thinking..."):
                try:
                    stream = pipeline.chat(prompt)

                    for chunk in stream:
                        full_response += chunk
                        message_placeholder.markdown(full_response + "▌")
                    
                    message_placeholder.markdown(full_response)
                except Exception as e:
                    message_placeholder.error(f"Error: {e}")
                    full_response = f"Error: {e}"

    st.session_state.messages.append({"role": "assistant", "content": full_response})

