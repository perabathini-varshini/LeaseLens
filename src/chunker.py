def create_chunks(
    clauses: list[dict],
    max_words: int = 120
) -> list[dict]:
    """
    Convert extracted clauses into retrieval-ready chunks.

    Each chunk preserves document traceability so that
    retrieved evidence can be linked back to the original
    lease clause.
    """

    if max_words <= 0:
        raise ValueError(
            "max_words must be greater than zero."
        )

    chunks = []
    chunk_counter = 1

    for clause in clauses:
        text = clause.get("text", "").strip()

        if not text:
            continue

        words = text.split()

        for start in range(
            0,
            len(words),
            max_words
        ):
            chunk_words = words[
                start:start + max_words
            ]

            chunk_text = " ".join(chunk_words)

            chunks.append({
                "chunk_id": (
                    f"CHUNK-{chunk_counter:03d}"
                ),
                "clause_id": clause.get(
                    "clause_id"
                ),
                "section_number": clause.get(
                    "section_number"
                ),
                "section_title": clause.get(
                    "section_title"
                ),
                "clause_type": clause.get(
                    "clause_type"
                ),
                "text": chunk_text,
                "source": clause.get(
                    "source"
                ),
                "location": clause.get(
                    "location"
                ),
                "location_type": clause.get(
                    "location_type"
                )
            })

            chunk_counter += 1

    return chunks