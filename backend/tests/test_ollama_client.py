"""
app/core/ollama_client.py の単体テスト。
実際のOllamaサーバーには接続せず、requests.postをモックする。
"""

from unittest.mock import MagicMock, patch

import pytest
import requests

from app.core.ollama_client import OllamaError, chat_completion, embed_texts


@patch("app.core.ollama_client.requests.post")
def test_embed_texts_returns_embeddings_on_success(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {"embeddings": [[0.1, 0.2], [0.3, 0.4]]}
    mock_post.return_value = mock_response

    result = embed_texts(["文章1", "文章2"])

    assert result == [[0.1, 0.2], [0.3, 0.4]]
    mock_post.assert_called_once()


@patch("app.core.ollama_client.time.sleep")  # リトライ待機を実際に待たない
@patch("app.core.ollama_client.requests.post")
def test_embed_texts_raises_ollama_error_after_max_retries(mock_post, mock_sleep):
    mock_post.side_effect = requests.ConnectionError("接続できません")

    with pytest.raises(OllamaError):
        embed_texts(["文章1"])

    # config.MAX_RETRIES回だけ呼び出されていることを確認（現在の設定では3回）
    assert mock_post.call_count == 3


@patch("app.core.ollama_client.requests.post")
def test_chat_completion_returns_message_content_on_success(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {"message": {"content": "回答テキスト"}}
    mock_post.return_value = mock_response

    result = chat_completion("質問プロンプト")

    assert result == "回答テキスト"


@patch("app.core.ollama_client.requests.post")
def test_chat_completion_raises_ollama_error_on_connection_failure(mock_post):
    mock_post.side_effect = requests.ConnectionError("接続できません")

    with pytest.raises(OllamaError):
        chat_completion("質問プロンプト")
