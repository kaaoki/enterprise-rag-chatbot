export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  sources?: string[];
};
