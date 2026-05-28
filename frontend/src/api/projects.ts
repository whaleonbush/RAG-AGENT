import { apiFetch } from "./client";
import type { Project } from "./types";

export function listProjects(): Promise<Project[]> {
  return apiFetch("/projects");
}

export function createProject(name: string, description: string): Promise<Project> {
  return apiFetch("/projects", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, description }),
  });
}

export function getProject(projectId: string): Promise<Project> {
  return apiFetch(`/projects/${projectId}`);
}

export function deleteProject(projectId: string): Promise<{ deleted: boolean }> {
  return apiFetch(`/projects/${projectId}`, { method: "DELETE" });
}
