"""Split text into overlapping chunks; kept apart from rag_pipeline so CI can test it without torch."""

from typing import List

from langchain_core.documents.base import Document

SEPARATORS = ["\n\n", "\n", ". ", " ", ""]


def split_documents(docs: List[Document], chunk_size: int, chunk_overlap: int) -> List[Document]:
    """Split documents into overlapping chunks on natural text boundaries."""
    splits = []

    for doc in docs:
        chunks = _recursive_split(doc.page_content, chunk_size, chunk_overlap, SEPARATORS)
        for i, chunk in enumerate(chunks):
            splits.append(
                Document(
                    page_content=chunk,
                    metadata={**doc.metadata, "start_index": i},
                )
            )
    return splits


def _recursive_split(
    text: str, chunk_size: int, chunk_overlap: int, separators: List[str], nested: bool = False
) -> List[str]:
    """Recursively split text on decreasing separators until chunks fit chunk_size.

    The overlap is added once, by the outermost call. A nested call (a part that is itself longer than chunk_size)
    only splits, otherwise its chunks would be overlapped again by the caller and repeat the same text twice.
    """
    if len(text) <= chunk_size:
        return [text] if text.strip() else []

    sep = ""
    remaining = list(separators)
    while remaining:
        candidate = remaining.pop(0)
        if candidate and candidate in text:
            sep = candidate
            break

    if not sep:
        # Fall back to hard character split
        return _hard_split(text, chunk_size, 0 if nested else chunk_overlap)

    parts = text.split(sep)
    chunks: List[str] = []
    current = ""

    for part in parts:
        candidate = (current + sep + part).lstrip(sep) if current else part
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                chunks.append(current)
            if len(part) > chunk_size:
                chunks.extend(_recursive_split(part, chunk_size, chunk_overlap, remaining[:], nested=True))
                current = ""
            else:
                current = part

    if current:
        chunks.append(current)

    # Apply overlap: prepend tail of previous chunk to next
    if nested or chunk_overlap <= 0 or len(chunks) <= 1:
        return [c for c in chunks if c.strip()]

    overlapped: List[str] = [chunks[0]]
    for i in range(1, len(chunks)):
        prev_tail = chunks[i - 1][-chunk_overlap:]
        merged = prev_tail + sep + chunks[i]
        overlapped.append(merged if len(merged) <= chunk_size * 1.2 else chunks[i])

    return [c for c in overlapped if c.strip()]


def _hard_split(text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
    """Simple sliding-window character split when no separator works."""
    chunks = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - chunk_overlap
    return chunks
