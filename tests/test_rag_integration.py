from src.indexing_service import IndexingService
from src.retrieval_service import RetrievalService
from src.vector_store import LocalVectorStore


class FakeEmbeddingClient:
    def embed(self, text: str) -> list[float]:
        text = text.lower()

        if "security deposit" in text:
            return [0.0, 1.0, 0.0]

        if "rent" in text:
            return [1.0, 0.0, 0.0]

        return [0.0, 0.0, 1.0]


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


def test_index_persist_reload_and_retrieve(tmp_path):
    index_path = tmp_path / "lease_vectors.json"

    original_store = LocalVectorStore(
        str(index_path)
    )

    embedding_client = FakeEmbeddingClient()

    indexing_service = IndexingService(
        vector_store=original_store,
        embedding_client=embedding_client
    )

    index_result = indexing_service.index_clauses(
        sample_clauses()
    )

    assert index_result["chunks_indexed"] == 2
    assert index_path.exists()

    # Simulate a fresh application loading the saved index.
    reloaded_store = LocalVectorStore(
        str(index_path)
    )

    reloaded_store.load()

    assert reloaded_store.count() == 2

    retrieval_service = RetrievalService(
        vector_store=reloaded_store,
        embedding_client=embedding_client
    )

    results = retrieval_service.search(
        "What is the security deposit?",
        top_k=1
    )

    assert len(results) == 1

    best_match = results[0]["chunk"]

    assert best_match["clause_id"] == "CLAUSE-002"
    assert best_match["section_title"] == "SECURITY DEPOSIT"
    assert best_match["source"] == "sample_lease.pdf"
    assert best_match["location"] == 2
    assert "₹40,000" in best_match["text"]


def test_reloaded_index_preserves_all_chunk_metadata(tmp_path):
    index_path = tmp_path / "lease_vectors.json"

    store = LocalVectorStore(
        str(index_path)
    )

    indexing_service = IndexingService(
        vector_store=store,
        embedding_client=FakeEmbeddingClient()
    )

    indexing_service.index_clauses(
        sample_clauses()
    )

    reloaded_store = LocalVectorStore(
        str(index_path)
    )

    reloaded_store.load()

    deposit_record = next(
        record
        for record in reloaded_store.records
        if record["chunk"]["clause_id"] == "CLAUSE-002"
    )

    chunk = deposit_record["chunk"]

    assert chunk["chunk_id"] == "CHUNK-002"
    assert chunk["clause_type"] == "SECURITY_DEPOSIT"
    assert chunk["location_type"] == "page"
    assert deposit_record["embedding"] == [0.0, 1.0, 0.0]