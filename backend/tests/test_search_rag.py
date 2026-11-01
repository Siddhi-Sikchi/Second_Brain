import io
import pytest


def test_hybrid_search_and_rag(client, registered_user):
    """SCRUM-25: Hybrid keyword & semantic search and RAG Q&A grounding."""
    headers = registered_user["headers"]

    # Ingest document
    content = (
        "Operating systems manage computer hardware and software resources. "
        "The kernel is the central component that provides memory management, process scheduling, "
        "and hardware device driver interaction. Virtual memory uses paging tables to isolate user memory."
    )
    res = client.post(
        "/api/documents/upload",
        files={"file": ("os_principles.txt", io.BytesIO(content.encode()), "text/plain")},
        data={"title": "Operating Systems Architecture"},
        headers=headers
    )
    assert res.status_code == 201

    # Search for "kernel memory management"
    search_res = client.post(
        "/api/search",
        json={"query": "kernel memory management"},
        headers=headers
    )
    assert search_res.status_code == 200
    results = search_res.json()
    assert len(results) > 0
    assert "Operating Systems" in results[0]["title"]
    assert results[0]["relevance_score"] > 0

    # Ask RAG question
    rag_res = client.post(
        "/api/search/rag",
        json={"question": "What is the role of the operating system kernel?"},
        headers=headers
    )
    assert rag_res.status_code == 200
    rag_data = rag_res.json()
    assert rag_data["is_grounded"] is True
    assert len(rag_data["citations"]) > 0
    assert "Operating Systems Architecture" in rag_data["citations"][0]["source_title"]


def test_rag_empty_information_fallback(client, registered_user):
    """SCRUM-25: Clear indication when knowledge base lacks sufficient info."""
    headers = registered_user["headers"]

    res = client.post(
        "/api/search/rag",
        json={"question": "What is quantum entanglement and quantum teleportation?"},
        headers=headers
    )
    assert res.status_code == 200
    data = res.json()
    assert data["is_grounded"] is False
    assert "not enough information" in data["answer"].lower()
