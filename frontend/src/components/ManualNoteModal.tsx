import { FormEvent, useState } from "react";

interface Props {
  open: boolean;
  onClose: () => void;
  onSubmit: (title: string, content: string, tags: string[]) => Promise<void>;
}

export default function ManualNoteModal({ open, onClose, onSubmit }: Props) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [tagsRaw, setTagsRaw] = useState("");
  const [loading, setLoading] = useState(false);

  if (!open) return null;

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!title.trim() || !content.trim()) return;
    setLoading(true);
    try {
      const tags = tagsRaw
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean);
      await onSubmit(title.trim(), content.trim(), tags);
      setTitle("");
      setContent("");
      setTagsRaw("");
      onClose();
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
      <div className="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-xl bg-white p-6 shadow-xl">
        <h2 className="text-lg font-semibold">메모 추가</h2>
        <form onSubmit={handleSubmit} className="mt-4 space-y-3">
          <input
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            placeholder="제목"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          <textarea
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            rows={8}
            placeholder="내용"
            value={content}
            onChange={(e) => setContent(e.target.value)}
          />
          <input
            className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm"
            placeholder="태그 (쉼표 구분)"
            value={tagsRaw}
            onChange={(e) => setTagsRaw(e.target.value)}
          />
          <div className="flex justify-end gap-2">
            <button type="button" onClick={onClose} className="px-4 py-2 text-sm text-slate-600">
              취소
            </button>
            <button
              type="submit"
              disabled={loading}
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm text-white disabled:opacity-50"
            >
              {loading ? "저장 중…" : "추가 후 인덱싱"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
