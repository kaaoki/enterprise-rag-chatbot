"use client";

import { useState, type FormEvent } from "react";
import MessageBubble from "@/components/MessageBubble";
import type { ChatMessage } from "@/lib/types";

type ChatWindowProps = {
  messages: ChatMessage[];
  onSend: (question: string) => void;
  isSending: boolean;
};

export default function ChatWindow({ messages, onSend, isSending }: ChatWindowProps) {
  const [input, setInput] = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const question = input.trim();
    if (!question || isSending) return;
    onSend(question);
    setInput("");
  }

  return (
    <div className="flex flex-1 flex-col">
      <div className="flex-1 space-y-5 overflow-y-auto pr-1" style={{ minHeight: "50vh" }}>
        {messages.length === 0 && (
          <p className="text-sm text-ink/60">
            登録済みの資料の内容についてご質問ください。資料に記載のない内容には「見つかりませんでした」と回答します。
          </p>
        )}
        {messages.map((message, i) => (
          <MessageBubble key={i} message={message} />
        ))}
        {isSending && <p className="text-sm text-ink/50">資料を検索して回答を作成しています…</p>}
      </div>

      <form onSubmit={handleSubmit} className="mt-6 flex gap-2 border-t border-line pt-4">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="資料の内容について質問してください"
          className="flex-1 rounded-sm border border-line bg-white px-3 py-2 text-sm text-ink outline-none focus:border-pine"
        />
        <button
          type="submit"
          disabled={isSending || !input.trim()}
          className="rounded-sm bg-pine px-4 py-2 text-sm text-white transition-colors hover:bg-pine-dark disabled:cursor-not-allowed disabled:opacity-50"
        >
          送信
        </button>
      </form>
    </div>
  );
}
