const API_BASE = import.meta.env.VITE_API_BASE ?? "";

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public body: unknown
  ) {
    super(message);
  }
}

export async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, options);
  const text = await res.text();
  let data: unknown = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = text;
    }
  }
  if (!res.ok) {
    let detail = res.statusText;
    if (typeof data === "object" && data && "detail" in data) {
      const raw = (data as { detail: unknown }).detail;
      // FastAPI 422 validation error는 배열 형태
      if (Array.isArray(raw)) {
        detail = raw
          .map((e: { msg?: string; loc?: unknown }) => `${e.loc ? JSON.stringify(e.loc) : ""}: ${e.msg ?? ""}`)
          .join("; ");
      } else {
        detail = String(raw);
      }
    }
    throw new ApiError(detail, res.status, data);
  }
  return data as T;
}
