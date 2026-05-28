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
  form.append("file", file);
  const qs = title ? `?title=${encodeURIComponent(title)}` : "";
  return apiFetch(`/projects/${projectId}/documents/upload${qs}`, {
    method: "POST",
    body: form,
  });
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
