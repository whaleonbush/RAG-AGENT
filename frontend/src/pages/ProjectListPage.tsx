import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { createProject, listProjects } from "../api/projects";
import type { Project } from "../api/types";
import CreateProjectModal from "../components/CreateProjectModal";

export default function ProjectListPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await listProjects();
      setProjects(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "목록 로드 실패");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <div className="mx-auto max-w-4xl px-4 py-10">
      <header className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">과제 지식 에이전트</h1>
          <p className="mt-1 text-sm text-slate-500">
            과제별로 자료를 모아 AI 검색·질의응답합니다
          </p>
        </div>
        <button
          type="button"
          onClick={() => setModalOpen(true)}
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          + 새 과제
        </button>
      </header>

      {error && (
        <p className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>
      )}

      <div className="mt-8">
        {loading && <p className="text-sm text-slate-500">불러오는 중…</p>}
        {!loading && projects.length === 0 && (
          <p className="rounded-xl border border-dashed border-slate-300 bg-white p-10 text-center text-slate-500">
            과제가 없습니다. 새 과제를 만들어 시작하세요.
          </p>
        )}
        <ul className="grid gap-4 sm:grid-cols-2">
          {projects.map((p) => (
            <li key={p.id}>
              <Link
                to={`/projects/${p.id}`}
                className="block rounded-xl border border-slate-200 bg-white p-5 shadow-sm transition hover:border-blue-300 hover:shadow-md"
              >
                <h2 className="font-semibold text-slate-900">{p.name}</h2>
                {p.description && (
                  <p className="mt-1 line-clamp-2 text-sm text-slate-600">{p.description}</p>
                )}
                <p className="mt-3 text-xs text-slate-400">
                  {new Date(p.created_at).toLocaleString("ko-KR")}
                </p>
              </Link>
            </li>
          ))}
        </ul>
      </div>

      <CreateProjectModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onCreate={async (name, description) => {
          await createProject(name, description);
          await load();
        }}
      />
    </div>
  );
}
