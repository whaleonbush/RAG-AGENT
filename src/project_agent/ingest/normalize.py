from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def _yaml_escape(value: str) -> str:
    if any(c in value for c in ":\"'\n"):
        return '"' + value.replace('"', '\\"') + '"'
    return value


def _metadata_to_yaml(meta: Dict) -> str:
    lines: List[str] = []
    for key, val in meta.items():
        if isinstance(val, list):
            inner = ", ".join(_yaml_escape(str(v)) for v in val)
            lines.append(f"{key}: [{inner}]")
        else:
            lines.append(f"{key}: {_yaml_escape(str(val))}")
    return "\n".join(lines)


def build_markdown(
    *,
    project_id: str,
    document_id: str,
    title: str,
    source_type: str,
    source_name: str,
    body: str,
    tags: Optional[List[str]] = None,
) -> str:
    meta = {
        "project_id": project_id,
        "document_id": document_id,
        "title": title,
        "source_type": source_type,
        "source": source_name,
        "tags": tags or [],
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }
    return f"---\n{_metadata_to_yaml(meta)}\n---\n\n{body.strip()}\n"


def extract_body(markdown: str) -> Tuple[Dict, str]:
    m = _FRONTMATTER_RE.match(markdown)
    if not m:
        return {}, markdown.strip()
    yaml_block = m.group(1)
    body = markdown[m.end() :].strip()
    meta: Dict = {}
    for line in yaml_block.splitlines():
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        val = val.strip()
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            meta[key] = [v.strip().strip('"') for v in inner.split(",") if v.strip()] if inner else []
        else:
            meta[key] = val.strip('"')
    return meta, body
