from __future__ import annotations

from typing import List

from project_agent.ingest.pipeline import IngestPipeline
from project_agent.index.vector_store import VectorIndex
from project_agent.models.schemas import DocumentInfo, IndexResult
from project_agent.storage.project_store import ProjectStore


class IndexService:
    def __init__(self) -> None:
        self.store = ProjectStore()
        self.ingest = IngestPipeline(self.store)
        self.vector = VectorIndex()

    def index_document(self, project_id: str, document_id: str) -> IndexResult:
        doc = self.store.get_document(project_id, document_id)
        if doc is None:
            raise ValueError("Document not found")
        if doc.status == "failed":
            raise ValueError(doc.error or "Document ingestion failed")

        chunks = self.ingest.load_chunks_for_document(project_id, doc)
        if not chunks:
            doc.status = "failed"
            doc.error = "No chunks produced"
            self.store.update_document(project_id, doc)
            raise ValueError("No chunks produced")

        try:
            count = self.vector.index_document(project_id, doc, chunks)
            doc.status = "indexed"
            doc.chunk_count = count
            doc.error = None
            self.store.update_document(project_id, doc)
            return IndexResult(document_id=document_id, chunk_count=count, status="indexed")
        except Exception as e:
            doc.status = "failed"
            doc.error = str(e)
            self.store.update_document(project_id, doc)
            raise

    def index_all_pending(self, project_id: str) -> List[IndexResult]:
        results: List[IndexResult] = []
        for doc in self.store.list_documents(project_id):
            if doc.status in ("pending", "failed"):
                try:
                    results.append(self.index_document(project_id, doc.id))
                except Exception:
                    continue
        return results

    def remove_document_index(self, project_id: str, document_id: str) -> None:
        self.vector.delete_document(project_id, document_id)
