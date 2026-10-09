from src.chunker import create_chunks


def create_clause():
    return {
        "clause_id": "CLAUSE-001",
        "section_number": "1",
        "section_title": "PARTIES",
        "clause_type": "PARTIES",
        "text": (
            "This Lease Agreement is entered into "
            "between the landlord and the tenant. "
            "The parties agree to the terms and "
            "conditions stated in this agreement."
        ),
        "source": "sample_lease.pdf",
        "location": "page 1",
        "location_type": "page"
    }


def test_create_chunks():
    clauses = [create_clause()]

    chunks = create_chunks(
        clauses,
        max_words=10
    )

    assert len(chunks) > 1


def test_chunk_preserves_traceability():
    clauses = [create_clause()]

    chunks = create_chunks(
        clauses,
        max_words=10
    )

    first_chunk = chunks[0]

    assert first_chunk["chunk_id"] == "CHUNK-001"
    assert first_chunk["clause_id"] == "CLAUSE-001"
    assert first_chunk["section_number"] == "1"
    assert first_chunk["section_title"] == "PARTIES"
    assert first_chunk["clause_type"] == "PARTIES"
    assert first_chunk["source"] == "sample_lease.pdf"
    assert first_chunk["location"] == "page 1"
    assert first_chunk["location_type"] == "page"


def test_chunk_text_respects_max_words():
    clauses = [create_clause()]

    chunks = create_chunks(
        clauses,
        max_words=10
    )

    for chunk in chunks:
        assert len(chunk["text"].split()) <= 10


def test_empty_clause_is_skipped():
    clauses = [
        {
            "clause_id": "CLAUSE-001",
            "text": ""
        }
    ]

    chunks = create_chunks(clauses)

    assert chunks == []


def test_invalid_max_words():
    clauses = [create_clause()]

    try:
        create_chunks(
            clauses,
            max_words=0
        )
        assert False
    except ValueError as exc:
        assert (
            str(exc)
            == "max_words must be greater than zero."
        )