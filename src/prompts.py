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
    "Do not add facts, terminology, or explanations that are not explicitly stated in the "
    "context, even if they seem plausible — synthesizing means combining what the context "
    "says, not inventing new detail. "
    "If the context contains passages from different sources on a similar topic, base your "
    "answer on the passage that most directly and specifically answers the question, and do "
    "not blend details from unrelated passages. "
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
    "You are grading whether each retrieved document is relevant to a question — i.e. whether "
    "it contains information that would help answer the question, even partially.\n"
    "The question may be written in a different language than the documents; judge relevance "
    "by meaning, not by language or exact wording match.\n"
    "Be inclusive: if a document plausibly relates to the topic of the question, count it as "
    "relevant even if it doesn't fully answer it — a later synthesis step will pick the best parts.\n"
    "List the indices (comma-separated, 0-indexed) of every relevant document.\n"
    "If none are relevant at all, output \"none\".\n"
    "Output only the indices or \"none\", nothing else. Examples: \"0,2\" or \"1,3\" or \"none\"."
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

# Evaluation — LLM-as-judge: does the generated answer match the reference answer?
CORRECTNESS_SYSTEM_PROMPT = (
    "You are grading whether a generated answer is correct compared to a reference answer.\n"
    "Reply \"yes\" if the generated answer conveys the same key facts as the reference answer, "
    "even if worded differently. Reply \"no\" if it is missing key facts or contradicts it.\n"
    "Output only \"yes\" or \"no\", nothing else."
)

CORRECTNESS_JUDGE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", CORRECTNESS_SYSTEM_PROMPT),
    ("human", "Question: {question}\n\nReference answer: {reference}\n\nGenerated answer: {answer}"),
])

# Evaluation — LLM-as-judge: is the generated answer grounded in the retrieved context?
FAITHFULNESS_SYSTEM_PROMPT = (
    "You are grading whether a generated answer is faithful to the provided context — "
    "i.e. every claim in the answer is supported by the context, with no fabricated information.\n"
    "Reply \"yes\" if the answer is fully supported by the context, or \"no\" if it contains "
    "unsupported or fabricated claims.\n"
    "Output only \"yes\" or \"no\", nothing else."
)

FAITHFULNESS_JUDGE_PROMPT = ChatPromptTemplate.from_messages([
    ("system", FAITHFULNESS_SYSTEM_PROMPT),
    ("human", "Context:\n{context}\n\nGenerated answer: {answer}"),
])
