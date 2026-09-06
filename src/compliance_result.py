"""
Compliance Result Model for LeaseLens.

Provides a consistent structure for compliance
evaluation results.
"""

from typing import Dict


VALID_STATUSES = {
    "COMPLIANT",
    "NON_COMPLIANT",
    "REVIEW",
}


def create_compliance_result(
    clause: Dict,
    status: str,
    reason: str,
    standard_key: str
) -> Dict:
    """
    Create a standardized compliance result.

    Args:
        clause: Extracted clause information.
        status: Compliance status.
        reason: Explanation for the result.
        standard_key: Company standard used.

    Returns:
        Structured compliance result.
    """

    if status not in VALID_STATUSES:
        raise ValueError(
            f"Invalid compliance status: {status}"
        )

    return {
        "clause_id": clause.get(
            "clause_id"
        ),
        "clause_type": clause.get(
            "clause_type"
        ),
        "section_title": clause.get(
            "section_title"
        ),
        "status": status,
        "reason": reason,
        "standard_key": standard_key,
    }