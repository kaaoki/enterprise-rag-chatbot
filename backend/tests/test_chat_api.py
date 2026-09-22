"""
/api/chat, /api/documents などのAPIエンドポイントのテスト。
Ollama呼び出しとChromaコレクションはモックに差し替える
（実際にOllamaサーバーが起動していなくてもテストが通るようにするため）。
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from app.core.ollama_client import OllamaError
from app.main import app


@pytest.fixture
def client_with_mock_collection():
    mock_collection = MagicMock()
    mock_collection.query.return_value = {
        "documents": [["チャンク内容"]],
        "metadatas": [[{"source": "sample.pdf"}]],
    }
    mock_collection.get.return_value = {"metadatas": [{"source": "sample.pdf"}]}

    with TestClient(app) as test_client:
        app.state.collection = mock_collection
        yield test_client


def test_health_check_returns_ok():
    with TestClient(app) as test_client:
        response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("app.core.rag_engine.chat_completion", return_value="モック回答です。")
@patch("app.core.rag_engine.embed_texts", return_value=[[0.1, 0.2]])
def test_chat_returns_answer_and_sources(mock_embed, mock_chat, client_with_mock_collection):
    response = client_with_mock_collection.post("/api/chat", json={"question": "テスト質問", "top_k": 1})
    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "モック回答です。"
    assert body["sources"] == ["sample.pdf"]


@patch("app.core.rag_engine.embed_texts", side_effect=OllamaError("Ollamaに接続できません。"))
def test_chat_returns_502_when_ollama_unreachable(mock_embed, client_with_mock_collection):
    response = client_with_mock_collection.post("/api/chat", json={"question": "テスト質問", "top_k": 1})
    assert response.status_code == 502


def test_chat_rejects_empty_question(client_with_mock_collection):
    response = client_with_mock_collection.post("/api/chat", json={"question": "", "top_k": 1})
    assert response.status_code == 422


def test_chat_rejects_top_k_out_of_range(client_with_mock_collection):
    response = client_with_mock_collection.post("/api/chat", json={"question": "質問", "top_k": 99})
    assert response.status_code == 422


def test_list_documents_returns_sorted_sources(client_with_mock_collection):
    response = client_with_mock_collection.get("/api/documents")
    assert response.status_code == 200
    assert response.json() == {"sources": ["sample.pdf"]}
