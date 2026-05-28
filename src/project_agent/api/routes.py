from __future__ import annotations

import tempfile
from pathlib import Path
from typing import List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import HTMLResponse

from project_agent.index.service import IndexService
from project_agent.ingest.pipeline import IngestPipeline
from project_agent.models.schemas import (
    ChatRequest,
    ChatResponse,
    DocumentInfo,
    IndexResult,
    ManualNoteCreate,
    Project,
    ProjectCreate,
)
from project_agent.rag.service import RagService
from project_agent.storage.project_store import ProjectStore

router = APIRouter()
store = ProjectStore()
ingest = IngestPipeline(store)
indexer = IndexService()
rag = RagService()

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".xlsm", ".txt", ".md", ".markdown", ".csv"}


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.post("/projects", response_model=Project)
def create_project(body: ProjectCreate) -> Project:
    return store.create_project(body.name, body.description)


@router.get("/projects", response_model=List[Project])
def list_projects() -> List[Project]:
    return store.list_projects()


@router.get("/projects/{project_id}", response_model=Project)
def get_project(project_id: str) -> Project:
    project = store.get_project(project_id)
    if project is None:
        raise HTTPException(404, "Project not found")
    return project


@router.delete("/projects/{project_id}")
def delete_project(project_id: str) -> dict:
    indexer.vector.delete_project(project_id)
    if not store.delete_project(project_id):
        raise HTTPException(404, "Project not found")
    return {"deleted": True}


@router.get("/projects/{project_id}/documents", response_model=List[DocumentInfo])
def list_documents(project_id: str) -> List[DocumentInfo]:
    _ensure_project(project_id)
    return store.list_documents(project_id)


@router.post("/projects/{project_id}/documents/upload", response_model=DocumentInfo)
async def upload_document(
    project_id: str,
    file: UploadFile = File(...),
    title: Optional[str] = None,
) -> DocumentInfo:
    _ensure_project(project_id)
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type: {suffix}")

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        doc = ingest.ingest_file(
            project_id,
            file_path=tmp_path,
            original_filename=file.filename or "upload",
            title=title,
        )
    finally:
        tmp_path.unlink(missing_ok=True)

    if doc.status == "failed":
        raise HTTPException(422, doc.error or "Ingest failed")
    return doc


@router.post("/projects/{project_id}/documents/manual", response_model=DocumentInfo)
def create_manual_note(project_id: str, body: ManualNoteCreate) -> DocumentInfo:
    _ensure_project(project_id)
    doc = ingest.ingest_manual(
        project_id,
        title=body.title,
        content=body.content,
        tags=body.tags,
    )
    if doc.status == "failed":
        raise HTTPException(422, doc.error or "Ingest failed")
    return doc


@router.post("/projects/{project_id}/documents/{document_id}/index", response_model=IndexResult)
def index_document(project_id: str, document_id: str) -> IndexResult:
    _ensure_project(project_id)
    try:
        return indexer.index_document(project_id, document_id)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e


@router.post("/projects/{project_id}/index", response_model=List[IndexResult])
def index_all(project_id: str) -> List[IndexResult]:
    _ensure_project(project_id)
    return indexer.index_all_pending(project_id)


@router.delete("/projects/{project_id}/documents/{document_id}")
def delete_document(project_id: str, document_id: str) -> dict:
    _ensure_project(project_id)
    indexer.remove_document_index(project_id, document_id)
    if not store.delete_document(project_id, document_id):
        raise HTTPException(404, "Document not found")
    return {"deleted": True}


@router.post("/projects/{project_id}/chat", response_model=ChatResponse)
def chat(project_id: str, body: ChatRequest) -> ChatResponse:
    _ensure_project(project_id)
    try:
        return rag.chat(project_id, body)
    except ValueError as e:
        raise HTTPException(404, str(e)) from e


@router.get("/", response_class=HTMLResponse)
def ui_home() -> str:
    return _CHAT_HTML


def _ensure_project(project_id: str) -> None:
    if store.get_project(project_id) is None:
        raise HTTPException(404, "Project not found")


_CHAT_HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <title>과제 지식 에이전트</title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; }
    textarea, input { width: 100%; box-sizing: border-box; margin: 0.25rem 0 0.75rem; }
    button { padding: 0.5rem 1rem; cursor: pointer; }
    #log { white-space: pre-wrap; background: #f6f8fa; padding: 1rem; border-radius: 8px; min-height: 200px; }
    .cite { font-size: 0.9em; color: #444; margin-top: 0.5rem; }
  </style>
</head>
<body>
  <h1>과제 지식 에이전트</h1>
  <label>과제 ID <input id="projectId" placeholder="POST /projects 후 id 입력" /></label>
  <label>질문 <textarea id="question" rows="3"></textarea></label>
  <button id="ask">질문하기</button>
  <h2>응답</h2>
  <div id="log">과제를 만들고 문서를 업로드·인덱싱한 뒤 질문하세요.</div>
  <script>
    document.getElementById('ask').onclick = async () => {
      const projectId = document.getElementById('projectId').value.trim();
      const question = document.getElementById('question').value.trim();
      if (!projectId || !question) return alert('과제 ID와 질문을 입력하세요');
      const log = document.getElementById('log');
      log.textContent = '검색 중...';
      const res = await fetch(`/projects/${projectId}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question })
      });
      const data = await res.json();
      if (!res.ok) { log.textContent = JSON.stringify(data, null, 2); return; }
      let html = data.answer + '\\n\\n--- 출처 ---\\n';
      for (const c of data.citations || []) {
        html += `• ${c.title} ${c.section || ''} ${c.page ? 'p.'+c.page : ''}\\n  ${c.excerpt}\\n`;
      }
      html += '\\n(Ollama: ' + (data.used_ollama ? '연결됨' : '미연결, 검색 요약 모드') + ')';
      log.textContent = html;
    };
  </script>
</body>
</html>"""
