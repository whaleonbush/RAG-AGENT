from project_agent.ingest.chunker import chunk_text


def test_chunk_text_splits_long_content():
    body = "문단 하나.\n\n" + ("가" * 500 + ".\n\n") * 5
    chunks = chunk_text(body, chunk_size=200, overlap=20)
    assert len(chunks) >= 2
    assert all(c.text for c in chunks)


def test_chunk_detects_page_sections():
    body = "## Page 3\n\n모터 정격 전압은 24V입니다."
    chunks = chunk_text(body, chunk_size=800, overlap=0)
    assert len(chunks) == 1
    assert chunks[0].page == 3
