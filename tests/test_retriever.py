import pytest

from src.retriever import VectorRetriever


class FakeVectorStore:
    def __init__(self, records):
        self.records = records


def create_record(
    chunk_id,
    text,
    embedding
):
    return {
        "chunk": {
            "chunk_id": chunk_id,
            "clause_id": chunk_id.replace(
                "CHUNK",
                "CLAUSE"
            ),
            "text": text
        },
        "embedding": embedding
    }


def test_cosine_similarity_identical_vectors():
    similarity = VectorRetriever.cosine_similarity(
        [1, 0, 0],
        [1, 0, 0]
    )

    assert similarity == pytest.approx(1.0)


def test_cosine_similarity_orthogonal_vectors():
    similarity = VectorRetriever.cosine_similarity(
        [1, 0],
        [0, 1]
    )

    assert similarity == pytest.approx(0.0)


def test_cosine_similarity_opposite_vectors():
    similarity = VectorRetriever.cosine_similarity(
        [1, 0],
        [-1, 0]
    )

    assert similarity == pytest.approx(-1.0)


def test_empty_vector_rejected():
    with pytest.raises(
        ValueError,
        match="Vectors cannot be empty"
    ):
        VectorRetriever.cosine_similarity(
            [],
            [1, 2]
        )


def test_dimension_mismatch_rejected():
    with pytest.raises(
        ValueError,
        match="same dimensions"
    ):
        VectorRetriever.cosine_similarity(
            [1, 2],
            [1, 2, 3]
        )


def test_zero_magnitude_rejected():
    with pytest.raises(
        ValueError,
        match="zero magnitude"
    ):
        VectorRetriever.cosine_similarity(
            [0, 0],
            [1, 2]
        )


def test_search_returns_highest_similarity_first():
    store = FakeVectorStore([
        create_record(
            "CHUNK-001",
            "Parties",
            [1, 0, 0]
        ),
        create_record(
            "CHUNK-002",
            "Rent",
            [0, 1, 0]
        ),
        create_record(
            "CHUNK-003",
            "Security deposit",
            [0, 0, 1]
        )
    ])

    retriever = VectorRetriever(store)

    results = retriever.search(
        [0, 0, 1],
        top_k=3
    )

    assert len(results) == 3

    assert (
        results[0]["chunk"]["chunk_id"]
        == "CHUNK-003"
    )

    assert results[0]["score"] == pytest.approx(
        1.0
    )


def test_search_respects_top_k():
    store = FakeVectorStore([
        create_record(
            "CHUNK-001",
            "One",
            [1, 0, 0]
        ),
        create_record(
            "CHUNK-002",
            "Two",
            [0, 1, 0]
        ),
        create_record(
            "CHUNK-003",
            "Three",
            [0, 0, 1]
        )
    ])

    retriever = VectorRetriever(store)

    results = retriever.search(
        [1, 0, 0],
        top_k=2
    )

    assert len(results) == 2

    assert (
        results[0]["chunk"]["chunk_id"]
        == "CHUNK-001"
    )


def test_empty_query_rejected():
    store = FakeVectorStore([])

    retriever = VectorRetriever(store)

    with pytest.raises(
        ValueError,
        match="Query embedding cannot be empty"
    ):
        retriever.search([])


def test_invalid_top_k_rejected():
    store = FakeVectorStore([])

    retriever = VectorRetriever(store)

    with pytest.raises(
        ValueError,
        match="top_k must be greater than zero"
    ):
        retriever.search(
            [1, 0, 0],
            top_k=0
        )


def test_empty_store_returns_empty_results():
    store = FakeVectorStore([])

    retriever = VectorRetriever(store)

    results = retriever.search(
        [1, 0, 0],
        top_k=5
    )

    assert results == []