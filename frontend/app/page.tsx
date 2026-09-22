"use client";

import { useEffect, useState } from "react";
import ChatWindow from "@/components/ChatWindow";
import SourcePanel from "@/components/SourcePanel";
import TopKControl from "@/components/TopKControl";
import { fetchDocuments, postChat } from "@/lib/api";
import type { ChatMessage } from "@/lib/types";

export default function Home() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [topK, setTopK] = useState(1); // CPU推論のOllamaでは1が実用速度の目安
  const [sources, setSources] = useState<string[]>([]);
  const [sourcesLoading, setSourcesLoading] = useState(true);
  const [sourcesError, setSourcesError] = useState<string | null>(null);
  const [isSending, setIsSending] = useState(false);

  useEffect(() => {
    fetchDocuments()
      .then((res) => setSources(res.sources))
      .catch((err) =>
        setSourcesError(err instanceof Error ? err.message : "資料一覧の取得に失敗しました")
      )
      .finally(() => setSourcesLoading(false));
  }, []);

  async function handleSend(question: string) {
    setMessages((prev) => [...prev, { role: "user", content: question }]);
    setIsSending(true);
    try {
      const res = await postChat(question, topK);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.answer, sources: res.sources },
      ]);
    } catch (err) {
      const message = err instanceof Error ? err.message : "回答の生成に失敗しました。";
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: `エラーが発生しました: ${message}` },
      ]);
    } finally {
      setIsSending(false);
    }
  }

  return (
    <main className="mx-auto flex min-h-screen max-w-5xl flex-col px-6 py-10">
      <header className="mb-8 flex flex-wrap items-end justify-between gap-4 border-b border-line pb-6">
        <div>
          <p className="text-xs tracking-wide text-kraft">Enterprise RAG Chatbot</p>
          <h1 className="mt-1 font-serif text-2xl text-ink">登録文書Q&amp;Aチャットボット</h1>
        </div>
        <div className="flex flex-col items-end gap-1">
          <TopKControl value={topK} onChange={setTopK} />
          <p className="text-[11px] text-ink/45">
            ローカルLLM（CPU推論）のため、1〜2を推奨
          </p>
        </div>
      </header>

      <div className="flex flex-1 flex-col gap-8 md:flex-row">
        <ChatWindow messages={messages} onSend={handleSend} isSending={isSending} />
        <SourcePanel sources={sources} isLoading={sourcesLoading} error={sourcesError} />
      </div>
    </main>
  );
}
