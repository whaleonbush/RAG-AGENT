from __future__ import annotations

from typing import Dict, List, Optional

import chromadb
from chromadb.api.models.Collection import Collection

from project_agent.config import get_settings
from project_agent.index.embeddings import get_embedding_provider
from project_agent.ingest.chunker import Chunk
from project_agent.models.schemas import DocumentInfo


class VectorIndex:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.embedder = get_embedding_provider()
        self.client = chromadb.PersistentClient(path=str(self.settings.chroma_dir))

    def _collection_name(self, project_id: str) -> str:
        return f"project_{project_id.replace('-', '_')}"

    def _get_collection(self, project_id: str) -> Collection:
        return self.client.get_or_create_collection(
            name=self._collection_name(project_id),
            metadata={"hnsw:space": "cosine"},
        )

    def index_document(
        self,
        project_id: str,
        document: DocumentInfo,
        chunks: List[Chunk],
    ) -> int:
        if not chunks:
            return 0
        col = self._get_collection(project_id)
        self.delete_document(project_id, document.id)

        ids: List[str] = []
        documents: List[str] = []
        metadatas: List[Dict] = []

        texts = [c.text for c in chunks]
        embeddings = self.embedder.embed(texts)

        for chunk, emb in zip(chunks, embeddings):
            cid = f"{document.id}_{chunk.chunk_index}"
            ids.append(cid)
            documents.append(chunk.text)
            metadatas.append(
                {
                    "document_id": document.id,
                    "title": document.title,
                    "section": chunk.section or "",
                    "page": chunk.page if chunk.page is not None else -1,
                    "chunk_index": chunk.chunk_index,
                }
            )
            col.add(ids=[cid], documents=documents[-1:], embeddings=[emb], metadatas=[metadatas[-1]])

        return len(chunks)

    def delete_document(self, project_id: str, document_id: str) -> None:
        col = self._get_collection(project_id)
        existing = col.get(where={"document_id": document_id})
        if existing["ids"]:
            col.delete(ids=existing["ids"])

    def delete_project(self, project_id: str) -> None:
        name = self._collection_name(project_id)
        try:
            self.client.delete_collection(name)
        except Exception:
            pass

    def search(
        self,
        project_id: str,
        query: str,
        *,
        top_k: Optional[int] = None,
    ) -> List[dict]:
        k = top_k or self.settings.retrieval_top_k
        col = self._get_collection(project_id)
        query_emb = self.embedder.embed([query])[0]
        result = col.query(query_embeddings=[query_emb], n_results=k)
        hits: List[dict] = []
        if not result["ids"] or not result["ids"][0]:
            return hits
        for i, cid in enumerate(result["ids"][0]):
            meta = (result["metadatas"] or [[{}]])[0][i]
            doc_text = (result["documents"] or [[""]])[0][i]
            distance = (result["distances"] or [[1.0]])[0][i]
            hits.append(
                {
                    "id": cid,
                    "text": doc_text,
                    "metadata": meta,
                    "distance": distance,
                }
            )
        return hits
