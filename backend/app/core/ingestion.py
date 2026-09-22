"""
文書取り込みロジック（Streamlit非依存）。

PDF読み込み・チャンク分割はGemini版から変更なし。
埋め込みの呼び出し先だけを、Ollama（ローカルLLM）に差し替えている。
"""

import os

from pypdf import PdfReader

from app.core.config import CHUNK_OVERLAP, CHUNK_SIZE, DOCS_DIR, EMBED_BATCH_SIZE
from app.core.ollama_client import embed_texts


def load_pdf_text(file_path: str) -> str:
    reader = PdfReader(file_path)
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            pages.append(text)
    return "\n".join(pages)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """シンプルな文字数ベースのチャンク分割（形態素解析なし）"""
    chunks = []
    start = 0
    text_length = len(text)
    while start < text_length:
        end = min(start + chunk_size, text_length)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def ingest_documents(collection, docs_dir: str = DOCS_DIR) -> tuple[list[str], list[str], int]:
    """
    docs_dir 配下のPDFを取り込む。
    戻り値: (今回処理したファイル一覧, スキップしたファイル一覧, 追加した総チャンク数)
    """
    if not os.path.isdir(docs_dir):
        raise FileNotFoundError(f"{docs_dir} フォルダが見つかりません。")

    pdf_files = [f for f in sorted(os.listdir(docs_dir)) if f.lower().endswith(".pdf")]
    if not pdf_files:
        raise FileNotFoundError(f"{docs_dir} フォルダにPDFファイルがありません。")

    existing_sources = set()
    if collection.count() > 0:
        existing_meta = collection.get()["metadatas"]
        existing_sources = {m["source"] for m in existing_meta}

    processed_files: list[str] = []
    skipped_files: list[str] = []
    total_chunks = 0

    for file_name in pdf_files:
        if file_name in existing_sources:
            skipped_files.append(file_name)
            continue

        file_path = os.path.join(docs_dir, file_name)
        text = load_pdf_text(file_path)
        if not text.strip():
            # スキャンPDF等、テキスト抽出できなかったファイル
            skipped_files.append(file_name)
            continue

        chunks = chunk_text(text)

        for batch_start in range(0, len(chunks), EMBED_BATCH_SIZE):
            batch = chunks[batch_start : batch_start + EMBED_BATCH_SIZE]
            embeddings = embed_texts(batch)
            ids = [f"{file_name}_{batch_start + i}" for i in range(len(batch))]
            metadatas = [
                {"source": file_name, "chunk_index": batch_start + i} for i in range(len(batch))
            ]

            collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=batch,
                metadatas=metadatas,
            )

        processed_files.append(file_name)
        total_chunks += len(chunks)

    return processed_files, skipped_files, total_chunks
