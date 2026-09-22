# エンタープライズ向けRAGチャットボット（FastAPI + Next.js）

指定した資料（PDF）の内容だけを根拠に回答する、RAG（検索拡張生成）構成のチャットボットです。
以前作成したStreamlit版RAGデモ（[RAG-Document-QA-Chatbot](https://github.com/kaaoki/RAG-Document-QA-Chatbot)）の検索・生成ロジックをベースに、
エンタープライズ向けRAGチャットボット開発案件（必須スキル: Python/RESTful API/Pytest、または Next.js/React）を想定して、
FastAPI + Next.js/React構成に発展させたものです。

## 背景・課題

案件の必須スキルが「バックエンド(Python/FastAPI/Pytest)」「フロントエンド(Next.js/React)」のいずれかだったため、
既存のStreamlit一体型のRAGロジックを、REST API（バックエンド）とUI（フロントエンド）に分離し、
Pytestによるテストも整備した。

開発途中、埋め込み・生成に使っていたGoogle Gemini APIで、AI Studio発行の新形式APIキー（`AQ.`から始まる形式）が
`401 UNAUTHENTICATED — ACCESS_TOKEN_TYPE_UNSUPPORTED`エラーを返す既知の不具合に遭遇したため、
**Ollama（ローカルLLM）に切り替えて開発を継続した**。これにより、クラウドLLM APIのアカウント側障害に対する
設計判断（オンプレミス/ローカルLLMへの切り替えやすさ）を実地で経験する形になった。

## できること

- 登録したPDF資料の内容だけを根拠に、チャット形式で質問に回答（資料に無い内容は「わからない」と正直に回答）
- 回答の根拠となった資料名を表示
- 検索するチャンク数（TOP_K）を調整可能
- REST API化（`POST /api/chat`, `GET /api/documents`, `POST /api/documents/ingest`）
- Pytestによるテスト（Ollama・ChromaDBはモックに差し替え、APIキーやモデル無しでも実行可能）

## 構成

```
enterprise-rag-chatbot/
├── backend/    # FastAPI（Python）。詳細は backend/README.md 参照
└── frontend/   # Next.js / React / TypeScript。詳細は frontend/README.md 参照
```

## 使用技術

| 分類 | 使用技術 |
|---|---|
| バックエンド | Python, FastAPI, Pytest |
| フロントエンド | TypeScript, Next.js (App Router), React, Tailwind CSS |
| LLM / 埋め込み | Ollama（ローカルLLM）: `elyza:8b`（生成）, `bge-m3`（埋め込み） |
| ベクトルDB | Chroma（ローカル永続化） |
| PDF読み込み | `pypdf` |

## セットアップ

`backend/README.md` と `frontend/README.md` にそれぞれの詳細な手順を記載している。概要は以下の通り。

```bash
# 1. Ollamaにモデルを準備
ollama pull bge-m3
ollama pull elyza:8b

# 2. バックエンド起動
cd backend
pip install -r requirements.txt
python -m pytest -v          # 16件のテストが通ることを確認
python -m uvicorn app.main:app --reload

# 3. フロントエンド起動（別ターミナル）
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

`http://localhost:3000` を開くとチャット画面が表示される（`docs/` フォルダにPDFを配置し、`POST /api/documents/ingest`で取り込んでおく必要がある）。

## 設計上の工夫

1. **ロジックとUI/APIの分離**: 検索・回答生成のコアロジック（`app/core/rag_engine.py`, `ingestion.py`）はUIフレームワークに依存しない純粋関数として実装し、FastAPI経由でもテストからも同じ関数を呼び出せる設計にしている
2. **外部LLMプロバイダの切り替えやすさ**: Gemini→Ollamaへの切り替えを、`app/core/ollama_client.py`にAPI呼び出しを集約することで、他のロジックにほぼ手を入れずに実施できた
3. **CPU推論を前提にしたパラメータ調整**: GPU無しのローカル環境では、プロンプトに渡すコンテキスト量（TOP_K・チャンクサイズ）が応答速度に大きく影響することを確認し、デフォルトのTOP_Kを1に調整した（GPU環境やクラウドLLM APIに戻す場合は4程度が目安）
4. **テストの外部依存排除**: OllamaサーバーやChromaDBの実体を使わず、`unittest.mock`でモックに差し替えることで、モデルやAPIキーが無い環境でもCI等で実行可能なテストにしている

## 動作検証・トラブルシューティングの記録

- **Gemini APIキー(`AQ.`形式)の401エラー**: Google AI Studio側の既知の不具合と判断し、Ollamaへ切り替えて解決
- **フロントエンドからのCORSエラー**: FastAPI側に`CORSMiddleware`が未設定だったため`Failed to fetch`が発生。`localhost:3000`を許可オリジンに追加して解決
- **CPU推論での応答速度**: TOP_K=4だと1回の応答に5分以上かかったが、TOP_K=1に下げることで実用速度まで改善することを確認

## 今後の拡張案

- Azure（App Service, Cosmos DB）へのデプロイ、Terraformによる構成管理の検証
- GPU環境や、クラウドLLM API（Gemini/OpenAI等）への切り替えによる高速化
- マルチターンでの会話履行、複数フォーマット対応（Word/Excel等）

## 免責事項

本アプリは学習・ポートフォリオ目的で作成したものです。実際の業務利用にあたっては、生成AIの回答を鵜呑みにせず、必ず一次資料を確認することを前提としています。
