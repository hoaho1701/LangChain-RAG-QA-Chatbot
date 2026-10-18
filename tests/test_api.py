"""API tests with a fake pipeline: no Ollama, no HF models, no ChromaDB needed."""

import json
import re

import pytest
from fastapi.testclient import TestClient
from langchain_core.documents.base import Document
from langchain_core.messages import AIMessage, HumanMessage

from api.main import create_app


class FakePipeline:
    """Same public surface that api/main.py uses on RAGPipeline."""

    def __init__(self):
        self.chain = object()  # non-None = "ready", like RAGPipeline.chain
        self.files = []
        self.last_history = None

    def list_indexed_files(self):
        return self.files

    def load_and_split_file(self, path):
        return [Document(page_content="x", metadata={"source": path, "page": 0})]

    def load_and_split_url(self, url):
        if "empty" in url:
            return []  # simulate a page with no extractable text
        return [Document(page_content="x", metadata={"source": url, "page": 0})]

    def embed_and_store_documents(self, splits):
        self.files += [s.metadata["source"] for s in splits]
        return True

    def remove_document(self, path):
        self.files.remove(path)

    def clear_workspace(self):
        self.files.clear()
        self.chain = None

    def chat(self, question, history):
        self.last_history = history
        yield {"context": [Document(page_content="c", metadata={"source": "./documents/a.pdf", "page": 2})]}
        yield {"answer": "Hel"}
        yield {"answer": "lo"}


@pytest.fixture
def client(tmp_path, monkeypatch):
    # Upload/delete must never touch the real ./documents folder.
    monkeypatch.setattr("api.main.DOCUMENTS_PATH", str(tmp_path))
    fake = FakePipeline()
    # `with` is required: it runs the lifespan, which is what creates app.state.pipeline/lock.
    with TestClient(create_app(lambda: fake)) as c:
        c.fake = fake
        c.docs_dir = tmp_path
        yield c


def parse_sse(text):
    """'event: x\\ndata: {json}\\n\\n' blocks -> [(event, data), ...]"""
    events = []
    for block in text.strip().split("\n\n"):
        name = re.search(r"^event: (.*)$", block, re.M).group(1)
        data = json.loads(re.search(r"^data: (.*)$", block, re.M).group(1))
        events.append((name, data))
    return events


def upload(client, name, content=b"hello", ctype="text/plain"):
    return client.post("/api/documents", files=[("files", (name, content, ctype))])


# ---------- health / list ----------


def test_health_ready(client):
    body = client.get("/api/health").json()
    assert body["status"] == "ok"
    assert body["ready"] is True
    assert "tracing" not in body


def test_health_not_ready_without_documents(client):
    client.fake.chain = None
    assert client.get("/api/health").json()["ready"] is False


# ---------- upload ----------


def test_upload_ok(client):
    r = upload(client, "notes.txt")
    assert r.status_code == 200
    assert r.json()["added"] == ["notes.txt"]
    assert (client.docs_dir / "notes.txt").read_bytes() == b"hello"
    assert client.get("/api/documents").json()["documents"] == [str(client.docs_dir / "notes.txt")]


def test_upload_rejects_unsupported_extension(client):
    r = upload(client, "virus.exe", ctype="application/octet-stream")
    assert r.status_code == 422
    assert r.json()["detail"]["failed"][0]["name"] == "virus.exe"
    assert not (client.docs_dir / "virus.exe").exists()


def test_upload_extension_check_is_case_insensitive(client):
    assert upload(client, "NOTES.TXT").status_code == 200


def test_upload_mixed_batch_keeps_good_files(client):
    r = client.post(
        "/api/documents",
        files=[
            ("files", ("good.md", b"# hi", "text/markdown")),
            ("files", ("bad.exe", b"x", "application/octet-stream")),
        ],
    )
    assert r.status_code == 200
    body = r.json()
    assert body["added"] == ["good.md"]
    assert body["failed"][0]["name"] == "bad.exe"


def test_upload_blocks_path_traversal(client):
    r = upload(client, "../../evil.txt")
    assert r.status_code == 200
    assert (client.docs_dir / "evil.txt").exists()  # saved INSIDE the documents dir
    assert not (client.docs_dir.parent / "evil.txt").exists()  # not above it
    assert not (client.docs_dir.parent.parent / "evil.txt").exists()


def test_upload_empty_content_is_reported(client):
    client.fake.load_and_split_file = lambda path: []
    r = upload(client, "empty.txt")
    assert r.status_code == 422
    assert r.json()["detail"]["failed"][0]["reason"] == "No valid content"


def test_upload_pipeline_error_is_reported_not_500(client):
    def boom(path):
        raise RuntimeError("cannot parse")

    client.fake.load_and_split_file = boom
    r = upload(client, "broken.txt")
    assert r.status_code == 422
    assert "cannot parse" in r.json()["detail"]["failed"][0]["reason"]


# ---------- url ----------


def test_add_url_ok(client):
    r = client.post("/api/documents/url", json={"url": "https://example.com/page"})
    assert r.status_code == 200
    assert "https://example.com/page" in client.fake.files


def test_add_url_without_content(client):
    r = client.post("/api/documents/url", json={"url": "https://empty.example.com"})
    assert r.status_code == 422


# ---------- delete / workspace ----------


def test_delete_document_removes_index_entry_and_file(client):
    upload(client, "a.txt")
    source = client.get("/api/documents").json()["documents"][0]
    r = client.delete("/api/documents", params={"source": source})
    assert r.status_code == 200
    assert client.fake.files == []
    assert not (client.docs_dir / "a.txt").exists()


def test_delete_unknown_source_is_404(client):
    assert client.delete("/api/documents", params={"source": "./documents/nope.pdf"}).status_code == 404


def test_delete_never_removes_files_outside_documents_dir(client):
    outside = client.docs_dir.parent / "keep.txt"
    outside.write_text("precious")
    client.fake.files.append(str(outside))  # indexed, but lives outside DOCUMENTS_PATH
    r = client.delete("/api/documents", params={"source": str(outside)})
    assert r.status_code == 200
    assert outside.exists()  # index entry removed, file on disk untouched


def test_delete_url_source_does_not_touch_disk(client):
    client.post("/api/documents/url", json={"url": "https://example.com/x"})
    r = client.delete("/api/documents", params={"source": "https://example.com/x"})
    assert r.status_code == 200
    assert client.fake.files == []


def test_clear_workspace(client):
    upload(client, "a.txt")
    r = client.delete("/api/workspace")
    assert r.status_code == 200
    assert client.fake.files == []
    assert client.get("/api/health").json()["ready"] is False


# ---------- chat (SSE) ----------


def test_chat_streams_sources_tokens_done(client):
    r = client.post("/api/chat", json={"question": "hi", "history": []})
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/event-stream")

    events = parse_sse(r.text)
    assert [name for name, _ in events] == ["sources", "token", "token", "done"]

    sources = events[0][1]
    assert sources == [{"file": "a.pdf", "page": 3, "snippet": "c"}]  # basename + page is 1-indexed
    assert "".join(data for name, data in events if name == "token") == "Hello"


def test_chat_without_documents_is_409(client):
    client.fake.chain = None
    r = client.post("/api/chat", json={"question": "hi", "history": []})
    assert r.status_code == 409


def test_chat_empty_question_is_422(client):
    assert client.post("/api/chat", json={"question": "", "history": []}).status_code == 422


def test_chat_error_becomes_error_event(client):
    def boom(question, history):
        raise RuntimeError("ollama down")
        yield  # makes this a generator, like the real chat()

    client.fake.chat = boom
    r = client.post("/api/chat", json={"question": "hi", "history": []})
    assert r.status_code == 200  # headers were already sent; error travels in the stream
    events = parse_sse(r.text)
    assert events[-1][0] == "error"
    assert "ollama down" in events[-1][1]["message"]


def test_chat_trims_history_and_maps_roles(client):
    history = [{"role": "user" if i % 2 == 0 else "assistant", "content": f"m{i}"} for i in range(50)]
    client.post("/api/chat", json={"question": "hi", "history": history})

    received = client.fake.last_history
    assert len(received) == 20  # MAX_CHAT_HISTORY_MESSAGES
    assert received[0].content == "m30"  # keeps the most recent ones
    assert isinstance(received[0], HumanMessage)
    assert isinstance(received[1], AIMessage)


def test_chat_rejects_unknown_role(client):
    r = client.post("/api/chat", json={"question": "hi", "history": [{"role": "system", "content": "x"}]})
    assert r.status_code == 422


def test_upload_without_content_leaves_no_file(client):
    client.fake.load_and_split_file = lambda path: []
    r = upload(client, "empty.txt")
    assert r.status_code == 422
    assert not (client.docs_dir / "empty.txt").exists()


def test_upload_error_leaves_no_file(client):
    def boom(path):
        raise RuntimeError("cannot parse")

    client.fake.load_and_split_file = boom
    r = upload(client, "broken.txt")
    assert r.status_code == 422
    assert not (client.docs_dir / "broken.txt").exists()


def test_upload_failure_keeps_the_good_files(client):
    load = client.fake.load_and_split_file
    client.fake.load_and_split_file = lambda path: [] if path.endswith("empty.txt") else load(path)

    r = client.post(
        "/api/documents",
        files=[
            ("files", ("good.txt", b"hello", "text/plain")),
            ("files", ("empty.txt", b"", "text/plain")),
        ],
    )
    assert r.status_code == 200
    assert (client.docs_dir / "good.txt").exists()
    assert not (client.docs_dir / "empty.txt").exists()
