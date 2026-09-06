"""
Compliance Checker for LeaseLens.

Compares extracted lease clauses against
company-defined standards.

Supported checks:
- RENT
- SECURITY_DEPOSIT
- TERMINATION
- MAINTENANCE
- GOVERNING_LAW
"""

import re
from typing import List, Dict


def extract_amount(text: str):
    """
    Extract the first monetary amount from clause text.

    Supports formats such as:
        INR 50,000
        Rs. 50,000
        ₹50,000
        50000 INR
    """

    patterns = [
        r"(?:INR|Rs\.?|₹)\s*([\d,]+)",
        r"([\d,]+)\s*(?:INR|Rs\.?|₹)",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:
            return int(
                match.group(1).replace(",", "")
            )

    return None


def extract_notice_days(text: str):
    """
    Extract notice period in days.

    Example:
        30 days notice
        thirty days notice
    """

    pattern = r"(\d+)\s*(?:day|days)"

    match = re.search(
        pattern,
        text,
        re.IGNORECASE
    )

    if match:
        return int(match.group(1))

    return None


def check_rent(clause: Dict, standard: Dict) -> Dict:
    """
    Check whether monthly rent is within
    the company standard.
    """

    amount = extract_amount(clause["text"])

    maximum = standard.get(
        "max_monthly_amount"
    )

    if amount is None:
        return {
            "status": "REVIEW",
            "reason": "Could not determine the monthly rent."
        }

    if maximum is None:
        return {
            "status": "REVIEW",
            "reason": "No maximum rent standard is defined."
        }

    if amount <= maximum:
        return {
            "status": "COMPLIANT",
            "reason": (
                f"Monthly rent of INR {amount:,} "
                f"is within the maximum allowed "
                f"amount of INR {maximum:,}."
            )
        }

    return {
        "status": "NON_COMPLIANT",
        "reason": (
            f"Monthly rent of INR {amount:,} "
            f"exceeds the maximum allowed "
            f"amount of INR {maximum:,}."
        )
    }


def check_security_deposit(
    clause: Dict,
    standard: Dict
) -> Dict:
    """
    Check whether the security deposit
    is within the company standard.
    """

    amount = extract_amount(clause["text"])

    maximum = standard.get(
        "max_amount"
    )

    if amount is None:
        return {
            "status": "REVIEW",
            "reason": (
                "Could not determine the "
                "security deposit amount."
            )
        }

    if maximum is None:
        return {
            "status": "REVIEW",
            "reason": (
                "No maximum security deposit "
                "standard is defined."
            )
        }

    if amount <= maximum:
        return {
            "status": "COMPLIANT",
            "reason": (
                f"Security deposit of INR {amount:,} "
                f"is within the maximum allowed "
                f"amount of INR {maximum:,}."
            )
        }

    return {
        "status": "NON_COMPLIANT",
        "reason": (
            f"Security deposit of INR {amount:,} "
            f"exceeds the maximum allowed "
            f"amount of INR {maximum:,}."
        )
    }


def check_termination(
    clause: Dict,
    standard: Dict
) -> Dict:
    """
    Check whether the termination notice
    satisfies the minimum notice requirement.
    """

    notice_days = extract_notice_days(
        clause["text"]
    )

    minimum_days = standard.get(
        "minimum_notice_days"
    )

    if notice_days is None:
        return {
            "status": "REVIEW",
            "reason": (
                "Could not determine the "
                "termination notice period."
            )
        }

    if minimum_days is None:
        return {
            "status": "REVIEW",
            "reason": (
                "No minimum termination "
                "notice standard is defined."
            )
        }

    if notice_days >= minimum_days:
        return {
            "status": "COMPLIANT",
            "reason": (
                f"Notice period of {notice_days} days "
                f"meets the minimum requirement "
                f"of {minimum_days} days."
            )
        }

    return {
        "status": "NON_COMPLIANT",
        "reason": (
            f"Notice period of {notice_days} days "
            f"is below the minimum requirement "
            f"of {minimum_days} days."
        )
    }


def check_maintenance(
    clause: Dict,
    standard: Dict
) -> Dict:
    """
    Check maintenance responsibility.
    """

    tenant_major_repairs = standard.get(
        "tenant_responsible_for_major_repairs"
    )

    text = clause["text"].lower()

    if tenant_major_repairs is None:
        return {
            "status": "REVIEW",
            "reason": (
                "No major-repair responsibility "
                "standard is defined."
            )
        }

    # Detect common wording indicating
    # that the tenant is responsible.
    tenant_responsible = (
        "tenant shall be responsible" in text
        or "tenant is responsible" in text
        or "tenant responsible" in text
    )

    if tenant_responsible:
        actual_responsibility = True
    else:
        actual_responsibility = False

    if actual_responsibility == tenant_major_repairs:
        return {
            "status": "COMPLIANT",
            "reason": (
                "Maintenance responsibility "
                "matches the company standard."
            )
        }

    return {
        "status": "NON_COMPLIANT",
        "reason": (
            "Maintenance responsibility "
            "does not match the company standard."
        )
    }


def check_governing_law(
    clause: Dict,
    standard: Dict
) -> Dict:
    """
    Check whether governing law information
    is present.
    """

    required = standard.get(
        "required",
        False
    )

    text = clause["text"].strip()

    if not required:
        return {
            "status": "COMPLIANT",
            "reason": (
                "Governing law is not required "
                "by the company standard."
            )
        }

    if text:
        return {
            "status": "COMPLIANT",
            "reason": (
                "Governing law information "
                "is present in the lease."
            )
        }

    return {
        "status": "NON_COMPLIANT",
        "reason": (
            "Governing law information "
            "is required but missing."
        )
    }


def check_clause(
    clause: Dict,
    standards: Dict
) -> Dict:
    """
    Check one clause against the appropriate
    company standard.
    """

    clause_type = clause["clause_type"]

    standard = standards.get(
        clause_type.lower(),
        {}
    )

    if clause_type == "RENT":
        result = check_rent(
            clause,
            standard
        )

    elif clause_type == "SECURITY_DEPOSIT":
        result = check_security_deposit(
            clause,
            standard
        )

    elif clause_type == "TERMINATION":
        result = check_termination(
            clause,
            standard
        )

    elif clause_type == "MAINTENANCE":
        result = check_maintenance(
            clause,
            standard
        )

    elif clause_type == "GOVERNING_LAW":
        result = check_governing_law(
            clause,
            standard
        )

    else:
        result = {
            "status": "REVIEW",
            "reason": (
                f"No compliance rule exists "
                f"for clause type {clause_type}."
            )
        }

    return {
        "clause_id": clause["clause_id"],
        "clause_type": clause_type,
        "section_title": clause["section_title"],
        "status": result["status"],
        "reason": result["reason"],
    }


def check_compliance(
    clauses: List[Dict],
    standards: Dict
) -> List[Dict]:
    """
    Check all extracted clauses against
    company standards.

    Returns a list of compliance results.
    """

    results = []

    for clause in clauses:

        result = check_clause(
            clause,
            standards
        )

        results.append(result)

    return results