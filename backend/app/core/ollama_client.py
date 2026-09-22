"""
Ollama（ローカルLLM）のHTTP APIへの薄いラッパー。

埋め込み（/api/embed）とチャット生成（/api/chat）を集約し、
rag_engine.py と ingestion.py の両方から利用する。
Gemini版で行っていた429対策の指数バックオフを、
Ollamaサーバー起動直後などの一時的な接続エラーに対するリトライに置き換えている。
"""

import time

import requests

from app.core.config import CHAT_MODEL, EMBEDDING_MODEL, MAX_RETRIES, OLLAMA_BASE_URL


class OllamaError(RuntimeError):
    """Ollamaサーバーとの通信に失敗した場合の例外。"""


def embed_texts(texts: list[str]) -> list[list[float]]:
    """
    テキストのリストを、Ollamaの埋め込みAPI（バッチ対応）でベクトル化する。
    """
    wait_seconds = 2
    last_error: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/embed",
                json={"model": EMBEDDING_MODEL, "input": texts},
                timeout=120,
            )
            response.raise_for_status()
            return response.json()["embeddings"]
        except requests.RequestException as e:
            last_error = e
            if attempt < MAX_RETRIES:
                time.sleep(wait_seconds)
                wait_seconds *= 2
                continue

    raise OllamaError(
        f"Ollamaの埋め込みAPI呼び出しに失敗しました（モデル: {EMBEDDING_MODEL}）。"
        f" `ollama serve` が起動しているか、`ollama pull {EMBEDDING_MODEL}` 済みか確認してください。"
    ) from last_error


def chat_completion(prompt: str) -> str:
    """Ollamaのチャット生成APIを呼び出し、応答テキストを返す。"""
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": CHAT_MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            },
            timeout=180,
        )
        response.raise_for_status()
        return response.json()["message"]["content"]
    except requests.RequestException as e:
        raise OllamaError(
            f"Ollamaのチャット生成API呼び出しに失敗しました（モデル: {CHAT_MODEL}）。"
            f" `ollama serve` が起動しているか、`ollama pull {CHAT_MODEL}` 済みか確認してください。"
        ) from e
