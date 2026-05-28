import type { QueueItem } from "../hooks/useUploadQueue";

const STATUS_LABEL: Record<QueueItem["status"], string> = {
  queued: "대기",
  uploading: "업로드 중",
  ingested: "파싱 완료",
  indexing: "인덱싱 중",
  indexed: "완료",
  failed: "실패",
};

interface Props {
  items: QueueItem[];
  onRetry: (id: string) => void;
  onClear: () => void;
}

export default function UploadQueueList({ items, onRetry, onClear }: Props) {
  if (items.length === 0) return null;

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <div className="mb-2 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-slate-800">업로드 큐 ({items.length})</h3>
        <button
          type="button"
          onClick={onClear}
          className="text-xs text-slate-500 hover:text-slate-800"
        >
          완료 항목 지우기
        </button>
      </div>
      <ul className="max-h-48 space-y-2 overflow-y-auto">
        {items.map((item) => (
          <li
            key={item.id}
            className="flex items-start justify-between gap-2 rounded-lg bg-slate-50 px-3 py-2 text-sm"
          >
            <div className="min-w-0 flex-1">
              <p className="truncate font-medium">{item.file.name}</p>
              <p className="text-xs text-slate-500">
                {STATUS_LABEL[item.status]}
                {item.chunkCount != null ? ` · ${item.chunkCount} chunks` : ""}
              </p>
              {item.error && <p className="text-xs text-red-600">{item.error}</p>}
            </div>
            {item.status === "failed" && (
              <button
                type="button"
                onClick={() => onRetry(item.id)}
                className="shrink-0 text-xs text-blue-600 hover:underline"
              >
                재시도
              </button>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}
