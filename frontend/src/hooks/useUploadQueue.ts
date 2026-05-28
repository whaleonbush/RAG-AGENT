import { useCallback, useState } from "react";
import { indexDocument, uploadDocument } from "../api/documents";
import { SUPPORTED_EXTENSIONS } from "../api/types";

export type QueueStatus =
  | "queued"
  | "uploading"
  | "ingested"
  | "indexing"
  | "indexed"
  | "failed";

export interface QueueItem {
  id: string;
  file: File;
  status: QueueStatus;
  error?: string;
  documentId?: string;
  chunkCount?: number;
}

function isSupported(file: File): boolean {
  const name = file.name.toLowerCase();
  return SUPPORTED_EXTENSIONS.some((ext) => name.endsWith(ext));
}

export function useUploadQueue(
  projectId: string,
  autoIndex: boolean,
  onComplete?: () => void
) {
  const [items, setItems] = useState<QueueItem[]>([]);

  const updateItem = useCallback((id: string, patch: Partial<QueueItem>) => {
    setItems((prev) => prev.map((it) => (it.id === id ? { ...it, ...patch } : it)));
  }, []);

  const processOne = useCallback(
    async (item: QueueItem) => {
      try {
        updateItem(item.id, { status: "uploading", error: undefined });
        const doc = await uploadDocument(projectId, item.file);
        updateItem(item.id, {
          status: "ingested",
          documentId: doc.id,
        });

        if (autoIndex) {
          updateItem(item.id, { status: "indexing" });
          const result = await indexDocument(projectId, doc.id);
          updateItem(item.id, {
            status: "indexed",
            chunkCount: result.chunk_count,
          });
        } else {
          updateItem(item.id, { status: "indexed" });
        }
      } catch (e) {
        const msg = e instanceof Error ? e.message : "업로드 실패";
        updateItem(item.id, { status: "failed", error: msg });
      }
    },
    [projectId, autoIndex, updateItem]
  );

  const addFiles = useCallback(
    async (files: File[]) => {
      const valid = files.filter(isSupported);
      const rejected = files.length - valid.length;
      if (valid.length === 0) {
        return { added: 0, rejected };
      }

      const newItems: QueueItem[] = valid.map((file) => ({
        id: `${file.name}-${file.size}-${Date.now()}-${Math.random()}`,
        file,
        status: "queued" as const,
      }));

      setItems((prev) => [...newItems, ...prev]);

      for (const item of newItems) {
        await processOne(item);
      }

      onComplete?.();
      return { added: valid.length, rejected };
    },
    [processOne, onComplete]
  );

  const retry = useCallback(
    (id: string) => {
      const item = items.find((i) => i.id === id);
      if (item) void processOne(item);
    },
    [items, processOne]
  );

  const clearDone = useCallback(() => {
    setItems((prev) => prev.filter((i) => i.status !== "indexed" && i.status !== "failed"));
  }, []);

  return { items, addFiles, retry, clearDone };
}
