# src/prompts.py

from llama_index.core import PromptTemplate

# Translate the prompt into English for better understanding by the LLM
QA_TEMPLATE_STR = (
    "You are an expert AI research assistant. Your task is to provide a comprehensive and synthesized answer to the user's question based ONLY on the provided context.\n"
    "Analyze all parts of the context to form a complete understanding. Do not just extract sentences.\n"
    "If the context does not contain the answer, state that you cannot find the relevant information in the provided documents.\n\n"
    "Context Information:\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "User's Question: {query_str}\n"
    "Your Answer (in the same language as the question):"
)

QA_TEMPLATE = PromptTemplate(QA_TEMPLATE_STR)