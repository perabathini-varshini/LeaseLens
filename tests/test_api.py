from pathlib import Path

from fastapi.testclient import TestClient

from app import app
from src import pipeline
from api import routes as api_routes
from src.chunker import create_chunks

from src.vector_store import LocalVectorStore

client = TestClient(app)

BASE_DIR = Path(__file__).resolve().parent.parent
LEASES_DIR = BASE_DIR / "data" / "leases"


class FakeIndexingService:
    def __init__(self, vector_store):
        self.vector_store = vector_store

    def index_clauses(self, clauses, max_words=120):
        chunks = create_chunks(
            clauses,
            max_words=max_words
        )

        self.vector_store.records = [
            {
                "chunk": chunk,
                "embedding": [1.0, 0.0, 0.0]
            }
            for chunk in chunks
        ]

        self.vector_store.save()

        return {
            "chunks_indexed": len(chunks),
            "chunk_ids": [
                chunk["chunk_id"]
                for chunk in chunks
            ]
        }


def test_health_endpoint():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "LeaseLens"
    }


def test_invalid_file_type():
    response = client.post(
        "/api/analyze",
        files={
            "file": (
                "sample.txt",
                b"This is an invalid file.",
                "text/plain"
            )
        }
    )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_duplicate_extension():
    response = client.post(
        "/api/analyze",
        files={
            "file": (
                "sample_lease.pdf.pdf",
                b"fake pdf content",
                "application/pdf"
            )
        }
    )

    assert response.status_code == 400
    assert (
        "only one PDF or DOCX extension"
        in response.json()["detail"]
    )


def test_empty_file():
    response = client.post(
        "/api/analyze",
        files={
            "file": (
                "empty.pdf",
                b"",
                "application/pdf"
            )
        }
    )

    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_valid_pdf_analysis(monkeypatch):
    monkeypatch.setattr(
        api_routes,
        "IndexingService",
        FakeIndexingService
    )

    pdf_path = LEASES_DIR / "sample_lease.pdf"

    with pdf_path.open("rb") as file:
        response = client.post(
            "/api/analyze",
            files={
                "file": (
                    pdf_path.name,
                    file,
                    "application/pdf"
                )
            }
        )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["lease_id"]
    assert data["rag_indexing"]["status"] == "success"
    assert data["rag_indexing"]["chunks_indexed"] > 0
    assert data["result"]["summary"]["total_clauses"] > 0
    assert len(data["result"]["compliance"]) > 0


def test_analysis_survives_gemini_initialization_failure(
    monkeypatch,
    tmp_path
):
    class FailingGeminiExplainer:
        def __init__(self):
            raise RuntimeError(
                "Gemini unavailable for test"
            )

    monkeypatch.setattr(
        pipeline,
        "GeminiExplainer",
        FailingGeminiExplainer
    )

    result = pipeline.run_pipeline(
        "data/leases/sample_lease.pdf",
        str(tmp_path / "gemini_failure_test.json")
    )

    assert result["compliance"]

    for compliance_result in result["compliance"]:
        assert (
            compliance_result["ai_explanation"]
            == "AI explanation unavailable: "
            "Gemini unavailable for test"
        )

def test_ask_invalid_lease_id():
    response = client.post(
        "/api/ask",
        json={
            "lease_id": "not-a-valid-uuid",
            "question": "What is the rent?"
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid lease ID."


def test_ask_unknown_lease(monkeypatch, tmp_path):
    monkeypatch.setattr(
        api_routes,
        "VECTOR_DIR",
        tmp_path
    )

    response = client.post(
        "/api/ask",
        json={
            "lease_id": "12345678-1234-5678-1234-567812345678",
            "question": "What is the rent?"
        }
    )

    assert response.status_code == 404
    assert "No indexed lease found" in response.json()["detail"]

def test_ask_empty_question():
    response = client.post(
        "/api/ask",
        json={
            "lease_id": "12345678-1234-5678-1234-567812345678",
            "question": "   "
        }
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Question cannot be empty."

def test_ask_returns_answer_and_sources(monkeypatch, tmp_path):
    lease_id = "12345678-1234-5678-1234-567812345678"

    monkeypatch.setattr(
        api_routes,
        "VECTOR_DIR",
        tmp_path
    )

    vector_path = tmp_path / f"{lease_id}.json"

    vector_store = LocalVectorStore(str(vector_path))
    vector_store.add(
        {
            "chunk_id": "CHUNK-001",
            "clause_id": "CLAUSE-001",
            "section_number": "1",
            "section_title": "Rent",
            "clause_type": "rent",
            "text": "The monthly rent is Rs. 25,000.",
            "source": "sample_lease.pdf",
            "location": "Page 1",
            "location_type": "page"
        },
        [1.0, 0.0, 0.0]
    )
    vector_store.save()

    class FakeRAGService:
        def __init__(self, vector_store):
            self.vector_store = vector_store

        def answer(self, question):
            assert question == "What is the monthly rent?"

            chunk = self.vector_store.records[0]["chunk"]

            return {
                "answer": "The monthly rent is Rs. 25,000.",
                "sources": [
                    {
                        "chunk_id": chunk["chunk_id"],
                        "clause_id": chunk["clause_id"],
                        "section_title": chunk["section_title"],
                        "clause_type": chunk["clause_type"],
                        "text": chunk["text"],
                        "score": 1.0
                    }
                ]
            }

    monkeypatch.setattr(
        api_routes,
        "RAGService",
        FakeRAGService
    )

    response = client.post(
        "/api/ask",
        json={
            "lease_id": lease_id,
            "question": "What is the monthly rent?"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["lease_id"] == lease_id
    assert data["answer"] == "The monthly rent is Rs. 25,000."
    assert len(data["sources"]) == 1
    assert data["sources"][0]["chunk_id"] == "CHUNK-001"
    assert data["sources"][0]["text"] == "The monthly rent is Rs. 25,000."