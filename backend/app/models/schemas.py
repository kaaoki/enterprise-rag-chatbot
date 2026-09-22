"""
APIのリクエスト/レスポンススキーマ（Pydanticモデル）。
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="ユーザーからの質問")
    top_k: int = Field(default=4, ge=1, le=10, description="検索するチャンク数")


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


class DocumentsResponse(BaseModel):
    sources: list[str]


class IngestResponse(BaseModel):
    processed_files: list[str]
    skipped_files: list[str]
    total_chunks: int
