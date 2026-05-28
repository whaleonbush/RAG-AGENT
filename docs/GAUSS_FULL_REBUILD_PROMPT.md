# 가우스(Gauss) 전체 재구현 프롬프트

아래 블록 전체를 VS Code 가우스 채팅에 붙여넣으세요. (GitHub clone이 불가할 때만 사용)

---

```
# 역할
당신은 Python 백엔드 엔지니어입니다. 빈 폴더에 아래 스펙대로 **과제 지식 에이전트(Project Knowledge Agent)** PoC를 처음부터 구현하세요. 파일을 빠짐없이 만들고, 마지막에 `pytest`가 통과하도록 하세요.

# 프로젝트 목적
- 과제(프로젝트)마다 독립된 지식 공간
- PDF/DOCX/XLSX/TXT/MD 업로드 + 수동 메모 → Markdown 정규화
- 청킹 → FastEmbed(기본) 또는 Ollama 임베딩 → Chroma (과제별 collection)
- RAG 질의 + citations; Ollama 있으면 LLM 답변, 없으면 검색 요약 fallback

# 기술 스택
- Python 3.9+ (Optional/List 사용, `str | None` 금지)
- FastAPI, uvicorn, chromadb, fastembed, pymupdf, python-docx, openpyxl
- setuptools.build_meta (pyproject.toml)

# 디렉터리
project-agent/
  pyproject.toml, .env.example, .gitignore, docker-compose.yml, README.md
  src/project_agent/{main,config,api/,models/,storage/,ingest/,index/,rag/}
  tests/{test_chunker.py,test_api.py}

# API
GET /health
POST/GET/DELETE /projects
GET/POST /projects/{id}/documents (upload manual, list)
POST .../documents/{doc_id}/index, POST .../index
DELETE .../documents/{doc_id}
POST .../chat
GET / → minimal HTML chat (project id + question)

# 중요 구현 메모
1. normalize.py: python-frontmatter 사용 금지, YAML frontmatter 직접 구현
2. embeddings: FastEmbed 결과를 float list로 변환 후 Chroma에 저장
3. vector collection: project_{uuid_with_underscores}
4. .gitignore: .env, .venv, storage/

# 테스트
test_health; test flow create project → manual note → index → chat (answer or citations contain "24")

완료: pip install -e ".[dev]" && pytest -q (4 passed)
```

---

원본 저장소: https://github.com/whaleonbush/RAG-AGENT
