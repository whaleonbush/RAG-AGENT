from __future__ import annotations

from typing import List, Tuple

import httpx

from project_agent.config import get_settings

SYSTEM_PROMPT = """당신은 과제 전용 지식 에이전트입니다.
아래 [컨텍스트]에 있는 정보만 사용해 질문에 답하세요.
컨텍스트에 없으면 "제공된 자료에서 해당 정보를 찾지 못했습니다"라고 답하세요.
답변 마지막에 참고한 출처를 [출처: 문서제목, 섹션/페이지] 형식으로 나열하세요."""


def build_context_block(hits: List[dict]) -> str:
    blocks: List[str] = []
    for i, hit in enumerate(hits, start=1):
        meta = hit.get("metadata") or {}
        title = meta.get("title", "unknown")
        section = meta.get("section") or ""
        page = meta.get("page", -1)
        loc = f"p.{page}" if page and int(page) > 0 else section
        blocks.append(f"--- 컨텍스트 {i} [{title} {loc}] ---\n{hit.get('text', '')}")
    return "\n\n".join(blocks)


_client: httpx.Client | None = None


def _get_client(base_url: str) -> httpx.Client:
    global _client
    if _client is None:
        # trust_env=False: 사내 프록시 환경변수가 localhost Ollama 호출을 가로채는 것을 방지.
        _client = httpx.Client(base_url=base_url, timeout=300.0, trust_env=False)
    return _client


def generate_answer(question: str, hits: List[dict]) -> Tuple[str, bool]:
    settings = get_settings()
    context = build_context_block(hits)
    user_prompt = f"[컨텍스트]\n{context}\n\n[질문]\n{question}"

    try:
        client = _get_client(settings.ollama_base_url)
        resp = client.post(
            "/api/chat",
            json={
                "model": settings.ollama_model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt[:8000]},
                ],
                "stream": False,
                # keep_alive: 모델을 메모리에 유지해 매 요청마다 재로딩하지 않는다(CPU에서 특히 중요).
                "keep_alive": settings.ollama_keep_alive,
                "options": {
                    "temperature": 0.2,
                    # num_ctx: 컨텍스트 창을 제한해 CPU 처리량을 높인다.
                    "num_ctx": settings.ollama_num_ctx,
                    # num_predict: 답변 최대 토큰을 제한해 생성 시간을 줄인다.
                    "num_predict": settings.ollama_num_predict,
                },
            },
        )
        resp.raise_for_status()
        content = resp.json()["message"]["content"]
        return content.strip(), True
    except Exception as exc:
        print(f"[OLLAMA ERROR] {type(exc).__name__}: {exc}")
        return _fallback_answer(question, hits), False


def _fallback_answer(question: str, hits: List[dict]) -> str:
    if not hits:
        return "제공된 자료에서 해당 정보를 찾지 못했습니다. (Ollama 미연결 — 검색 결과만 표시합니다.)"
    lines = [
        "Ollama에 연결할 수 없어 검색된 관련 구절을 요약해 드립니다.",
        f"질문: {question}",
        "",
    ]
    for i, hit in enumerate(hits[:3], start=1):
        meta = hit.get("metadata") or {}
        title = meta.get("title", "unknown")
        excerpt = (hit.get("text") or "")[:400]
        lines.append(f"{i}. [{title}] {excerpt}...")
    lines.append("\n[출처] 위 인용 구절을 참고하세요.")
    return "\n".join(lines)
