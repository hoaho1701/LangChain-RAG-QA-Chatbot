# src/prompts.py

from langchain_core.prompts import PromptTemplate

# Translate the prompt into English for better understanding by the LLM
QA_TEMPLATE_STR = """You are an expert AI research assistant. 
Your task is to provide a comprehensive and synthesized answer to the user's question based ONLY on the provided context.

Analyze all parts of the context to form a complete understanding. Do not just extract sentences.
If the context does not contain the answer, state that you cannot find the relevant information in the provided documents.

Context Information:
---------------------
{context}
---------------------

User's Question: {question}

Your Answer:"""

QA_TEMPLATE = PromptTemplate.from_template(QA_TEMPLATE_STR)