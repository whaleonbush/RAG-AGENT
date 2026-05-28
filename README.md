# 과제 지식 에이전트 (RAG-AGENT)

과제(프로젝트)마다 문서·메모를 모아 AI 검색에 맞게 정규화하고, 온프레미스 LLM(Ollama)으로 질의응답하는 RAG 에이전트 PoC입니다.

**Repository:** https://github.com/whaleonbush/RAG-AGENT

**사내 PC 설치·가우스 프롬프트:** [docs/사내_설치_및_가우스_프롬프트.md](docs/사내_설치_및_가우스_프롬프트.md)

## 기능 (MVP)

- 과제(Project) 생성·목록·삭제
- 파일 업로드: PDF, DOCX, XLSX, TXT, MD
- 수동 메모 입력
- Markdown 정규화 → 청킹 → 벡터 인덱싱 (Chroma + FastEmbed)
- RAG 채팅 API + 간단 웹 UI (`/`)

## 요구 사항

- Python 3.9+ (3.11 권장)

## 빠른 시작

```bash
git clone https://github.com/whaleonbush/RAG-AGENT.git
cd RAG-AGENT
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

cp .env.example .env
# 최초 실행 시 FastEmbed 모델 다운로드 (수 분 소요 가능)

uvicorn project_agent.main:app --reload
```

브라우저: http://127.0.0.1:8000/docs (Swagger) · 레거시 채팅: http://127.0.0.1:8000/legacy

### React UI (드래그앤드롭)

터미널 1 — API:

```bash
source .venv/bin/activate
uvicorn project_agent.main:app --reload
```

터미널 2 — 프론트:

```bash
cd frontend
npm install
npm run dev
```

브라우저: http://127.0.0.1:5173

### Ollama (온프레 LLM, 선택)

```bash
docker compose up ollama -d
docker exec -it $(docker ps -qf name=ollama) ollama pull llama3.2
docker exec -it $(docker ps -qf name=ollama) ollama pull nomic-embed-text
```

`.env`에서 `EMBEDDING_PROVIDER=ollama`로 바꾸면 Ollama 임베딩을 사용합니다.

## API 사용 예시

```bash
# 1. 과제 생성
curl -s -X POST http://127.0.0.1:8000/projects \
  -H 'Content-Type: application/json' \
  -d '{"name":"모터 개발","description":"2026 Q2"}'

# 2. 메모 추가
curl -s -X POST http://127.0.0.1:8000/projects/{PROJECT_ID}/documents/manual \
  -H 'Content-Type: application/json' \
  -d '{"title":"스펙","content":"정격 전압 24V"}'

# 3. 인덱싱
curl -s -X POST http://127.0.0.1:8000/projects/{PROJECT_ID}/index

# 4. 질문
curl -s -X POST http://127.0.0.1:8000/projects/{PROJECT_ID}/chat \
  -H 'Content-Type: application/json' \
  -d '{"question":"정격 전압이 얼마야?"}'
```

## 프로젝트 구조

```
src/project_agent/
  api/          # FastAPI 라우트
  ingest/       # 파싱, Markdown, 청킹
  index/        # 임베딩, Chroma
  rag/          # 검색 + Ollama 답변
  storage/      # 과제·문서 메타데이터 (파일시스템)
storage/        # 런타임 데이터 (gitignore)
```

## 테스트

```bash
pytest
```

## 다음 단계

- PLM 커넥터 (동일 ingest 파이프라인)
- SSO / 과제 멤버 권한
- 하이브리드 검색 (BM25 + 벡터)
- 재인덱싱 스케줄러
