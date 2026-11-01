import io
import pytest


def test_upload_text_document(client, registered_user):
    """SCRUM-12: Upload Document, extract text, summarize, and auto-tag."""
    headers = registered_user["headers"]

    sample_content = (
        "Artificial intelligence and deep learning algorithms have revolutionized natural language "
        "processing. Large language models leverage transformer neural networks with self-attention "
        "mechanisms. Vector embeddings allow semantic search and retrieval-augmented generation to "
        "ground responses on verified academic source materials."
    )
    file_bytes = io.BytesIO(sample_content.encode("utf-8"))

    res = client.post(
        "/api/documents/upload",
        files={"file": ("transformers_ai.txt", file_bytes, "text/plain")},
        data={"title": "Introduction to Transformers", "category": "Artificial Intelligence"},
        headers=headers
    )
    assert res.status_code == 201
    doc = res.json()
    assert doc["title"] == "Introduction to Transformers"
    assert doc["processing_status"] == "completed"
    assert doc["word_count"] > 20
    assert doc["summary"] is not None
    assert len(doc["tags"]) > 0

    # Retrieve from list
    list_res = client.get("/api/documents", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1


def test_upload_unsupported_format_rejected(client, registered_user):
    """SCRUM-12: File type validation rejects unsupported extensions."""
    headers = registered_user["headers"]
    bad_file = io.BytesIO(b"binary executable")

    res = client.post(
        "/api/documents/upload",
        files={"file": ("malicious.exe", bad_file, "application/x-msdownload")},
        headers=headers
    )
    assert res.status_code == 400
    assert "unsupported file format" in res.json()["detail"].lower()


def test_create_and_manage_note(client, registered_user):
    """SCRUM-13: Create note, edit note, auto-tagging, and deletion."""
    headers = registered_user["headers"]

    # 1. Create note
    create_res = client.post(
        "/api/notes",
        json={
            "title": "Study Note: Relational Databases",
            "content": "Relational databases use structured query language (SQL) and ACID transactions to ensure database consistency and atomicity.",
            "category": "Computer Science",
            "tags": ["Databases", "SQL"],
            "is_pinned": True
        },
        headers=headers
    )
    assert create_res.status_code == 201
    note = create_res.json()
    assert note["title"] == "Study Note: Relational Databases"
    assert note["is_pinned"] is True
    assert note["word_count"] > 10

    note_id = note["id"]

    # 2. Update note
    update_res = client.put(
        f"/api/notes/{note_id}",
        json={
            "title": "Study Note: Advanced SQL & Indexing",
            "is_pinned": False
        },
        headers=headers
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Study Note: Advanced SQL & Indexing"
    assert update_res.json()["is_pinned"] is False

    # 3. List notes
    list_res = client.get("/api/notes", headers=headers)
    assert list_res.status_code == 200
    assert any(n["id"] == note_id for n in list_res.json())

    # 4. Delete note
    del_res = client.delete(f"/api/notes/{note_id}", headers=headers)
    assert del_res.status_code == 200
