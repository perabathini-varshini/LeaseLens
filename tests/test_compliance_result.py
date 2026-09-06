import pytest

from src.compliance_result import (
    create_compliance_result
)


def test_create_compliant_result():

    clause = {
        "clause_id": "CLAUSE-001",
        "clause_type": "RENT",
        "section_title": "RENT"
    }

    result = create_compliance_result(
        clause=clause,
        status="COMPLIANT",
        reason="Rent clause complies with the standard.",
        standard_key="rent"
    )

    assert result["clause_id"] == "CLAUSE-001"
    assert result["clause_type"] == "RENT"
    assert result["section_title"] == "RENT"
    assert result["status"] == "COMPLIANT"
    assert result["standard_key"] == "rent"


def test_create_non_compliant_result():

    clause = {
        "clause_id": "CLAUSE-002",
        "clause_type": "TERMINATION",
        "section_title": "TERMINATION"
    }

    result = create_compliance_result(
        clause=clause,
        status="NON_COMPLIANT",
        reason="Notice period is below the minimum.",
        standard_key="termination"
    )

    assert result["status"] == "NON_COMPLIANT"
    assert result["standard_key"] == "termination"


def test_create_review_result():

    clause = {
        "clause_id": "CLAUSE-003",
        "clause_type": "SECURITY_DEPOSIT",
        "section_title": "SECURITY DEPOSIT"
    }

    result = create_compliance_result(
        clause=clause,
        status="REVIEW",
        reason="Could not determine the deposit amount.",
        standard_key="security_deposit"
    )

    assert result["status"] == "REVIEW"


def test_invalid_status():

    clause = {
        "clause_id": "CLAUSE-004",
        "clause_type": "RENT",
        "section_title": "RENT"
    }

    with pytest.raises(ValueError):

        create_compliance_result(
            clause=clause,
            status="INVALID",
            reason="Invalid test status.",
            standard_key="rent"
        )