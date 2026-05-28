from __future__ import annotations

from typing import Optional

from project_agent.config import get_settings
from project_agent.index.vector_store import VectorIndex
from project_agent.models.schemas import ChatRequest, ChatResponse, Citation
from project_agent.rag.llm import generate_answer
from project_agent.storage.project_store import ProjectStore


class RagService:
    def __init__(self) -> None:
        self.store = ProjectStore()
        self.vector = VectorIndex()
        self.settings = get_settings()

    def chat(self, project_id: str, request: ChatRequest) -> ChatResponse:
        if self.store.get_project(project_id) is None:
            raise ValueError("Project not found")

        top_k = request.top_k or self.settings.retrieval_top_k
        hits = self.vector.search(project_id, request.question, top_k=top_k)

        citations = [
            Citation(
                document_id=(h.get("metadata") or {}).get("document_id", ""),
                title=(h.get("metadata") or {}).get("title", ""),
                section=(h.get("metadata") or {}).get("section") or None,
                page=_page_or_none(h),
                excerpt=(h.get("text") or "")[:300],
            )
            for h in hits
        ]

        answer, used_ollama = generate_answer(request.question, hits)
        return ChatResponse(answer=answer, citations=citations, used_ollama=used_ollama)


def _page_or_none(hit: dict) -> Optional[int]:
    page = (hit.get("metadata") or {}).get("page", -1)
    if page is None or int(page) < 0:
        return None
    return int(page)
