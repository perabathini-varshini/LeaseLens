import pytest

from src.indexing_service import IndexingService


class FakeEmbeddingClient:
    def embed(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError("Embedding text cannot be empty.")

        return [1.0, 0.0, 0.0]


class FakeVectorStore:
    def __init__(self):
        self.records = []
        self.save_called = False

    def save(self):
        self.save_called = True


def sample_clauses():
    return [
        {
            "clause_id": "CLAUSE-001",
            "section_number": "1",
            "section_title": "RENT",
            "clause_type": "RENT",
            "text": "The monthly rent is ₹25,000.",
            "source": "sample_lease.pdf",
            "location": 1,
            "location_type": "page"
        },
        {
            "clause_id": "CLAUSE-002",
            "section_number": "2",
            "section_title": "SECURITY DEPOSIT",
            "clause_type": "SECURITY_DEPOSIT",
            "text": "The security deposit is ₹40,000.",
            "source": "sample_lease.pdf",
            "location": 2,
            "location_type": "page"
        }
    ]


def create_service():
    store = FakeVectorStore()

    service = IndexingService(
        vector_store=store,
        embedding_client=FakeEmbeddingClient()
    )

    return service, store


def test_index_clauses_creates_embeddings():
    service, store = create_service()

    result = service.index_clauses(
        sample_clauses()
    )

    assert result["chunks_indexed"] == 2
    assert store.save_called
    assert len(store.records) == 2


def test_index_preserves_traceability():
    service, store = create_service()

    service.index_clauses(sample_clauses())

    chunk = store.records[0]["chunk"]

    assert chunk["clause_id"] == "CLAUSE-001"
    assert chunk["section_title"] == "RENT"
    assert chunk["source"] == "sample_lease.pdf"
    assert chunk["location"] == 1


def test_reindex_replaces_old_records():
    service, store = create_service()

    store.records = [
        {
            "chunk": {"chunk_id": "OLD"},
            "embedding": [0.0, 1.0, 0.0]
        }
    ]

    service.index_clauses(sample_clauses())

    assert len(store.records) == 2
    assert all(
        record["chunk"]["chunk_id"] != "OLD"
        for record in store.records
    )


def test_empty_clauses_create_empty_index():
    service, store = create_service()

    result = service.index_clauses([])

    assert result["chunks_indexed"] == 0
    assert store.records == []
    assert store.save_called


def test_embedding_failure_preserves_existing_index():
    service, store = create_service()

    original_records = [
        {
            "chunk": {"chunk_id": "EXISTING"},
            "embedding": [0.0, 1.0, 0.0]
        }
    ]

    store.records = original_records

    class FailingEmbeddingClient:
        def embed(self, text: str) -> list[float]:
            raise RuntimeError("Embedding service unavailable")

    service.embedding_client = FailingEmbeddingClient()

    with pytest.raises(
        RuntimeError,
        match="Embedding service unavailable"
    ):
        service.index_clauses(sample_clauses())

    assert store.records is original_records
    assert not store.save_called


def test_invalid_clauses_input_is_rejected():
    service, _ = create_service()

    with pytest.raises(
        ValueError,
        match="Clauses must be provided as a list."
    ):
        service.index_clauses(None)