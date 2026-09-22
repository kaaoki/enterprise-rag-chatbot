"""
チャット・資料一覧・文書取り込み用のエンドポイント。
"""

from fastapi import APIRouter, HTTPException, Request

from app.core.ingestion import ingest_documents
from app.core.ollama_client import OllamaError
from app.core.rag_engine import answer_question
from app.models.schemas import ChatRequest, ChatResponse, DocumentsResponse, IngestResponse

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: Request, body: ChatRequest) -> ChatResponse:
    collection = request.app.state.collection
    try:
        answer, sources = answer_question(collection, body.question, top_k=body.top_k)
    except OllamaError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    return ChatResponse(answer=answer, sources=sources)


@router.get("/documents", response_model=DocumentsResponse)
def list_documents(request: Request) -> DocumentsResponse:
    collection = request.app.state.collection
    try:
        all_meta = collection.get()["metadatas"]
        sources = sorted({m["source"] for m in all_meta})
    except Exception:
        sources = []
    return DocumentsResponse(sources=sources)


@router.post("/documents/ingest", response_model=IngestResponse)
def ingest(request: Request) -> IngestResponse:
    collection = request.app.state.collection
    try:
        processed, skipped, total_chunks = ingest_documents(collection)
    except FileNotFoundError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except OllamaError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    return IngestResponse(processed_files=processed, skipped_files=skipped, total_chunks=total_chunks)
