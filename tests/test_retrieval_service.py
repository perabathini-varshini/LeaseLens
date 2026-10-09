import pytest

from src.retrieval_service import RetrievalService


class FakeEmbeddingClient:
    def __init__(self):
        self.last_text = None

    def embed(self, text):
        self.last_text = text

        if "security deposit" in text.lower():
            return [0, 0, 1]

        return [1, 0, 0]


class FakeVectorStore:
    def __init__(self):
        self.records = [
            {
                "chunk": {
                    "chunk_id": "CHUNK-001",
                    "clause_id": "CLAUSE-001",
                    "section_title": "RENT",
                    "clause_type": "RENT",
                    "text": (
                        "The monthly rent is INR 50000."
                    )
                },
                "embedding": [1, 0, 0]
            },
            {
                "chunk": {
                    "chunk_id": "CHUNK-002",
                    "clause_id": "CLAUSE-002",
                    "section_title": "SECURITY DEPOSIT",
                    "clause_type": "SECURITY_DEPOSIT",
                    "text": (
                        "The security deposit is INR 40000."
                    )
                },
                "embedding": [0, 0, 1]
            }
        ]


def create_service():
    embedding_client = FakeEmbeddingClient()

    service = RetrievalService(
        FakeVectorStore(),
        embedding_client=embedding_client
    )

    return service, embedding_client


def test_search_returns_relevant_chunks():
    service, embedding_client = (
        create_service()
    )

    results = service.search(
        "What is the security deposit?",
        top_k=1
    )

    assert len(results) == 1

    assert (
        results[0]["chunk"]["chunk_id"]
        == "CHUNK-002"
    )

    assert results[0]["score"] == pytest.approx(
        1.0
    )

    assert (
        embedding_client.last_text
        == "What is the security deposit?"
    )


def test_search_respects_top_k():
    service, _ = create_service()

    results = service.search(
        "What is the rent?",
        top_k=1
    )

    assert len(results) == 1


def test_empty_query_rejected():
    service, _ = create_service()

    with pytest.raises(
        ValueError,
        match="Search query cannot be empty"
    ):
        service.search("")


def test_whitespace_query_rejected():
    service, _ = create_service()

    with pytest.raises(
        ValueError,
        match="Search query cannot be empty"
    ):
        service.search("   ")