def get_clause_type(section_title: str) -> str:
    """
    Determine a basic clause type from the section title.
    """

    title = section_title.lower()

    if "rent" in title:
        return "RENT"

    if "deposit" in title:
        return "SECURITY_DEPOSIT"

    if "maintenance" in title:
        return "MAINTENANCE"

    if "termination" in title:
        return "TERMINATION"

    if "governing law" in title:
        return "GOVERNING_LAW"

    if "parties" in title:
        return "PARTIES"

    return "OTHER"


def extract_clauses(sections: list[dict]) -> list[dict]:
    """
    Convert detected sections into structured clauses.
    """

    clauses = []

    for index, section in enumerate(sections, start=1):

        clause_type = get_clause_type(
            section["title"]
        )

        clause = {
            "clause_id": f"CLAUSE-{index:03d}",
            "section_number": section["section_number"],
            "section_title": section["title"],
            "clause_type": clause_type,
            "text": section["text"],
            "source": section["source"],
            "location": section["location"],
            "location_type": section["location_type"]
        }

        clauses.append(clause)

    return clauses