# src/prompts.py

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Prompt to rephrase the user question as a standalone question based on chat history
CONTEXTUALIZE_Q_SYSTEM_PROMPT = (
    "Given a chat history and the latest user question which might reference "
    "context in the chat history, formulate a standalone question which can be "
    "understood without the chat history. Do NOT answer the question, just "
    "reformulate it if needed and otherwise return it as is."
)

CONTEXTUALIZE_Q_PROMPT = ChatPromptTemplate.from_messages([
    ("system", CONTEXTUALIZE_Q_SYSTEM_PROMPT),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

# Main QA prompt with conversation history support
QA_SYSTEM_PROMPT = (
    "You are an expert AI research assistant. "
    "Your task is to provide a comprehensive and synthesized answer to the user's question "
    "based ONLY on the provided context.\n\n"
    "Analyze all parts of the context to form a complete understanding. "
    "Do not just extract sentences. "
    "If the context does not contain the answer, state that you cannot find "
    "the relevant information in the provided documents.\n\n"
    "Context:\n{context}"
)

QA_PROMPT = ChatPromptTemplate.from_messages([
    ("system", QA_SYSTEM_PROMPT),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

# Agentic RAG — grade retrieved documents for relevance
GRADE_SYSTEM_PROMPT = (
    "You are grading retrieved documents for relevance to a question.\n"
    "List the indices (comma-separated, 0-indexed) of documents that are relevant.\n"
    "If none are relevant, output \"none\".\n"
    "Output only indices or \"none\", nothing else. Examples: \"0,2\" or \"1,3\" or \"none\"."
)

GRADE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", GRADE_SYSTEM_PROMPT),
    ("human", "Question: {question}\n\nDocuments:\n{documents}"),
])

# Agentic RAG — rewrite query when retrieved docs are not relevant
REWRITE_SYSTEM_PROMPT = (
    "Rewrite the following question to be more specific and detailed "
    "to improve document retrieval accuracy. "
    "Output only the rewritten question, nothing else."
)

REWRITE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", REWRITE_SYSTEM_PROMPT),
    ("human", "{question}"),
])
