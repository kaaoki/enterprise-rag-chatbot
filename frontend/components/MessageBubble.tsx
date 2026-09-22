import type { ChatMessage } from "@/lib/types";

export default function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={
          isUser
            ? "max-w-[80%] rounded-sm bg-ink/[0.06] px-4 py-3 text-[15px] leading-relaxed text-ink"
            : "max-w-[80%] border-l-2 border-pine py-1 pl-4 text-[15px] leading-relaxed text-ink"
        }
      >
        <p className="whitespace-pre-wrap">{message.content}</p>
        {message.sources && message.sources.length > 0 && (
          <p className="mt-2 text-xs text-kraft">参照: {message.sources.join("、")}</p>
        )}
      </div>
    </div>
  );
}
