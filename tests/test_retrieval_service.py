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
        match="Search query must be a non-empty string"
    ):
        service.search("")


def test_whitespace_query_rejected():
    service, _ = create_service()

    with pytest.raises(
        ValueError,
        match="Search query must be a non-empty string"
    ):
        service.search("   ")


@pytest.mark.parametrize(
    "query",
    [
        None,
        123,
        [],
    ],
)
def test_invalid_query_type_rejected(query):
    service, embedding_client = create_service()

    with pytest.raises(
        ValueError,
        match="Search query must be a non-empty string",
    ):
        service.search(query)

    assert embedding_client.last_text is None

@pytest.mark.parametrize(
    "top_k",
    [
        0,
        -1,
        1.5,
        "5",
        None,
        True,
    ],
)
def test_invalid_top_k_rejected_before_embedding(top_k):
    service, embedding_client = create_service()

    with pytest.raises(ValueError):
        service.search(
            "What is the rent?",
            top_k=top_k,
        )

    assert embedding_client.last_text is None


@pytest.mark.parametrize(
    "min_similarity",
    [
        -1.0,
        0.0,
        0.5,
        1.0,
    ],
)
def test_search_accepts_valid_similarity_threshold(
    min_similarity
):
    service, _ = create_service()

    results = service.search(
        "What is the rent?",
        min_similarity=min_similarity
    )

    assert isinstance(results, list)


@pytest.mark.parametrize(
    "min_similarity",
    [
        -1.1,
        1.1,
        float("nan"),
        float("inf"),
        "0.5",
        None,
        True,
        10**1000,
    ],
)
def test_search_rejects_invalid_similarity_threshold(
    min_similarity
):
    service, embedding_client = create_service()

    with pytest.raises(
        ValueError,
        match="min_similarity must be a finite number",
    ):
        service.search(
            "What is the security deposit?",
            min_similarity=min_similarity,
        )

    assert embedding_client.last_text is None


def test_search_passes_similarity_threshold_to_retriever():
    service, _ = create_service()
    captured = {}

    def fake_search(query_embedding, top_k=5, min_similarity=-1.0):
        captured["query_embedding"] = query_embedding
        captured["top_k"] = top_k
        captured["min_similarity"] = min_similarity
        return []

    service.retriever.search = fake_search

    results = service.search(
        "What is the rent?",
        top_k=3,
        min_similarity=0.65,
    )

    assert results == []
    assert captured["top_k"] == 3
    assert captured["min_similarity"] == 0.65
    assert captured["query_embedding"] is not None
