# Enterprise RAG Chatbot — Backend (FastAPI + Ollama)

既存のStreamlit版RAGデモ（[RAG-Document-QA-Chatbot](https://github.com/kaaoki/RAG-Document-QA-Chatbot)）の
検索・回答生成ロジックを、FastAPIによるREST API構成に移植したバックエンドです。
埋め込み・生成にはGemini APIではなく、**Ollama（ローカルLLM）** を使用しています
（病院向け患者管理支援ツールと同じ構成）。

## Gemini版からの変更点

開発中、Google AI Studioで新規発行されるAPIキーが`AQ.`形式のみとなり、
`401 UNAUTHENTICATED — ACCESS_TOKEN_TYPE_UNSUPPORTED`エラーが解消しない
既知の不具合に遭遇したため、Ollama（ローカルLLM）に切り替えた。

| 項目 | Gemini版 | 本バージョン（Ollama版） |
|---|---|---|
| 埋め込み | Gemini Embedding API | Ollama `/api/embed`（デフォルト: `bge-m3`） |
| 生成 | Gemini API (`gemini-3.6-flash`) | Ollama `/api/chat`（デフォルト: `elyza:8b`） |
| 認証 | APIキー必須 | 不要（ローカル動作） |
| 外部依存 | `google-genai` | なし（`requests`でOllamaのHTTP APIを直接呼ぶ） |

## 事前準備（Ollama）

```bash
# Ollama自体は https://ollama.com/ からインストール済みであることを前提とする

# 埋め込み用モデル（多言語対応、日本語資料にも対応）
ollama pull bge-m3

# 生成用モデル（病院案件と同じELYZA-JP-8Bを想定。別モデルでもよい）
ollama pull elyza:8b   # 既に取得済みならスキップ

# Ollamaサーバーが起動していることを確認
ollama list
```

生成用に別のモデルを使う場合は、`OLLAMA_CHAT_MODEL`環境変数で上書きできる。

## セットアップ

```bash
pip install -r requirements.txt
```

## 起動

```bash
python -m uvicorn app.main:app --reload
```

`http://127.0.0.1:8000/docs` でSwagger UIが開き、APIを直接試せる。

## エンドポイント

- `GET /health` : ヘルスチェック
- `POST /api/chat` : `{"question": "...", "top_k": 4}` → `{"answer": "...", "sources": [...]}`
- `GET /api/documents` : 登録済み資料の一覧
- `POST /api/documents/ingest` : `docs/` フォルダ配下のPDFを取り込み（`DOCS_DIR`環境変数で変更可）

Ollamaに接続できない場合、`/api/chat`と`/api/documents/ingest`は`502 Bad Gateway`を返す
（`app/core/ollama_client.py`の`OllamaError`をハンドリング）。

## 環境変数（すべて省略可、デフォルトあり）

| 変数名 | デフォルト | 説明 |
|---|---|---|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollamaサーバーのアドレス |
| `OLLAMA_EMBEDDING_MODEL` | `bge-m3` | 埋め込みモデル名 |
| `OLLAMA_CHAT_MODEL` | `elyza:8b` | 生成モデル名 |
| `CHROMA_DB_DIR` | `chroma_db` | ベクトルDBの保存先 |
| `DOCS_DIR` | `docs` | 取り込み対象PDFのフォルダ |

## テスト

```bash
python -m pytest -v
```

Ollamaサーバーの実体は使わず、`unittest.mock`でモックに差し替えてテストしている
（Ollama未起動でも実行可能。通信失敗時の502エラー・リトライ処理のテストも含む）。

## 今後

- `frontend/`（Next.js）からこのAPIを呼び出すチャットUIは実装済み
- Azure（App Service, Cosmos DB）へのデプロイ、Terraformによる構成管理は次フェーズで検証
- 面接で問われた場合: 「クラウドLLM APIのアカウント側不具合に遭遇し、ローカルLLMに切り替えて開発を継続した」という判断の経緯として説明できる
