import os

os.environ["USE_TF"] = "0"
os.environ["USE_JAX"] = "0"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"

from dotenv import load_dotenv
load_dotenv()

import json
import threading
import shutil
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, File, HTTPException, Query, Request, UploadFile
from fastapi.responses import StreamingResponse
from langchain_core.messages import AIMessage, HumanMessage

from api.schemas import ChatRequest, UrlRequest
from src.config import DOCUMENTS_PATH, MAX_CHAT_HISTORY_MESSAGES

ALLOWED_EXT = {".pdf", ".txt", ".md", ".docx"}


def _default_factory():
    from src.rag_pipeline import RAGPipeline
    p = RAGPipeline()
    p.load_existing_index()
    return p


def _sse(event: str, data) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


def _unique_sources(docs):
    seen, out = set(), []
    for d in docs:
        f = os.path.basename(d.metadata.get("source", "Unknown"))
        page = d.metadata.get("page", 0) + 1
        if (f, page) not in seen:
            seen.add((f, page))
            out.append({"file": f, "page": page,
                        "snippet": d.page_content[:300]})
    return out


router = APIRouter(prefix="/api")


@router.get("/health")
def health(request: Request):
    p = request.app.state.pipeline
    tracing = os.environ.get("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    return {"status": "ok", "ready": p.chain is not None,
            "indexed_files": len(p.list_indexed_files()),
            "tracing": {"enabled": tracing,
                        "project": os.environ.get("LANGCHAIN_PROJECT", "default")}}


@router.get("/documents")
def list_documents(request: Request):
    return {"documents": request.app.state.pipeline.list_indexed_files()}


@router.post("/documents")
def upload_documents(request: Request, files: list[UploadFile] = File(...)):
    pipeline = request.app.state.pipeline
    lock = request.app.state.lock
    added, failed = [], []
    for f in files:
        name = os.path.basename(f.filename or "")
        if os.path.splitext(name)[1].lower() not in ALLOWED_EXT:
            failed.append({"name": name or "(no name)", "reason": "Unsupported file type"})
            continue

        path = os.path.join(DOCUMENTS_PATH, name)
        with open(path, "wb") as out:
            shutil.copyfileobj(f.file, out)

        try:
            splits = pipeline.load_and_split_file(path)
            if not splits:
                failed.append({"name": name, "reason": "No valid content"})
                continue
            with lock:
                pipeline.embed_and_store_documents(splits)
            added.append(name)
        except Exception as e:
            failed.append({"name": name, "reason": str(e)})

    if not added:
        raise HTTPException(422, detail={"added": [], "failed": failed})
    return {"added": added, "failed": failed}
    

@router.post("/documents/url")
def add_url(request: Request, body: UrlRequest):
    pipeline = request.app.state.pipeline
    lock = request.app.state.lock
    splits = pipeline.load_and_split_url(body.url)
    if not splits:
        raise HTTPException(422, "Could not extract content from URL.")
    with lock:
        pipeline.embed_and_store_documents(splits)
    return {"added": body.url}


@router.delete("/documents")
def delete_document(request: Request, source: str = Query(...)):
    pipeline = request.app.state.pipeline
    lock = request.app.state.lock
    if source not in pipeline.list_indexed_files():
        raise HTTPException(404, "Source not found in index.")
    with lock:
        pipeline.remove_document(source)
    root = os.path.realpath(DOCUMENTS_PATH)
    real = os.path.realpath(source)
    if "://" not in source and real.startswith(root + os.sep) and os.path.isfile(real):
        os.remove(real)
    return {"removed": source}
    

@router.delete("/workspace")
def clear_workspace(request: Request):
    pipeline = request.app.state.pipeline
    lock = request.app.state.lock
    with lock:
        pipeline.clear_workspace()
    return {"status": "cleared"}


@router.post("/chat")
def chat(request: Request, body: ChatRequest):
    pipeline = request.app.state.pipeline
    if pipeline.chain is None:
        raise HTTPException(409, "No documents indexed. Upload documents first.")   # A12
    msgs = [HumanMessage(content=m.content) if m.role == "user" else AIMessage(content=m.content)
            for m in body.history][-MAX_CHAT_HISTORY_MESSAGES:]                      # A14

    def event_stream():
        try:
            for chunk in pipeline.chat(body.question, msgs):
                if "context" in chunk:
                    yield _sse("sources", _unique_sources(chunk["context"]))
                if "answer" in chunk:
                    yield _sse("token", chunk["answer"])
            yield _sse("done", {})
        except Exception as e:
            yield _sse("error", {"message": str(e)})                                 # A13

    return StreamingResponse(event_stream(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


def create_app(pipeline_factory=_default_factory) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        os.makedirs(DOCUMENTS_PATH, exist_ok=True)
        app.state.pipeline = pipeline_factory()
        app.state.lock = threading.Lock()
        yield

    app = FastAPI(title="RAG QA Chatbot API", lifespan=lifespan)
    app.include_router(router)
    return app


app = create_app()   # uvicorn api.main:app
