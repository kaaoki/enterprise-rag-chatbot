export type ChatApiResponse = {
  answer: string;
  sources: string[];
};

export type DocumentsApiResponse = {
  sources: string[];
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function fetchDocuments(): Promise<DocumentsApiResponse> {
  const res = await fetch(`${API_BASE_URL}/api/documents`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`資料一覧の取得に失敗しました (status: ${res.status})`);
  }
  return res.json();
}

export async function postChat(question: string, topK: number): Promise<ChatApiResponse> {
  const res = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, top_k: topK }),
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(`回答の生成に失敗しました (status: ${res.status})${detail ? `: ${detail}` : ""}`);
  }
  return res.json();
}
