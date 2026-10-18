"""Tests for RAGPipeline.load_existing_index on a real Chroma store, without loading any model."""

import chromadb
import pytest

# src.rag_pipeline imports torch-based packages at the top; skip where they are not installed (CI)
pytest.importorskip("sentence_transformers")

from src.rag_pipeline import RAGPipeline

COLLECTION = "paper_navigator_db"


@pytest.fixture
def pipeline(tmp_path):
    """A RAGPipeline built without __init__ (no models) on a throwaway Chroma folder."""
    p = RAGPipeline.__new__(RAGPipeline)
    p.client = chromadb.PersistentClient(path=str(tmp_path / "chroma"))
    p.embeddings = None
    p.chain = None
    # The real method builds the LCEL chain from the LLM; here we only need to know that it was called.
    p.setup_rag_chain = lambda: setattr(p, "chain", object())
    return p


def test_empty_collection_is_not_ready(pipeline):
    """A collection that exists but has no chunks (last file deleted, server restarted) must not report ready."""
    pipeline.client.get_or_create_collection(COLLECTION)

    assert pipeline.load_existing_index() is False
    assert pipeline.chain is None


def test_collection_with_chunks_is_ready(pipeline):
    """The fix must not break the normal case."""
    collection = pipeline.client.get_or_create_collection(COLLECTION)
    collection.add(ids=["1"], documents=["hello"], embeddings=[[0.1, 0.2, 0.3]], metadatas=[{"source": "a.txt"}])

    assert pipeline.load_existing_index() is True
    assert pipeline.chain is not None
