import { useCallback, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  createManualNote,
  deleteDocument,
  indexAll,
  indexDocument,
  listDocuments,
} from "../api/documents";
import { getProject } from "../api/projects";
import type { DocumentInfo, Project } from "../api/types";
import ChatPanel from "../components/ChatPanel";
import DocumentList from "../components/DocumentList";
import DropZone from "../components/DropZone";
import ManualNoteModal from "../components/ManualNoteModal";
import UploadQueueList from "../components/UploadQueueList";
import { useUploadQueue } from "../hooks/useUploadQueue";

export default function ProjectWorkspacePage() {
  const { projectId } = useParams<{ projectId: string }>();
  const [project, setProject] = useState<Project | null>(null);
  const [documents, setDocuments] = useState<DocumentInfo[]>([]);
  const [autoIndex, setAutoIndex] = useState(true);
  const [noteOpen, setNoteOpen] = useState(false);
  const [indexingId, setIndexingId] = useState<string | null>(null);
  const [bulkLoading, setBulkLoading] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const refreshDocs = useCallback(async () => {
    if (!projectId) return;
    const docs = await listDocuments(projectId);
    setDocuments(docs);
  }, [projectId]);

  const load = useCallback(async () => {
    if (!projectId) return;
    const [p, docs] = await Promise.all([
      getProject(projectId),
      listDocuments(projectId),
    ]);
    setProject(p);
    setDocuments(docs);
  }, [projectId]);

  useEffect(() => {
    void load();
  }, [load]);

  const { items, addFiles, retry, clearDone } = useUploadQueue(
    projectId ?? "",
    autoIndex,
    () => void refreshDocs()
  );

  if (!projectId) {
    return <p className="p-8">잘못된 경로입니다.</p>;
  }

  const pid = projectId;

  async function handleFiles(files: File[]) {
    const result = await addFiles(files);
    if (result && result.rejected > 0) {
      setToast(`지원하지 않는 파일 ${result.rejected}개 제외됨`);
      setTimeout(() => setToast(null), 4000);
    }
    await refreshDocs();
  }

  async function handleManual(title: string, content: string, tags: string[]) {
    const doc = await createManualNote(pid, { title, content, tags });
    setIndexingId(doc.id);
    try {
      await indexDocument(pid, doc.id);
      setToast("메모가 인덱싱되었습니다");
    } finally {
      setIndexingId(null);
      await refreshDocs();
      setTimeout(() => setToast(null), 3000);
    }
  }

  async function handleReindex(docId: string) {
    setIndexingId(docId);
    try {
      await indexDocument(pid, docId);
      await refreshDocs();
    } finally {
      setIndexingId(null);
    }
  }

  async function handleDelete(docId: string) {
    if (!confirm("이 자료를 삭제할까요?")) return;
    await deleteDocument(pid, docId);
    await refreshDocs();
  }

  async function handleIndexAll() {
    setBulkLoading(true);
    try {
      await indexAll(pid);
      await refreshDocs();
      setToast("전체 인덱싱 완료");
      setTimeout(() => setToast(null), 3000);
    } finally {
      setBulkLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-3 px-4 py-4">
          <div>
            <Link to="/" className="text-sm text-blue-600 hover:underline">
              ← 과제 목록
            </Link>
            <h1 className="mt-1 text-xl font-bold">{project?.name ?? "…"}</h1>
            {project?.description && (
              <p className="text-sm text-slate-500">{project.description}</p>
            )}
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <label className="flex items-center gap-2 text-sm text-slate-600">
              <input
                type="checkbox"
                checked={autoIndex}
                onChange={(e) => setAutoIndex(e.target.checked)}
              />
              업로드 후 자동 인덱싱
            </label>
            <button
              type="button"
              onClick={() => setNoteOpen(true)}
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm hover:bg-slate-50"
            >
              + 메모
            </button>
            <button
              type="button"
              onClick={() => void handleIndexAll()}
              disabled={bulkLoading}
              className="rounded-lg bg-slate-800 px-3 py-2 text-sm text-white hover:bg-slate-900 disabled:opacity-50"
            >
              {bulkLoading ? "인덱싱 중…" : "전체 인덱싱"}
            </button>
          </div>
        </div>
      </header>

      {toast && (
        <div className="fixed bottom-4 right-4 z-50 rounded-lg bg-slate-800 px-4 py-2 text-sm text-white shadow-lg">
          {toast}
        </div>
      )}

      <main className="mx-auto grid max-w-7xl gap-6 p-4 lg:grid-cols-2">
        <section className="space-y-4">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            자료
          </h2>
          <DropZone onFiles={(f) => void handleFiles(f)} />
          <UploadQueueList items={items} onRetry={retry} onClear={clearDone} />
          <DocumentList
            documents={documents}
            onDelete={(id) => void handleDelete(id)}
            onReindex={(id) => void handleReindex(id)}
            indexingId={indexingId}
          />
        </section>

        <section>
          <ChatPanel projectId={pid} />
        </section>
      </main>

      <ManualNoteModal
        open={noteOpen}
        onClose={() => setNoteOpen(false)}
        onSubmit={handleManual}
      />
    </div>
  );
}
