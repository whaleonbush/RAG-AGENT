import { apiFetch } from "./client";
import type { ChatResponse } from "./types";

export function sendChat(
  projectId: string,
  question: string,
  topK?: number
): Promise<ChatResponse> {
  return apiFetch(`/projects/${projectId}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, top_k: topK }),
  });
}
