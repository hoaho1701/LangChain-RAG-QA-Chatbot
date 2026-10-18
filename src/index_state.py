"""Check whether the Chroma index can answer questions; kept apart from rag_pipeline so CI can test it without torch."""


def has_indexed_chunks(client, collection_name: str) -> bool:
    """True when the collection exists and holds at least one chunk."""
    try:
        # A collection outlives its last chunk, so existing is not enough
        return client.get_collection(collection_name).count() > 0
    except Exception:
        return False
