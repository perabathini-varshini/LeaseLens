from src.compliance_checker import (
    check_compliance
)


def test_missing_rent_text_returns_review():

    standards = {
        "rent": {
            "currency": "INR",
            "allow_unilateral_modification": False
        }
    }

    clauses = [
        {
            "clause_id": "CLAUSE-001",
            "section_title": "RENT",
            "clause_type": "RENT",
            "text": ""
        }
    ]

    results = check_compliance(
        clauses,
        standards
    )

    assert results[0]["status"] == "REVIEW"


def test_missing_termination_notice_returns_review():

    standards = {
        "termination": {
            "minimum_notice_days": 30,
            "maximum_notice_days": 60
        }
    }

    clauses = [
        {
            "clause_id": "CLAUSE-002",
            "section_title": "TERMINATION",
            "clause_type": "TERMINATION",
            "text": (
                "Either party may terminate "
                "the lease."
            )
        }
    ]

    results = check_compliance(
        clauses,
        standards
    )

    assert results[0]["status"] == "REVIEW"


def test_ambiguous_maintenance_returns_review():

    standards = {
        "maintenance": {
            "required": True,
            "tenant_responsible_for_major_repairs": False
        }
    }

    clauses = [
        {
            "clause_id": "CLAUSE-003",
            "section_title": "MAINTENANCE",
            "clause_type": "MAINTENANCE",
            "text": (
                "Maintenance shall be handled "
                "as required."
            )
        }
    ]

    results = check_compliance(
        clauses,
        standards
    )

    assert results[0]["status"] == "REVIEW"


def test_missing_security_deposit_amount_returns_review():

    standards = {
        "security_deposit": {
            "currency": "INR",
            "min_amount": 30000,
            "max_amount": 50000,
            "require_return_timeline": True,
            "allow_forfeiture": False
        }
    }

    clauses = [
        {
            "clause_id": "CLAUSE-004",
            "section_title": "SECURITY DEPOSIT",
            "clause_type": "SECURITY_DEPOSIT",
            "text": (
                "The Tenant shall provide "
                "a security deposit."
            )
        }
    ]

    results = check_compliance(
        clauses,
        standards
    )

    assert results[0]["status"] == "REVIEW"


def test_missing_standard_returns_review():

    standards = {}

    clauses = [
        {
            "clause_id": "CLAUSE-005",
            "section_title": "RENT",
            "clause_type": "RENT",
            "text": (
                "The Tenant shall pay "
                "monthly rent."
            )
        }
    ]

    results = check_compliance(
        clauses,
        standards
    )

    assert results[0]["status"] == "REVIEW"