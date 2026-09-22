"""
FastAPIエントリポイント。

起動時（lifespan）にChromaコレクションを初期化し、app.state に保持する。
Gemini版と異なり、外部LLM APIクライアントの初期化は不要
（Ollamaはリクエストごとにapp/core/ollama_client.pyがHTTP呼び出しする方式）。
"""

from contextlib import asynccontextmanager

import chromadb
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat import router as chat_router
from app.core.config import COLLECTION_NAME, DB_DIR

# ブラウザ（フロントエンド）から別オリジンのこのAPIを呼べるようにするオリジン一覧。
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    chroma_client = chromadb.PersistentClient(path=DB_DIR)
    app.state.collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
    yield


app = FastAPI(title="Enterprise RAG Chatbot API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api")


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}
