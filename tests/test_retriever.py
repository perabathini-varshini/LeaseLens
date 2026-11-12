import math
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
        match="top_k must be a positive integer"
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

def test_search_returns_empty_when_no_results_meet_threshold():
    class FakeVectorStore:
        records = [
            {
                "chunk": {
                    "chunk_id": "CHUNK-001",
                    "text": "Monthly rent is 25000."
                },
                "embedding": [1.0, 0.0, 0.0]
            }
        ]

    retriever = VectorRetriever(FakeVectorStore())

    results = retriever.search(
        [0.0, 1.0, 0.0],
        min_similarity=0.5
    )

    assert results == []

def test_search_keeps_results_above_threshold():
    class FakeVectorStore:
        records = [
            {
                "chunk": {
                    "chunk_id": "CHUNK-001",
                    "text": "Monthly rent is 25000."
                },
                "embedding": [1.0, 0.0, 0.0]
            }
        ]

    retriever = VectorRetriever(FakeVectorStore())

    results = retriever.search(
        [1.0, 0.0, 0.0],
        min_similarity=0.5
    )

    assert len(results) == 1
    assert results[0]["score"] >= 0.5


def test_invalid_similarity_threshold_is_rejected():
    class FakeVectorStore:
        records = []

    retriever = VectorRetriever(FakeVectorStore())

    for threshold in (
        -1.1,
        1.1,
        math.nan,
        math.inf,
        -math.inf,
    ):
        with pytest.raises(ValueError):
            retriever.search(
                [1.0, 0.0, 0.0],
                min_similarity=threshold,
            )

@pytest.mark.parametrize(
    "vector",
    [
        [float("nan"), 1.0],
        [float("inf"), 1.0],
        [float("-inf"), 1.0],
        ["invalid", 1.0],
    ],
)
def test_cosine_similarity_rejects_invalid_vector_values(vector):
    with pytest.raises(ValueError):
        VectorRetriever.cosine_similarity(
            vector,
            [1.0, 0.0],
        )


def test_cosine_similarity_rejects_non_finite_result():
    with pytest.raises(ValueError):
        VectorRetriever.cosine_similarity(
            [1e308, 1e308],
            [1e308, 1e308],
        )


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
def test_search_rejects_invalid_top_k(top_k):
    class FakeVectorStore:
        records = []

    retriever = VectorRetriever(FakeVectorStore())

    with pytest.raises(ValueError):
        retriever.search(
            [1.0, 0.0],
            top_k=top_k,
        )

@pytest.mark.parametrize(
    "threshold",
    [
        "0.5",
        None,
        True,
    ],
)
def test_search_rejects_invalid_similarity_threshold_type(
    threshold,
):
    class FakeVectorStore:
        records = []

    retriever = VectorRetriever(FakeVectorStore())

    with pytest.raises(ValueError):
        retriever.search(
            [1.0, 0.0],
            min_similarity=threshold,
        )


def test_search_skips_record_with_missing_embedding():
    class FakeVectorStore:
        records = [
            {
                "chunk": {
                    "chunk_id": "CHUNK-BAD",
                    "text": "Malformed record",
                }
            },
            {
                "chunk": {
                    "chunk_id": "CHUNK-GOOD",
                    "text": "Valid record",
                },
                "embedding": [1.0, 0.0],
            },
        ]

    retriever = VectorRetriever(FakeVectorStore())

    results = retriever.search([1.0, 0.0])

    assert len(results) == 1
    assert results[0]["chunk"]["chunk_id"] == "CHUNK-GOOD"


def test_search_skips_record_with_invalid_embedding():
    class FakeVectorStore:
        records = [
            {
                "chunk": {
                    "chunk_id": "CHUNK-BAD",
                    "text": "Invalid embedding",
                },
                "embedding": [float("nan"), 0.0],
            },
            {
                "chunk": {
                    "chunk_id": "CHUNK-GOOD",
                    "text": "Valid record",
                },
                "embedding": [1.0, 0.0],
            },
        ]

    retriever = VectorRetriever(FakeVectorStore())

    results = retriever.search([1.0, 0.0])

    assert len(results) == 1
    assert results[0]["chunk"]["chunk_id"] == "CHUNK-GOOD"

def test_search_skips_non_dictionary_records():
    class FakeVectorStore:
        records = [
            None,
            "invalid record",
            {
                "chunk": {
                    "chunk_id": "CHUNK-GOOD",
                    "text": "Valid record",
                },
                "embedding": [1.0, 0.0],
            },
        ]

    retriever = VectorRetriever(FakeVectorStore())

    results = retriever.search([1.0, 0.0])

    assert len(results) == 1
    assert results[0]["chunk"]["chunk_id"] == "CHUNK-GOOD"

@pytest.mark.parametrize(
    "query_embedding",
    [
        "invalid",
        None,
        123,
        [1.0, None],
        [1.0, float("nan")],
        [1.0, float("inf")],
        [True, 1.0],
    ],
)
def test_search_rejects_invalid_query_embedding(
    query_embedding,
):
    retriever = VectorRetriever(
        vector_store=type("Store", (), {"records": []})()
    )

    with pytest.raises(ValueError):
        retriever.search(query_embedding)