"""
Smoke tests for the core API surface: health, document listing, upload
validation, and chat session lifecycle. LLM/embedding calls are not mocked
here at the unit level — see test_rag.py for pipeline-level mocking.
"""
import io

import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "app_name" in body


@pytest.mark.asyncio
async def test_list_documents_empty_or_list(client):
    resp = await client.get("/api/documents")
    assert resp.status_code == 200
    body = resp.json()
    assert "documents" in body
    assert isinstance(body["documents"], list)


@pytest.mark.asyncio
async def test_upload_rejects_non_pdf(client):
    fake_file = io.BytesIO(b"not a real pdf")
    files = {"file": ("notes.txt", fake_file, "text/plain")}
    resp = await client.post("/api/upload", files=files)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_get_nonexistent_document_returns_404(client):
    resp = await client.get("/api/documents/does-not-exist")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_document_returns_404(client):
    resp = await client.delete("/api/documents/does-not-exist")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_chat_session_history_not_found(client):
    resp = await client.get("/api/chat/sessions/does-not-exist/messages")
    assert resp.status_code == 404


# ---------- Chat History feature (/api/history) ----------

@pytest.mark.asyncio
async def test_create_chat_session(client):
    resp = await client.post("/api/history/sessions", json={"title": "My First Chat"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["title"] == "My First Chat"
    assert body["message_count"] == 0
    assert body["document_id"] is None


@pytest.mark.asyncio
async def test_create_chat_session_with_invalid_document_returns_404(client):
    resp = await client.post(
        "/api/history/sessions", json={"title": "Doc chat", "document_id": "nonexistent-doc"}
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_all_chat_sessions_includes_created(client):
    created = await client.post("/api/history/sessions", json={"title": "Listable Chat"})
    session_id = created.json()["id"]

    resp = await client.get("/api/history/sessions")
    assert resp.status_code == 200
    ids = [s["id"] for s in resp.json()["sessions"]]
    assert session_id in ids


@pytest.mark.asyncio
async def test_get_single_chat_session_detail(client):
    created = await client.post("/api/history/sessions", json={"title": "Detail Chat"})
    session_id = created.json()["id"]

    resp = await client.get(f"/api/history/sessions/{session_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == session_id
    assert body["messages"] == []


@pytest.mark.asyncio
async def test_rename_chat_session(client):
    created = await client.post("/api/history/sessions", json={"title": "Old Name"})
    session_id = created.json()["id"]

    resp = await client.patch(
        f"/api/history/sessions/{session_id}/rename", json={"title": "New Name"}
    )
    assert resp.status_code == 200

    detail = await client.get(f"/api/history/sessions/{session_id}")
    assert detail.json()["title"] == "New Name"


@pytest.mark.asyncio
async def test_rename_nonexistent_chat_session_returns_404(client):
    resp = await client.patch(
        "/api/history/sessions/does-not-exist/rename", json={"title": "X"}
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_search_chat_sessions_by_title(client):
    await client.post("/api/history/sessions", json={"title": "Unique Searchable Title XYZ"})

    resp = await client.get("/api/history/sessions/search", params={"q": "Searchable Title XYZ"})
    assert resp.status_code == 200
    titles = [s["title"] for s in resp.json()["sessions"]]
    assert any("Searchable Title XYZ" in t for t in titles)


@pytest.mark.asyncio
async def test_clear_chat_session(client):
    created = await client.post("/api/history/sessions", json={"title": "Clear Me"})
    session_id = created.json()["id"]

    resp = await client.post(f"/api/history/sessions/{session_id}/clear")
    assert resp.status_code == 200

    detail = await client.get(f"/api/history/sessions/{session_id}")
    assert detail.json()["messages"] == []


@pytest.mark.asyncio
async def test_delete_chat_session(client):
    created = await client.post("/api/history/sessions", json={"title": "Delete Me"})
    session_id = created.json()["id"]

    resp = await client.delete(f"/api/history/sessions/{session_id}")
    assert resp.status_code == 200

    detail = await client.get(f"/api/history/sessions/{session_id}")
    assert detail.status_code == 404
