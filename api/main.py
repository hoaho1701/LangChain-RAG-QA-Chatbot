# api/main.py

import os

# Must be set before any ML library is imported.
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"

from dotenv import load_dotenv

load_dotenv()  # load .env before src.config reads the environment

import json
import shutil
import threading
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import APIRouter, FastAPI, File, HTTPException, Query, Request, UploadFile
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage, HumanMessage

from api.schemas import ChatRequest, HistoryMessage, UrlRequest
from src.config import DOCUMENTS_PATH, MAX_CHAT_HISTORY_MESSAGES

ALLOWED_EXT = {".pdf", ".txt", ".md", ".docx"}
SNIPPET_LENGTH = 300


def _default_factory():
    """Build the real pipeline. Imported lazily so tests never load torch or the models."""
    from src.rag_pipeline import RAGPipeline

    pipeline = RAGPipeline()
    pipeline.load_existing_index()
    return pipeline


def _sse(event: str, data) -> str:
    """Format one Server-Sent Event. ensure_ascii=False keeps Vietnamese text readable."""
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _unique_sources(docs) -> list[dict]:
    """Deduplicate retrieved chunks by (file, page); pages are 1-indexed for display."""
    seen, sources = set(), []
    for doc in docs:
        file = os.path.basename(doc.metadata.get("source", "Unknown"))
        page = doc.metadata.get("page", 0) + 1
        if (file, page) not in seen:
            seen.add((file, page))
            sources.append({"file": file, "page": page, "snippet": doc.page_content[:SNIPPET_LENGTH]})
    return sources


def _to_messages(history: list[HistoryMessage]) -> list:
    """Convert client history to LangChain messages, keeping only the most recent ones."""
    message_class = {"user": HumanMessage, "assistant": AIMessage}
    messages = [message_class[m.role](content=m.content) for m in history]
    return messages[-MAX_CHAT_HISTORY_MESSAGES:]


router = APIRouter(prefix="/api")


@router.get("/health")
def health(request: Request):
    """Report whether the pipeline is ready to answer."""
    pipeline = request.app.state.pipeline
    return {
        "status": "ok",
        "ready": pipeline.chain is not None,
        "indexed_files": len(pipeline.list_indexed_files()),
    }


@router.get("/documents")
def list_documents(request: Request):
    """List every indexed source (file path or URL)."""
    return {"documents": request.app.state.pipeline.list_indexed_files()}


@router.post("/documents")
def upload_documents(request: Request, files: list[UploadFile] = File(...)):
    """Save uploaded files into documents/ and index them. Bad files are reported, not fatal."""
    pipeline = request.app.state.pipeline
    lock = request.app.state.lock
    added, failed = [], []

    for upload in files:
        # basename() blocks path traversal such as "../../etc/x"
        name = os.path.basename(upload.filename or "")
        if os.path.splitext(name)[1].lower() not in ALLOWED_EXT:
            failed.append({"name": name or "(no name)", "reason": "Unsupported file type"})
            continue

        # Keeps metadata "source" as "./documents/<name>", which eval/dataset.json relies on
        path = os.path.join(DOCUMENTS_PATH, name)
        with open(path, "wb") as out:
            shutil.copyfileobj(upload.file, out)

        try:
            splits = pipeline.load_and_split_file(path)  # slow but read-only: kept outside the lock
            if not splits:
                Path(path).unlink(missing_ok=True)
                failed.append({"name": name, "reason": "No valid content"})
                continue
            with lock:
                pipeline.embed_and_store_documents(splits)
            added.append(name)
        except Exception as e:
            Path(path).unlink(missing_ok=True)
            failed.append({"name": name, "reason": str(e)})

    if not added:
        raise HTTPException(422, detail={"added": [], "failed": failed})
    return {"added": added, "failed": failed}


@router.post("/documents/url")
def add_url(request: Request, body: UrlRequest):
    """Fetch a web page and index its text."""
    pipeline = request.app.state.pipeline
    lock = request.app.state.lock

    splits = pipeline.load_and_split_url(body.url)  # network call: kept outside the lock
    if not splits:
        raise HTTPException(422, "Could not extract content from URL.")
    with lock:
        pipeline.embed_and_store_documents(splits)
    return {"added": body.url}


@router.delete("/documents")
def delete_document(request: Request, source: str = Query(...)):
    """Remove a source from the index, and from disk if it is a file inside documents/."""
    pipeline = request.app.state.pipeline
    lock = request.app.state.lock

    if source not in pipeline.list_indexed_files():
        raise HTTPException(404, "Source not found in index.")
    with lock:
        pipeline.remove_document(source)

    # Never delete anything outside documents/ (URLs have no file at all)
    root = os.path.realpath(DOCUMENTS_PATH)
    real = os.path.realpath(source)
    if "://" not in source and real.startswith(root + os.sep) and os.path.isfile(real):
        os.remove(real)
    return {"removed": source}


@router.delete("/workspace")
def clear_workspace(request: Request):
    """Delete all uploaded files and the whole vector database."""
    with request.app.state.lock:
        request.app.state.pipeline.clear_workspace()
    return {"status": "cleared"}


@router.post("/chat")
def chat(request: Request, body: ChatRequest):
    """Stream an answer as Server-Sent Events: one `sources`, many `token`, then `done`."""
    pipeline = request.app.state.pipeline

    # Checked before streaming starts, so a real status code can still be returned
    if pipeline.chain is None:
        raise HTTPException(409, "No documents indexed. Upload documents first.")

    history = _to_messages(body.history)

    def event_stream():
        try:
            for chunk in pipeline.chat(body.question, history):
                if "context" in chunk:
                    yield _sse("sources", _unique_sources(chunk["context"]))
                if "answer" in chunk:
                    yield _sse("token", chunk["answer"])
            yield _sse("done", {})
        except Exception as e:
            # The 200 status is already sent, so errors can only travel inside the stream
            yield _sse("error", {"message": str(e)})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},  # no proxy buffering
    )


def create_app(pipeline_factory=_default_factory) -> FastAPI:
    """Build the app. Tests pass a fake factory so no model is loaded."""

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        os.makedirs(DOCUMENTS_PATH, exist_ok=True)
        app.state.pipeline = pipeline_factory()  # loads models once; the server accepts requests only after
        app.state.lock = threading.Lock()  # serializes writes to ChromaDB
        yield

    app = FastAPI(title="RAG QA Chatbot API", lifespan=lifespan)
    app.include_router(router)
    return app


app = create_app()  # run with: uv run uvicorn api.main:app
