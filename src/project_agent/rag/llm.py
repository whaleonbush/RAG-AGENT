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


def generate_answer(question: str, hits: List[dict]) -> Tuple[str, bool]:
    settings = get_settings()
    context = build_context_block(hits)
    user_prompt = f"[컨텍스트]\n{context}\n\n[질문]\n{question}"

    try:
        with httpx.Client(base_url=settings.ollama_base_url, timeout=300.0, trust_env=False) as client:
            resp = client.post(
                "/api/chat",
                json={
                    "model": settings.ollama_model,
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt[:8000]},
                    ],
                    "stream": False,
                    "options": {"temperature": 0.3, "num_predict": 1024},
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
