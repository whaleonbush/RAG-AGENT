from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Chunk:
    text: str
    section: Optional[str]
    page: Optional[int]
    chunk_index: int


_PAGE_RE = re.compile(r"^## Page (\d+)$", re.MULTILINE)
_SECTION_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


def _split_paragraphs(text: str) -> List[str]:
    parts = re.split(r"\n\s*\n", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _detect_page(section_header: Optional[str]) -> Optional[int]:
    if not section_header:
        return None
    m = re.match(r"Page (\d+)", section_header)
    return int(m.group(1)) if m else None


def chunk_text(text: str, *, chunk_size: int = 800, overlap: int = 120) -> List[Chunk]:
    paragraphs = _split_paragraphs(text)
    if not paragraphs:
        return []

    chunks: List[Chunk] = []
    current_section: Optional[str] = None
    buffer: List[str] = []
    buffer_len = 0
    chunk_index = 0

    def flush() -> None:
        nonlocal buffer, buffer_len, chunk_index
        if not buffer:
            return
        body = "\n\n".join(buffer)
        chunks.append(
            Chunk(
                text=body,
                section=current_section,
                page=_detect_page(current_section),
                chunk_index=chunk_index,
            )
        )
        chunk_index += 1
        if overlap > 0 and len(body) > overlap:
            tail = body[-overlap:]
            buffer = [tail]
            buffer_len = len(tail)
        else:
            buffer = []
            buffer_len = 0

    for para in paragraphs:
        if para.startswith("## Page "):
            flush()
            current_section = para.replace("## ", "")
            continue
        header = _SECTION_RE.match(para.split("\n", 1)[0])
        if header and para.startswith(header.group(0)):
            flush()
            current_section = header.group(2).strip()
            if buffer_len + len(para) + 2 <= chunk_size:
                buffer.append(para)
                buffer_len += len(para) + 2
            else:
                if buffer:
                    flush()
                buffer = [para]
                buffer_len = len(para)
            continue

        if buffer_len + len(para) + 2 > chunk_size:
            flush()
        buffer.append(para)
        buffer_len += len(para) + 2
        if buffer_len >= chunk_size:
            flush()

    flush()
    return chunks
