from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from project_agent.config import get_settings
from project_agent.ingest.chunker import chunk_text
from project_agent.ingest.normalize import build_markdown, extract_body
from project_agent.ingest.parsers import parse_file
from project_agent.models.schemas import DocumentInfo
from project_agent.storage.project_store import ProjectStore


class IngestPipeline:
    def __init__(self, store: Optional[ProjectStore] = None) -> None:
        self.store = store or ProjectStore()
        self.settings = get_settings()

    def ingest_file(
        self,
        project_id: str,
        *,
        file_path: Path,
        original_filename: str,
        title: Optional[str] = None,
    ) -> DocumentInfo:
        doc = self.store.add_document(
            project_id,
            title=title or original_filename,
            source_type="file",
            original_filename=original_filename,
        )
        dest = self.store.original_path(project_id, doc.id, original_filename)
        dest.write_bytes(file_path.read_bytes())

        try:
            body = parse_file(dest)
            if not body.strip():
                raise ValueError("No extractable text in file")
            md = build_markdown(
                project_id=project_id,
                document_id=doc.id,
                title=doc.title,
                source_type="file",
                source_name=original_filename,
                body=body,
            )
            out = self.store.processed_markdown_path(project_id, doc.id)
            out.write_text(md, encoding="utf-8")
            doc.status = "pending"
        except Exception as e:
            doc.status = "failed"
            doc.error = str(e)
        self.store.update_document(project_id, doc)
        return doc

    def ingest_manual(
        self,
        project_id: str,
        *,
        title: str,
        content: str,
        tags: Optional[List[str]] = None,
    ) -> DocumentInfo:
        doc = self.store.add_document(
            project_id,
            title=title,
            source_type="manual",
            original_filename=None,
        )
        try:
            md = build_markdown(
                project_id=project_id,
                document_id=doc.id,
                title=title,
                source_type="manual",
                source_name=title,
                body=content,
                tags=tags,
            )
            out = self.store.processed_markdown_path(project_id, doc.id)
            out.write_text(md, encoding="utf-8")
            doc.status = "pending"
        except Exception as e:
            doc.status = "failed"
            doc.error = str(e)
        self.store.update_document(project_id, doc)
        return doc

    def load_chunks_for_document(self, project_id: str, document: DocumentInfo) -> list:
        path = self.store.processed_markdown_path(project_id, document.id)
        if not path.is_file():
            return []
        md = path.read_text(encoding="utf-8")
        meta, body = extract_body(md)
        chunks = chunk_text(
            body,
            chunk_size=self.settings.chunk_size,
            overlap=self.settings.chunk_overlap,
        )
        for c in chunks:
            c.text = f"Title: {meta.get('title', document.title)}\n\n{c.text}"
        return chunks
