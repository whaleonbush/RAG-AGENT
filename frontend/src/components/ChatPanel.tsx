import { FormEvent, useState } from "react";
import { sendChat } from "../api/chat";
import type { Citation } from "../api/types";

interface Message {
  role: "user" | "assistant";
  text: string;
  citations?: Citation[];
  usedOllama?: boolean;
}

interface Props {
  projectId: string;
}

export default function ChatPanel({ projectId }: Props) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const q = input.trim();
    if (!q || loading) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", text: q }]);
    setLoading(true);
    try {
      const res = await sendChat(projectId, q);
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          text: res.answer,
          citations: res.citations,
          usedOllama: res.used_ollama,
        },
      ]);
    } catch (err) {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          text: err instanceof Error ? err.message : "질문 처리 실패",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex h-full min-h-[420px] flex-col rounded-xl border border-slate-200 bg-white">
      <div className="border-b border-slate-100 px-4 py-3">
        <h2 className="font-semibold text-slate-800">AI 질문</h2>
        <p className="text-xs text-slate-500">업로드·인덱싱된 자료만 근거로 답변합니다</p>
      </div>

      <div className="flex-1 space-y-3 overflow-y-auto p-4">
        {messages.length === 0 && (
          <p className="text-center text-sm text-slate-400">
            예: 정격 전압이 얼마야?
          </p>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`rounded-lg px-3 py-2 text-sm ${
              msg.role === "user"
                ? "ml-8 bg-blue-600 text-white"
                : "mr-8 bg-slate-100 text-slate-800"
            }`}
          >
            <p className="whitespace-pre-wrap">{msg.text}</p>
            {msg.role === "assistant" && msg.usedOllama != null && (
              <p className="mt-1 text-xs opacity-70">
                {msg.usedOllama ? "LLM 연결됨" : "검색 요약 모드"}
              </p>
            )}
            {msg.citations && msg.citations.length > 0 && (
              <div className="mt-2 space-y-1 border-t border-slate-200 pt-2">
                <p className="text-xs font-medium opacity-80">출처</p>
                {msg.citations.map((c, j) => (
                  <div key={j} className="rounded bg-white/60 p-2 text-xs">
                    <span className="font-medium">{c.title}</span>
                    {c.page != null && c.page > 0 && (
                      <span className="text-slate-500"> · p.{c.page}</span>
                    )}
                    <p className="mt-0.5 line-clamp-2 text-slate-600">{c.excerpt}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && (
          <p className="text-center text-sm text-slate-400">검색 중…</p>
        )}
      </div>

      <form onSubmit={handleSubmit} className="border-t border-slate-100 p-3">
        <div className="flex gap-2">
          <input
            className="flex-1 rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
            placeholder="질문 입력…"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            전송
          </button>
        </div>
      </form>
    </div>
  );
}
