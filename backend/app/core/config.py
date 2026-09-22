"""
設定値・環境変数の読み込み。

Gemini APIからOllama（ローカルLLM）に切り替えたバージョン。
病院案件のツールと同じくOllamaを使うため、追加の外部登録・APIキーは不要。
"""

import os

DB_DIR = os.environ.get("CHROMA_DB_DIR", "chroma_db")
COLLECTION_NAME = "documents"

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
# 日本語資料も扱うため、多言語対応の埋め込みモデルをデフォルトにしている。
EMBEDDING_MODEL = os.environ.get("OLLAMA_EMBEDDING_MODEL", "bge-m3")
# 病院案件と同じくELYZA-JP-8Bをデフォルトに。環境に無ければ`ollama pull`するか
# OLLAMA_CHAT_MODEL環境変数で別モデルを指定する。
CHAT_MODEL = os.environ.get("OLLAMA_CHAT_MODEL", "elyza:8b")
# デフォルトのTOP_K。
# 本来は4程度が検索精度の目安だが、CPU推論のOllamaではコンテキスト長が
# 応答速度に大きく影響するため、ローカル検証環境では1に固定している
# （TOP_K=2でも実用速度にならないことを確認済み）。
# GPU環境やクラウドLLM APIに切り替える場合は、ここを4程度に戻すことを推奨。
DEFAULT_TOP_K = 1

DOCS_DIR = os.environ.get("DOCS_DIR", "docs")
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 150
EMBED_BATCH_SIZE = 20
MAX_RETRIES = 3
