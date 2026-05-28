from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: str = ""


class Project(BaseModel):
    id: str
    name: str
    description: str
    created_at: datetime


class DocumentInfo(BaseModel):
    id: str
    project_id: str
    title: str
    source_type: Literal["file", "manual"]
    original_filename: Optional[str] = None
    status: Literal["pending", "indexed", "failed"] = "pending"
    chunk_count: int = 0
    error: Optional[str] = None
    created_at: datetime


class ManualNoteCreate(BaseModel):
    title: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)
    tags: List[str] = Field(default_factory=list)


class IndexResult(BaseModel):
    document_id: str
    chunk_count: int
    status: str


class Citation(BaseModel):
    document_id: str
    title: str
    section: Optional[str] = None
    page: Optional[int] = None
    excerpt: str


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: Optional[int] = None


class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
    used_ollama: bool
