"""Tests for src/index_state.py against a real Chroma store in a throwaway folder."""

import chromadb
import pytest

from src.index_state import has_indexed_chunks

NAME = "paper_navigator_db"


@pytest.fixture
def client(tmp_path):
    return chromadb.PersistentClient(path=str(tmp_path / "chroma"))


@pytest.fixture
def collection(client):
    return client.get_or_create_collection(NAME)


def add_chunk(collection):
    """Pass embeddings by hand so Chroma does not download its default model."""
    collection.add(ids=["1"], documents=["hello"], embeddings=[[0.1, 0.2, 0.3]], metadatas=[{"source": "a.txt"}])


def test_missing_collection_has_no_chunks(client):
    assert has_indexed_chunks(client, NAME) is False


def test_empty_collection_has_no_chunks(collection, client):
    assert has_indexed_chunks(client, NAME) is False


def test_collection_survives_deleting_its_last_chunk(collection, client):
    """The bug: removing the last file leaves the collection behind, and it must not count as ready."""
    add_chunk(collection)
    collection.delete(where={"source": "a.txt"})

    assert has_indexed_chunks(client, NAME) is False


def test_collection_with_a_chunk_has_chunks(collection, client):
    add_chunk(collection)

    assert has_indexed_chunks(client, NAME) is True
