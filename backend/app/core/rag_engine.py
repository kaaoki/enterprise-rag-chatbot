"""
RAGチャットボットのコアロジック（Streamlit非依存）。

検索・コンテキスト構築のロジックはGemini版から変更なし。
埋め込み・回答生成の呼び出し先だけを、Ollama（ローカルLLM）に差し替えている。
"""

from app.core.config import DEFAULT_TOP_K
from app.core.ollama_client import chat_completion, embed_texts

ANSWER_PROMPT_TEMPLATE = """\
あなたは、与えられた資料の内容だけをもとに回答するアシスタントです。
以下の「参考資料」に書かれている情報のみを根拠として、質問に日本語で答えてください。

- 参考資料に答えが含まれていない場合は、正直に「資料の中に該当する情報が見つかりませんでした」と答えてください。憶測で答えを作らないでください。
- 可能であれば、回答の根拠となった資料名にも触れてください。

--- 参考資料 ---
{context}
--- 参考資料ここまで ---

質問: {question}
"""


def embed_query(query: str) -> list[float]:
    return embed_texts([query])[0]


def retrieve(collection, query_embedding: list[float], top_k: int = DEFAULT_TOP_K):
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    return list(zip(documents, metadatas))


def build_context(retrieved_chunks) -> str:
    parts = []
    for i, (doc, meta) in enumerate(retrieved_chunks, start=1):
        source = meta.get("source", "不明な資料")
        parts.append(f"[資料{i}: {source}]\n{doc}")
    return "\n\n".join(parts)


def generate_answer(question: str, context: str) -> str:
    prompt = ANSWER_PROMPT_TEMPLATE.format(context=context, question=question)
    return chat_completion(prompt)


def answer_question(collection, question: str, top_k: int = DEFAULT_TOP_K) -> tuple[str, list[str]]:
    """
    /api/chat から呼び出す一連の処理（検索→コンテキスト構築→回答生成）をまとめたヘルパー。
    """
    query_embedding = embed_query(question)
    retrieved = retrieve(collection, query_embedding, top_k=top_k)
    context = build_context(retrieved)
    answer = generate_answer(question, context)
    used_sources = sorted({meta.get("source", "不明") for _, meta in retrieved})
    return answer, used_sources
