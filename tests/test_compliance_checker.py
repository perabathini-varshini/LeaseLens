import json

from src.compliance_checker import check_compliance


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


def test_compliant_rent():
    standards = load_standards()

    clauses = [
        {
            "clause_id": "CLAUSE-002",
            "section_title": "RENT",
            "clause_type": "RENT",
            "text": (
                "The Tenant shall pay a "
                "monthly rent of INR 50,000."
            )
        }
    ]

    results = check_compliance(
        clauses,
        standards
    )

    assert results[0]["status"] == "COMPLIANT"


def test_non_compliant_security_deposit():
    standards = load_standards()

    clauses = [
        {
            "clause_id": "CLAUSE-003",
            "section_title": "SECURITY DEPOSIT",
            "clause_type": "SECURITY_DEPOSIT",
            "text": (
                "The Tenant shall provide a "
                "security deposit of INR 100,000."
            )
        }
    ]

    results = check_compliance(
        clauses,
        standards
    )

    assert results[0]["status"] == "NON_COMPLIANT"


def test_compliant_termination():
    standards = load_standards()

    clauses = [
        {
            "clause_id": "CLAUSE-007",
            "section_title": "TERMINATION",
            "clause_type": "TERMINATION",
            "text": (
                "Either party may terminate "
                "the lease with 30 days notice."
            )
        }
    ]

    results = check_compliance(
        clauses,
        standards
    )

    assert results[0]["status"] == "COMPLIANT"


def test_non_compliant_termination():
    standards = load_standards()

    clauses = [
        {
            "clause_id": "CLAUSE-008",
            "section_title": "TERMINATION",
            "clause_type": "TERMINATION",
            "text": (
                "Either party may terminate "
                "the lease with 15 days notice."
            )
        }
    ]

    results = check_compliance(
        clauses,
        standards
    )

    assert results[0]["status"] == "NON_COMPLIANT"


def test_review_when_rent_amount_missing():
    standards = load_standards()

    clauses = [
        {
            "clause_id": "CLAUSE-009",
            "section_title": "RENT",
            "clause_type": "RENT",
            "text": (
                "The Tenant shall pay rent "
                "monthly."
            )
        }
    ]

    results = check_compliance(
        clauses,
        standards
    )

    # Current rent rule does not require
    # an amount, so this should currently
    # remain compliant.
    assert results[0]["status"] == "COMPLIANT"