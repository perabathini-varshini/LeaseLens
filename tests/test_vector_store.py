import json

import pytest

from src.vector_store import LocalVectorStore


def create_chunk():
    return {
        "chunk_id": "CHUNK-001",
        "clause_id": "CLAUSE-001",
        "section_number": "1",
        "section_title": "PARTIES",
        "clause_type": "PARTIES",
        "text": (
            "This agreement is between the "
            "landlord and tenant."
        ),
        "source": "sample_lease.pdf",
        "location": "page 1",
        "location_type": "page"
    }


def test_add_record(tmp_path):
    store = LocalVectorStore(
        str(tmp_path / "vectors.json")
    )

    embedding = [0.1, 0.2, 0.3]

    store.add(
        create_chunk(),
        embedding
    )

    assert store.count() == 1
    assert store.records[0]["chunk"]["chunk_id"] == (
        "CHUNK-001"
    )
    assert store.records[0]["embedding"] == embedding


def test_empty_embedding_rejected(tmp_path):
    store = LocalVectorStore(
        str(tmp_path / "vectors.json")
    )

    with pytest.raises(
        ValueError,
        match="Embedding cannot be empty"
    ):
        store.add(
            create_chunk(),
            []
        )


def test_save_store(tmp_path):
    storage_path = tmp_path / "vectors.json"

    store = LocalVectorStore(
        str(storage_path)
    )

    store.add(
        create_chunk(),
        [0.1, 0.2, 0.3]
    )

    store.save()

    assert storage_path.exists()

    with storage_path.open(
        "r",
        encoding="utf-8"
    ) as file:
        data = json.load(file)

    assert len(data) == 1
    assert data[0]["chunk"]["chunk_id"] == (
        "CHUNK-001"
    )


def test_load_store(tmp_path):
    storage_path = tmp_path / "vectors.json"

    first_store = LocalVectorStore(
        str(storage_path)
    )

    first_store.add(
        create_chunk(),
        [0.1, 0.2, 0.3]
    )

    first_store.save()

    second_store = LocalVectorStore(
        str(storage_path)
    )

    second_store.load()

    assert second_store.count() == 1
    assert (
        second_store.records[0]["chunk"]["chunk_id"]
        == "CHUNK-001"
    )
    assert (
        second_store.records[0]["embedding"]
        == [0.1, 0.2, 0.3]
    )


def test_load_missing_store(tmp_path):
    storage_path = tmp_path / "missing.json"

    store = LocalVectorStore(
        str(storage_path)
    )

    store.load()

    assert store.count() == 0


def test_invalid_store_format(tmp_path):
    storage_path = tmp_path / "vectors.json"

    storage_path.write_text(
        json.dumps({"invalid": "format"}),
        encoding="utf-8"
    )

    store = LocalVectorStore(
        str(storage_path)
    )

    with pytest.raises(
        ValueError,
        match="Vector store must contain a list"
    ):
        store.load()