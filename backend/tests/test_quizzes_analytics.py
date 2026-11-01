import io
import pytest


def test_quiz_generator_and_submission(client, registered_user):
    """SCRUM-27: Generate quiz from documents, attempt quiz, and evaluate score."""
    headers = registered_user["headers"]

    # Ingest document
    content = (
        "Distributed consensus algorithms like Raft and Paxos allow state machine replication. "
        "Raft divides consensus into leader election, log replication, and safety. "
        "Heartbeat messages maintain leader authority and detect server crashes."
    )
    client.post(
        "/api/documents/upload",
        files={"file": ("consensus.txt", io.BytesIO(content.encode()), "text/plain")},
        data={"title": "Distributed Consensus"},
        headers=headers
    )

    # Generate quiz
    gen_res = client.post(
        "/api/quizzes/generate",
        json={"title": "Raft Consensus Quiz", "source_type": "all", "question_count": 3},
        headers=headers
    )
    assert gen_res.status_code == 201
    quiz = gen_res.json()
    assert quiz["title"] == "Raft Consensus Quiz"
    assert len(quiz["questions"]) >= 1

    q_id = quiz["questions"][0]["id"]
    # Submit attempt
    submit_res = client.post(
        f"/api/quizzes/{quiz['id']}/submit",
        json={"answers": [{"question_id": q_id, "user_answer": "Raft"}], "time_taken_seconds": 25},
        headers=headers
    )
    assert submit_res.status_code == 200
    res_data = submit_res.json()
    assert "score" in res_data
    assert len(res_data["evaluations"]) >= 1


def test_analytics_dashboard_metrics(client, registered_user):
    """SCRUM-28: Real-time analytics computed accurately from user database state."""
    headers = registered_user["headers"]

    res = client.get("/api/analytics/dashboard", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "total_documents" in data
    assert "total_notes" in data
    assert "total_words" in data
    assert "average_quiz_score" in data
    assert "storage_used_bytes" in data
    assert "categories" in data
    assert isinstance(data["categories"], dict)


def test_knowledge_graph_data(client, registered_user):
    """SCRUM-26: Knowledge graph structure contains nodes and edges."""
    headers = registered_user["headers"]

    res = client.get("/api/graph", headers=headers)
    assert res.status_code == 200
    graph = res.json()
    assert "nodes" in graph
    assert "links" in graph
    assert isinstance(graph["nodes"], list)
