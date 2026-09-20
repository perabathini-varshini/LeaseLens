from pathlib import Path

from fastapi.testclient import TestClient

from app import app
from src import pipeline

client = TestClient(app)

BASE_DIR = Path(__file__).resolve().parent.parent
LEASES_DIR = BASE_DIR / "data" / "leases"


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
    assert "only one PDF or DOCX extension" in response.json()["detail"]


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

def test_valid_pdf_analysis():
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
        str(
            tmp_path / "gemini_failure_test.json"
        )
    )

        assert result["compliance"]

        for compliance_result in result["compliance"]:
            assert (
            compliance_result["ai_explanation"]
            == "AI explanation unavailable: "
            "Gemini unavailable for test"
        )