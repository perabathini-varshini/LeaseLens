"""
Compliance Checker for LeaseLens.

Compares extracted lease clauses against
company-defined standards.

Supported checks:
- RENT
- SECURITY_DEPOSIT
- TERMINATION
- MAINTENANCE
- NOTICE
- PROHIBITED_CONDITIONS
"""

import re
from typing import List, Dict


def extract_amount(text: str):
    """
    Extract the first monetary amount from clause text.

    Supports:
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
        60 days notice
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


def check_rent(
    clause: Dict,
    standard: Dict
) -> Dict:
    """
    Check rent clause against company standards.

    Current standard checks:
    - Currency
    - Unilateral rent modification
    """

    text = clause["text"].lower()

    if not text.strip():
        return {
            "status": "REVIEW",
            "reason": (
                "The rent clause is empty "
                "or contains no usable text."
            )
        }

    # Check unilateral modification
    allow_unilateral = standard.get(
        "allow_unilateral_modification"
    )

    unilateral_detected = (
        "unilaterally" in text
        or "unilateral" in text
        or "landlord may modify rent" in text
        or "landlord may increase rent" in text
        or "landlord can modify rent" in text
        or "landlord can increase rent" in text
    )

    if (
        allow_unilateral is False
        and unilateral_detected
    ):
        return {
            "status": "NON_COMPLIANT",
            "reason": (
                "The lease allows unilateral "
                "rent modification, which is "
                "not permitted by the company standard."
            )
        }

    return {
        "status": "COMPLIANT",
        "reason": (
            "Rent clause complies with the "
            "current company standard."
        )
    }


def check_security_deposit(
    clause: Dict,
    standard: Dict
) -> Dict:
    """
    Check security deposit against company standards.

    Checks:
    - Minimum amount
    - Maximum amount
    - Return timeline requirement
    - Forfeiture restriction
    """

    text = clause["text"].lower()

    amount = extract_amount(
        clause["text"]
    )

    minimum = standard.get(
        "min_amount"
    )

    maximum = standard.get(
        "max_amount"
    )

    require_return = standard.get(
        "require_return_timeline"
    )

    allow_forfeiture = standard.get(
        "allow_forfeiture"
    )

    if amount is None:
        return {
            "status": "REVIEW",
            "reason": (
                "Could not determine the "
                "security deposit amount."
            )
        }

    if (
        minimum is not None
        and amount < minimum
    ):
        return {
            "status": "NON_COMPLIANT",
            "reason": (
                f"Security deposit of INR {amount:,} "
                f"is below the minimum required "
                f"amount of INR {minimum:,}."
            )
        }

    if (
        maximum is not None
        and amount > maximum
    ):
        return {
            "status": "NON_COMPLIANT",
            "reason": (
                f"Security deposit of INR {amount:,} "
                f"exceeds the maximum allowed "
                f"amount of INR {maximum:,}."
            )
        }

    if (
        require_return is True
        and "return" not in text
    ):
        return {
            "status": "REVIEW",
            "reason": (
                "A security deposit return "
                "timeline is required but could "
                "not be identified."
            )
        }

    forfeiture_detected = (
        "forfeit" in text
        or "forfeiture" in text
        or "deposit will not be returned" in text
        or "deposit shall not be returned" in text
    )

    if (
        allow_forfeiture is False
        and forfeiture_detected
    ):
        return {
            "status": "NON_COMPLIANT",
            "reason": (
                "The lease contains a security "
                "deposit forfeiture condition, "
                "which is not permitted."
            )
        }

    return {
        "status": "COMPLIANT",
        "reason": (
            f"Security deposit of INR {amount:,} "
            "complies with the company standard."
        )
    }


def check_termination(
    clause: Dict,
    standard: Dict
) -> Dict:
    """
    Check termination notice period.

    Current standard:
    - Minimum: 30 days
    - Maximum: 60 days
    """

    notice_days = extract_notice_days(
        clause["text"]
    )

    minimum = standard.get(
        "minimum_notice_days"
    )

    maximum = standard.get(
        "maximum_notice_days"
    )

    if notice_days is None:
        return {
            "status": "REVIEW",
            "reason": (
                "Could not determine the "
                "termination notice period."
            )
        }

    if (
        minimum is not None
        and notice_days < minimum
    ):
        return {
            "status": "NON_COMPLIANT",
            "reason": (
                f"Notice period of {notice_days} days "
                f"is below the minimum requirement "
                f"of {minimum} days."
            )
        }

    if (
        maximum is not None
        and notice_days > maximum
    ):
        return {
            "status": "NON_COMPLIANT",
            "reason": (
                f"Notice period of {notice_days} days "
                f"exceeds the maximum allowed "
                f"period of {maximum} days."
            )
        }

    return {
        "status": "COMPLIANT",
        "reason": (
            f"Notice period of {notice_days} days "
            "is within the permitted range."
        )
    }


def check_maintenance(
    clause: Dict,
    standard: Dict
) -> Dict:
    """
    Check maintenance responsibility.
    """

    required = standard.get(
        "required"
    )

    tenant_major_repairs = standard.get(
        "tenant_responsible_for_major_repairs"
    )

    text = clause["text"].lower()

    if required is True and not text.strip():
        return {
            "status": "NON_COMPLIANT",
            "reason": (
                "Maintenance responsibility is "
                "required but the clause is empty."
            )
        }

    tenant_responsible = (
        "tenant shall be responsible" in text
        or "tenant is responsible" in text
        or "tenant responsible" in text
    )

    landlord_responsible = (
        "landlord shall be responsible" in text
        or "landlord is responsible" in text
        or "landlord responsible" in text
    )

    if tenant_responsible and landlord_responsible:
        return {
            "status": "REVIEW",
            "reason": (
                "The clause contains conflicting "
                "maintenance responsibilities."
            )
        }

    if not tenant_responsible and not landlord_responsible:
        return {
            "status": "REVIEW",
            "reason": (
                "Could not determine who is responsible "
                "for major repairs."
            )
        }

    actual_responsibility = tenant_responsible

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


def check_notice(
    clause: Dict,
    standard: Dict
) -> Dict:
    """
    Check whether a required notice clause exists.
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
                "Notice clause is not required "
                "by the company standard."
            )
        }

    if text:
        return {
            "status": "COMPLIANT",
            "reason": (
                "Required notice information "
                "is present in the lease."
            )
        }

    return {
        "status": "NON_COMPLIANT",
        "reason": (
            "A notice clause is required "
            "but is missing."
        )
    }


def check_prohibited_conditions(
    clause: Dict,
    standard: Dict
) -> Dict:
    """
    Detect prohibited conditions in a lease clause.

    Supported conditions:
    - Unrestricted landlord entry
    - Deposit forfeiture
    - Unilateral rent modification
    """

    text = clause["text"].lower()

    violations = []

    if standard.get(
        "unrestricted_landlord_entry"
    ):
        unrestricted_entry = (
            "landlord may enter at any time" in text
            or "landlord can enter at any time" in text
            or "landlord may enter without notice" in text
            or "landlord can enter without notice" in text
            or "unrestricted entry" in text
        )

        if unrestricted_entry:
            violations.append(
                "unrestricted landlord entry"
            )

    if standard.get(
        "deposit_forfeiture"
    ):
        forfeiture = (
            "deposit forfeited" in text
            or "deposit forfeiture" in text
            or "deposit will be forfeited" in text
            or "deposit shall be forfeited" in text
        )

        if forfeiture:
            violations.append(
                "deposit forfeiture"
            )

    if standard.get(
        "unilateral_rent_modification"
    ):
        unilateral_rent = (
            "landlord may modify rent" in text
            or "landlord may increase rent" in text
            or "landlord can modify rent" in text
            or "landlord can increase rent" in text
            or "unilateral rent modification" in text
        )

        if unilateral_rent:
            violations.append(
                "unilateral rent modification"
            )

    if violations:
        return {
            "status": "NON_COMPLIANT",
            "reason": (
                "Prohibited condition detected: "
                + ", ".join(violations)
                + "."
            )
        }

    return {
        "status": "COMPLIANT",
        "reason": (
            "No prohibited conditions were "
            "detected in the clause."
        )
    }


def check_clause(
    clause: Dict,
    standards: Dict
) -> Dict:
    """
    Check one clause against the
    appropriate company standard.
    """

    clause_type = clause["clause_type"]

    standard_key = clause_type.lower()

    if standard_key not in standards:
        return {
            "clause_id": clause["clause_id"],
            "clause_type": clause_type,
            "section_title": clause["section_title"],
            "status": "REVIEW",
            "reason": (
                f"No company standard is defined "
                f"for clause type {clause_type}."
            ),
        }

    standard = standards[standard_key]

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

    elif clause_type == "NOTICE":
        result = check_notice(
            clause,
            standard
        )

    elif clause_type == "PROHIBITED_CONDITIONS":
        result = check_prohibited_conditions(
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