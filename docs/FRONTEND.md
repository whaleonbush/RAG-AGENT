# React 프론트엔드

## 스택

- React 18 + Vite + TypeScript
- Tailwind CSS
- react-dropzone (드래그앤드롭)
- react-router-dom

## 실행

API (`8000`)와 프론트(`5173`)를 동시에 실행합니다. Vite가 `/projects` 등을 API로 프록시합니다.

```bash
# 터미널 1
uvicorn project_agent.main:app --reload

# 터미널 2
cd frontend && npm run dev
```

http://127.0.0.1:5173

## 화면

| 경로 | 설명 |
|------|------|
| `/` | 과제 목록, 새 과제 생성 |
| `/projects/:id` | 드롭존 업로드, 자료 목록, AI 채팅 |

## 빌드

```bash
cd frontend && npm run build
```

산출물: `frontend/dist/` (사내 배포 시 nginx 또는 정적 서버에 올림)

## 환경 변수

`frontend/.env`:

```env
# API를 다른 호스트에 둘 때만 설정 (기본: Vite 프록시 사용)
# VITE_API_BASE=http://192.168.x.x:8000
```
