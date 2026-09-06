"""
Improved Clause Retriever for LeaseLens.

Retrieves relevant clauses using:
- keyword matching
- stop-word filtering
- clause-type matching
- weighted scoring
"""

from typing import List, Dict


STOP_WORDS = {
    "what",
    "is",
    "the",
    "a",
    "an",
    "of",
    "to",
    "for",
    "and",
    "in",
    "on",
    "my",
    "how",
    "much",
    "does",
    "do",
    "are",
    "was",
    "this",
    "that",
}


CLAUSE_KEYWORDS = {
    "RENT": {
        "rent",
        "monthly",
        "payment",
        "pay",
        "amount",
    },

    "SECURITY_DEPOSIT": {
        "deposit",
        "security",
        "refundable",
        "advance",
    },

    "MAINTENANCE": {
        "maintenance",
        "repair",
        "repairs",
        "damage",
        "fix",
    },

    "TERMINATION": {
        "termination",
        "terminate",
        "notice",
        "vacate",
        "end",
    },

    "GOVERNING_LAW": {
        "law",
        "jurisdiction",
        "governing",
        "legal",
    },

    "PARTIES": {
        "landlord",
        "tenant",
        "parties",
        "agreement",
    },
}


def normalize_words(text: str) -> set:
    """
    Convert text into normalized keywords.
    """

    words = text.lower().split()

    normalized = set()

    for word in words:

        word = word.strip(
            ".,!?;:()[]{}\"'"
        )

        if word and word not in STOP_WORDS:
            normalized.add(word)

    return normalized


def calculate_score(
    query: str,
    clause: Dict
) -> int:
    """
    Calculate relevance score for a clause.
    """

    query_words = normalize_words(query)

    section_title = clause.get(
        "section_title",
        ""
    ).lower()

    clause_type = clause.get(
        "clause_type",
        ""
    )

    clause_text = clause.get(
        "text",
        ""
    ).lower()

    score = 0

    # -----------------------------------------
    # 1. Direct section title matching
    # -----------------------------------------

    for word in query_words:

        if word in section_title:
            score += 5

    # -----------------------------------------
    # 2. Clause type keyword matching
    # -----------------------------------------

    expected_keywords = CLAUSE_KEYWORDS.get(
        clause_type,
        set()
    )

    for word in query_words:

        if word in expected_keywords:
            score += 3

    # -----------------------------------------
    # 3. Text keyword matching
    # -----------------------------------------

    text_words = normalize_words(
        clause_text
    )

    for word in query_words:

        if word in text_words:
            score += 1

    return score


def retrieve_clauses(
    query: str,
    clauses: List[Dict]
) -> List[Dict]:
    """
    Retrieve clauses relevant to the user's query.

    Clauses are ranked according to their
    relevance score.
    """

    if not query or not clauses:
        return []

    scored_clauses = []

    for clause in clauses:

        score = calculate_score(
            query,
            clause
        )

        if score > 0:

            scored_clauses.append({
                "clause": clause,
                "score": score
            })

    # Highest score first
    scored_clauses.sort(
        key=lambda item: item["score"],
        reverse=True
    )

    return [
        item["clause"]
        for item in scored_clauses
    ]