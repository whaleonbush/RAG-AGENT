export interface Project {
  id: string;
  name: string;
  description: string;
  created_at: string;
}

export interface DocumentInfo {
  id: string;
  project_id: string;
  title: string;
  source_type: "file" | "manual";
  original_filename: string | null;
  status: "pending" | "indexed" | "failed";
  chunk_count: number;
  error: string | null;
  created_at: string;
}

export interface Citation {
  document_id: string;
  title: string;
  section: string | null;
  page: number | null;
  excerpt: string;
}

export interface ChatResponse {
  answer: string;
  citations: Citation[];
  used_ollama: boolean;
}

export const SUPPORTED_EXTENSIONS = [
  ".pdf",
  ".docx",
  ".xlsx",
  ".xlsm",
  ".txt",
  ".md",
  ".markdown",
  ".csv",
];
