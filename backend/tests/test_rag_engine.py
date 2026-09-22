"""
app/core/rag_engine.py と app/core/ingestion.py の単体テスト。
Ollama呼び出し（embed_texts, chat_completion）はモックに差し替える。
"""

from unittest.mock import MagicMock, patch

from app.core.ingestion import chunk_text
from app.core.rag_engine import answer_question, build_context, retrieve


def test_chunk_text_splits_long_text_with_overlap():
    text = "a" * 3000
    chunks = chunk_text(text, chunk_size=1000, overlap=100)
    assert len(chunks) > 1
    # オーバーラップにより、連続するチャンクの末尾が次のチャンクの先頭に含まれる
    assert chunks[0][-50:] in text


def test_chunk_text_short_text_returns_single_chunk():
    text = "短いテキストです。"
    chunks = chunk_text(text, chunk_size=1000, overlap=100)
    assert chunks == [text]


def test_build_context_formats_each_source():
    retrieved = [
        ("本文チャンク1", {"source": "sample_a.pdf"}),
        ("本文チャンク2", {"source": "sample_b.pdf"}),
    ]
    context = build_context(retrieved)
    assert "[資料1: sample_a.pdf]" in context
    assert "[資料2: sample_b.pdf]" in context
    assert "本文チャンク1" in context


def test_build_context_missing_source_falls_back_to_placeholder():
    retrieved = [("本文チャンク", {})]
    context = build_context(retrieved)
    assert "不明な資料" in context


def test_retrieve_zips_documents_and_metadata():
    mock_collection = MagicMock()
    mock_collection.query.return_value = {
        "documents": [["doc1", "doc2"]],
        "metadatas": [[{"source": "a.pdf"}, {"source": "b.pdf"}]],
    }
    result = retrieve(mock_collection, query_embedding=[0.1, 0.2], top_k=2)
    assert result == [("doc1", {"source": "a.pdf"}), ("doc2", {"source": "b.pdf"})]
    mock_collection.query.assert_called_once_with(query_embeddings=[[0.1, 0.2]], n_results=2)


@patch("app.core.rag_engine.chat_completion")
@patch("app.core.rag_engine.embed_texts")
def test_answer_question_returns_answer_and_sorted_unique_sources(mock_embed_texts, mock_chat_completion):
    mock_embed_texts.return_value = [[0.1, 0.2]]
    mock_chat_completion.return_value = "テスト回答"

    mock_collection = MagicMock()
    mock_collection.query.return_value = {
        "documents": [["chunk1", "chunk2"]],
        "metadatas": [[{"source": "b.pdf"}, {"source": "a.pdf"}]],
    }

    answer, sources = answer_question(mock_collection, "質問", top_k=2)

    assert answer == "テスト回答"
    assert sources == ["a.pdf", "b.pdf"]  # ソート済み・重複なしであることを確認
    mock_embed_texts.assert_called_once_with(["質問"])
