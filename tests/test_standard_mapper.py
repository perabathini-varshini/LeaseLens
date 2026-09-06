import json

from src.standard_mapper import (
    map_clause_to_standard,
    map_clauses_to_standards
)


STANDARD_PATH = (
    "data/standards/company_standards.json"
)


def load_standards():

    with open(
        STANDARD_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def test_rent_mapping():

    standards = load_standards()

    clause = {
        "clause_id": "CLAUSE-001",
        "clause_type": "RENT"
    }

    result = map_clause_to_standard(
        clause,
        standards
    )

    assert result["matched"] is True
    assert result["standard_key"] == "rent"
    assert result["standard"] == standards["rent"]


def test_security_deposit_mapping():

    standards = load_standards()

    clause = {
        "clause_id": "CLAUSE-002",
        "clause_type": "SECURITY_DEPOSIT"
    }

    result = map_clause_to_standard(
        clause,
        standards
    )

    assert result["matched"] is True
    assert result["standard_key"] == "security_deposit"


def test_termination_mapping():

    standards = load_standards()

    clause = {
        "clause_id": "CLAUSE-003",
        "clause_type": "TERMINATION"
    }

    result = map_clause_to_standard(
        clause,
        standards
    )

    assert result["matched"] is True
    assert result["standard_key"] == "termination"


def test_unknown_clause_mapping():

    standards = load_standards()

    clause = {
        "clause_id": "CLAUSE-999",
        "clause_type": "UNKNOWN"
    }

    result = map_clause_to_standard(
        clause,
        standards
    )

    assert result["matched"] is False
    assert result["standard"] == {}


def test_multiple_clause_mapping():

    standards = load_standards()

    clauses = [
        {
            "clause_id": "CLAUSE-001",
            "clause_type": "RENT"
        },
        {
            "clause_id": "CLAUSE-002",
            "clause_type": "TERMINATION"
        }
    ]

    results = map_clauses_to_standards(
        clauses,
        standards
    )

    assert len(results) == 2
    assert results[0]["matched"] is True
    assert results[1]["matched"] is True