import type { DocumentInfo } from "../api/types";

interface Props {
  documents: DocumentInfo[];
  onDelete: (id: string) => void;
  onReindex: (id: string) => void;
  indexingId: string | null;
}

const STATUS_BADGE: Record<DocumentInfo["status"], string> = {
  pending: "bg-amber-100 text-amber-800",
  indexed: "bg-green-100 text-green-800",
  failed: "bg-red-100 text-red-800",
};

export default function DocumentList({
  documents,
  onDelete,
  onReindex,
  indexingId,
}: Props) {
  if (documents.length === 0) {
    return (
      <p className="rounded-xl border border-dashed border-slate-200 bg-white p-6 text-center text-sm text-slate-500">
        아직 자료가 없습니다. 파일을 드래그하거나 메모를 추가하세요.
      </p>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl border border-slate-200 bg-white">
      <table className="w-full text-left text-sm">
        <thead className="bg-slate-50 text-xs uppercase text-slate-500">
          <tr>
            <th className="px-4 py-3">제목</th>
            <th className="px-4 py-3">유형</th>
            <th className="px-4 py-3">상태</th>
            <th className="px-4 py-3">청크</th>
            <th className="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {documents.map((doc) => (
            <tr key={doc.id} className="hover:bg-slate-50">
              <td className="px-4 py-3 font-medium">{doc.title}</td>
              <td className="px-4 py-3 text-slate-600">{doc.source_type}</td>
              <td className="px-4 py-3">
                <span
                  className={`inline rounded-full px-2 py-0.5 text-xs ${STATUS_BADGE[doc.status]}`}
                >
                  {doc.status}
                </span>
                {doc.error && (
                  <p className="mt-1 text-xs text-red-600">{doc.error}</p>
                )}
              </td>
              <td className="px-4 py-3">{doc.chunk_count || "—"}</td>
              <td className="px-4 py-3 text-right">
                {doc.status !== "indexed" && (
                  <button
                    type="button"
                    disabled={indexingId === doc.id}
                    onClick={() => onReindex(doc.id)}
                    className="mr-2 text-xs text-blue-600 hover:underline disabled:opacity-50"
                  >
                    인덱싱
                  </button>
                )}
                <button
                  type="button"
                  onClick={() => onDelete(doc.id)}
                  className="text-xs text-red-600 hover:underline"
                >
                  삭제
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
