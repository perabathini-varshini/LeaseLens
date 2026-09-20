import json

from src.compliance_checker import (
    check_compliance,
    check_maintenance
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

    assert results[0]["status"] == "REVIEW"

    assert (
        "rent amount"
        in results[0]["reason"].lower()
    )


def test_maintenance_major_structural_repairs_assigned_to_landlord():
    standards = load_standards()

    clauses = [
        {
            "clause_id": "CLAUSE-010",
            "section_title": "REPAIRS AND MAINTENANCE",
            "clause_type": "MAINTENANCE",
            "text": (
                "The Tenant shall keep the premises clean "
                "and in good condition. The Landlord shall "
                "be responsible for major structural repairs "
                "unless damage was caused by the Tenant's "
                "negligence or misuse."
            )
        }
    ]

    results = check_compliance(
        clauses,
        standards
    )

    assert results[0]["status"] == "COMPLIANT"


def test_maintenance_landlord_responsible_for_structural_repairs():
    clause = {
        "clause_type": "MAINTENANCE",
        "text": (
            "The tenant is responsible for keeping the premises "
            "clean and in good condition, while the landlord is "
            "responsible for structural repairs."
        )
    }

    standard = {
        "required": True,
        "tenant_responsible_for_major_repairs": False
    }

    result = check_maintenance(
        clause,
        standard
    )

    assert result["status"] == "COMPLIANT"

    assert (
        "matches the company standard"
        in result["reason"]
    )