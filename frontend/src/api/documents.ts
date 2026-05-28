import { apiFetch } from "./client";
import type { DocumentInfo } from "./types";

export function listDocuments(projectId: string): Promise<DocumentInfo[]> {
  return apiFetch(`/projects/${projectId}/documents`);
}

export async function uploadDocument(
  projectId: string,
  file: File,
  title?: string
): Promise<DocumentInfo> {
  const form = new FormData();
  form.append("file", file, file.name);
  const qs = title ? `?title=${encodeURIComponent(title)}` : "";
  const base = import.meta.env.VITE_API_BASE ?? "";
  const url = `${base}/projects/${projectId}/documents/upload${qs}`;

  console.log("[uploadDocument]", file.name, file.size, file.type, "→", url);

  const res = await fetch(url, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const data = await res.json();
      if (Array.isArray(data?.detail)) {
        detail = data.detail
          .map((e: { msg?: string; loc?: unknown }) =>
            `${e.loc ? JSON.stringify(e.loc) : ""}: ${e.msg ?? ""}`)
          .join("; ");
      } else if (data?.detail) {
        detail = String(data.detail);
      }
    } catch { /* ignore */ }
    throw new Error(`Upload failed (${res.status}): ${detail}`);
  }

  return res.json();
}

export function createManualNote(
  projectId: string,
  body: { title: string; content: string; tags?: string[] }
): Promise<DocumentInfo> {
  return apiFetch(`/projects/${projectId}/documents/manual`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export function indexDocument(
  projectId: string,
  documentId: string
): Promise<{ document_id: string; chunk_count: number; status: string }> {
  return apiFetch(`/projects/${projectId}/documents/${documentId}/index`, {
    method: "POST",
  });
}

export function indexAll(projectId: string): Promise<
  { document_id: string; chunk_count: number; status: string }[]
> {
  return apiFetch(`/projects/${projectId}/index`, { method: "POST" });
}

export function deleteDocument(
  projectId: string,
  documentId: string
): Promise<{ deleted: boolean }> {
  return apiFetch(`/projects/${projectId}/documents/${documentId}`, {
    method: "DELETE",
  });
}
