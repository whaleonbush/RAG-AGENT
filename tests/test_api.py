from fastapi.testclient import TestClient

from project_agent.main import create_app

client = TestClient(create_app())


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_project_and_manual_note_flow():
    r = client.post("/projects", json={"name": "테스트 과제", "description": "PoC"})
    assert r.status_code == 200
    project_id = r.json()["id"]

    r = client.post(
        f"/projects/{project_id}/documents/manual",
        json={
            "title": "모터 스펙 메모",
            "content": "정격 전압은 24V이며 허용 오차는 ±5%입니다.",
            "tags": ["motor"],
        },
    )
    assert r.status_code == 200
    doc_id = r.json()["id"]

    r = client.post(f"/projects/{project_id}/documents/{doc_id}/index")
    assert r.status_code == 200
    assert r.json()["chunk_count"] >= 1

    r = client.post(
        f"/projects/{project_id}/chat",
        json={"question": "정격 전압이 얼마야?"},
    )
    assert r.status_code == 200
    data = r.json()
    assert "24" in data["answer"] or any("24" in c["excerpt"] for c in data["citations"])
