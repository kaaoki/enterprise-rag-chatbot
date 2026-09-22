# Enterprise RAG Chatbot — Frontend (Next.js / React)

`backend/`(FastAPI)のAPIを呼び出すチャットUIです。Streamlit版のUIをNext.js + TypeScript + Tailwind CSSで再構築しています。

## デザインの方向性

「登録済みの資料だけを根拠に回答する」という本アプリの性質に合わせ、閲覧室・資料館のような落ち着いたトーンにしています。

- 配色: 紙色の背景(`paper`)+深いインク色の本文(`ink`)+操作色として深い松葉色(`pine`)、出典表示にはやや控えめな真鍮色(`kraft`)
- 出典（参照した資料名）は回答の下に脚注のように控えめに表示し、目立たせすぎない
- 見出しは明朝体（Noto Serif JP）、本文・UIはゴシック体（Noto Sans JP）で書体を使い分け

## セットアップ

```bash
npm install
cp .env.local.example .env.local
# .env.local の NEXT_PUBLIC_API_BASE_URL を、backendの起動先に合わせて設定
```

## 起動

```bash
npm run dev
```

`http://localhost:3000` を開くとチャット画面が表示されます。バックエンド(`backend/`)を先に起動しておく必要があります。

## 現状の制約(2026-09-22時点)

- `POST /api/documents/ingest` および `/api/chat` は、バックエンド側でGemini APIキーの認証エラー（`401 ACCESS_TOKEN_TYPE_UNSUPPORTED`、AI Studio発行のAQ.形式キーに関する既知の不具合）が発生しており、実際の回答生成はまだ確認できていません
- `GET /api/documents`（資料一覧表示）やUIの表示・入力自体は、バックエンドが起動していれば動作確認済みです
- Geminiキー問題が解消次第、`/api/chat`経由の実際の一問一答フローを確認する

## ビルド確認

```bash
npm run build
```

型チェック・ビルドとも成功することを確認済みです。

## 今後

- Azure（App Service）へのデプロイ、Terraformでの構成管理は次フェーズで検証予定
- `npm audit` で一部のNext.js関連の脆弱性（Next 16系でのみ完全に修正されるもの）が残っていますが、2025年12月の重大インシデント（RCE/DoS）については14系の最新パッチ（14.2.35）で対応済みです。実運用前にはNext 15/16系への移行を検討してください
