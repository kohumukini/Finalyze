import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_process_document_and_list_documents():
    response = client.post(
        "/process-document",
        content="This is a sample document for testing.",
        headers={"content-type": "text/plain"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == "Document processed successfully."
    assert payload["document"]["word_count"] == 7

    list_response = client.get("/documents")
    assert list_response.status_code == 200
    documents = list_response.json()["documents"]
    assert any(doc["id"] == payload["document"]["id"] for doc in documents)


def test_chat_route_returns_response():
    response = client.post("/chat", json={"message": "Hello from the chat test"})

    assert response.status_code == 200
    payload = response.json()
    assert "response" in payload
    assert isinstance(payload["response"], str)
    assert payload["response"]
