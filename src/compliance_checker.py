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


# ============================================================
# Utility Functions
# ============================================================

def extract_amount(text: str):
    """
    Extract the first monetary amount from clause text.

    Supports:
        INR 50,000
        Rs. 50,000
        ₹50,000
        50000 INR
    """

    if not text:
        return None

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

    Examples:
        30 days notice
        60 days written notice
    """

    if not text:
        return None

    pattern = r"(\d+)\s*days?"

    match = re.search(
        pattern,
        text,
        re.IGNORECASE
    )

    if match:
        return int(match.group(1))

    return None


def has_text(text: str) -> bool:
    """Check whether clause contains usable text."""
    return bool(text and text.strip())


# ============================================================
# RENT
# ============================================================

def check_rent(
    clause: Dict,
    standard: Dict
) -> Dict:
    """
    Check rent clause against company standards.

    Checks:
    - Rent amount exists
    - Currency
    - Unilateral rent modification
    """

    original_text = clause.get("text", "")
    text = original_text.lower()

    if not has_text(original_text):
        return {
            "status": "REVIEW",
            "reason": (
                "The rent clause is empty "
                "or contains no usable text."
            )
        }

    amount = extract_amount(original_text)

    if amount is None:
        return {
            "status": "REVIEW",
            "reason": (
                "A rent amount could not be "
                "identified in the lease."
            )
        }

    allow_unilateral = standard.get(
        "allow_unilateral_modification"
    )

    unilateral_patterns = [
        "unilaterally",
        "unilateral rent modification",
        "landlord may modify rent",
        "landlord may increase rent",
        "landlord can modify rent",
        "landlord can increase rent",
        "landlord may change the rent",
        "landlord can change the rent",
        "landlord may revise the rent",
        "landlord can revise the rent",
    ]

    unilateral_detected = any(
        pattern in text
        for pattern in unilateral_patterns
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
            f"Rent amount of INR {amount:,} "
            "is specified and no prohibited "
            "unilateral rent modification was detected."
        )
    }


# ============================================================
# SECURITY DEPOSIT
# ============================================================

def check_security_deposit(
    clause: Dict,
    standard: Dict
) -> Dict:
    """
    Check security deposit against company standards.

    Checks:
    - Minimum amount
    - Maximum amount
    - Return requirement
    - Return timeline
    - Forfeiture
    """

    original_text = clause.get("text", "")
    text = original_text.lower()

    if not has_text(original_text):
        return {
            "status": "REVIEW",
            "reason": (
                "The security deposit clause "
                "is empty."
            )
        }

    amount = extract_amount(original_text)

    minimum = standard.get("min_amount")
    maximum = standard.get("max_amount")

    require_return = standard.get(
        "require_return_timeline",
        False
    )

    allow_forfeiture = standard.get(
        "allow_forfeiture",
        False
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

    # --------------------------------------------------------
    # Check return timeline
    # --------------------------------------------------------

    if require_return is True:

        return_detected = (
            "return" in text
            or "refunded" in text
            or "refund" in text
            or "repaid" in text
        )

        timeline_detected = bool(
            re.search(
                r"\b(within|after|before)\s+\d+\s+days?\b",
                text
            )
            or re.search(
                r"\b\d+\s+days?\s+(of|after)\b",
                text
            )
        )

        if not return_detected or not timeline_detected:
            return {
                "status": "REVIEW",
                "reason": (
                    "The company standard requires "
                    "a security deposit return timeline, "
                    "but a clear return period could "
                    "not be identified."
                )
            }

    # --------------------------------------------------------
    # Check forfeiture
    # --------------------------------------------------------

    forfeiture_detected = (
        "forfeit" in text
        or "forfeiture" in text
        or "deposit will not be returned" in text
        or "deposit shall not be returned" in text
        or "deposit will be forfeited" in text
        or "deposit shall be forfeited" in text
        or "security deposit will be forfeited" in text
        or "security deposit shall be forfeited" in text
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
            "is within the permitted amount range "
            "and contains no prohibited forfeiture condition."
        )
    }


# ============================================================
# TERMINATION
# ============================================================

def check_termination(
    clause: Dict,
    standard: Dict
) -> Dict:
    """
    Check termination notice period.

    Checks:
    - Minimum notice period
    - Maximum notice period
    """

    original_text = clause.get("text", "")

    if not has_text(original_text):
        return {
            "status": "REVIEW",
            "reason": (
                "The termination clause "
                "is empty."
            )
        }

    notice_days = extract_notice_days(
        original_text
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


# ============================================================
# MAINTENANCE
# ============================================================

def check_maintenance(
    clause: Dict,
    standard: Dict
) -> Dict:
    """
    Check maintenance responsibility.

    Important distinction:
    - Routine cleaning and maintenance
    - Major or structural repairs

    The company standard controls responsibility
    for major or structural repairs.
    """

    original_text = clause.get("text", "")
    text = original_text.lower()

    required = standard.get(
        "required",
        False
    )

    tenant_major_repairs = standard.get(
        "tenant_responsible_for_major_repairs",
        False
    )

    # --------------------------------------------------------
    # Check empty clause
    # --------------------------------------------------------

    if not has_text(original_text):

        if required is True:
            return {
                "status": "NON_COMPLIANT",
                "reason": (
                    "Maintenance responsibility is "
                    "required but the clause is empty."
                )
            }

        return {
            "status": "COMPLIANT",
            "reason": (
                "Maintenance responsibility is "
                "not required by the company standard."
            )
        }

    # --------------------------------------------------------
    # Detect major or structural repair language
    # --------------------------------------------------------

    major_repair_terms = [
        "major repair",
        "major repairs",
        "structural repair",
        "structural repairs",
        "major structural repair",
        "major structural repairs",
        "structural damage",
        "major damage",
    ]

    major_repair_mentioned = any(
        term in text
        for term in major_repair_terms
    )

    # --------------------------------------------------------
    # Detect tenant responsibility
    # --------------------------------------------------------

    tenant_major_repair_patterns = [
        "tenant shall be responsible for major repairs",
        "tenant is responsible for major repairs",
        "tenant responsible for major repairs",
        "tenant shall handle major repairs",

        "tenant shall be responsible for structural repairs",
        "tenant is responsible for structural repairs",
        "tenant responsible for structural repairs",
        "tenant shall handle structural repairs",

        "tenant shall be responsible for major structural repairs",
        "tenant is responsible for major structural repairs",
        "tenant responsible for major structural repairs",
        "tenant shall handle major structural repairs",

        "tenant must pay for major repairs",
        "tenant must pay for structural repairs",
        "tenant shall pay for major repairs",
        "tenant shall pay for structural repairs",
    ]

    # --------------------------------------------------------
    # Detect landlord responsibility
    # --------------------------------------------------------

    landlord_major_repair_patterns = [
        "landlord shall be responsible for major repairs",
        "landlord is responsible for major repairs",
        "landlord responsible for major repairs",
        "landlord shall handle major repairs",

        "landlord shall be responsible for structural repairs",
        "landlord is responsible for structural repairs",
        "landlord responsible for structural repairs",
        "landlord shall handle structural repairs",

        "landlord shall be responsible for major structural repairs",
        "landlord is responsible for major structural repairs",
        "landlord responsible for major structural repairs",
        "landlord shall handle major structural repairs",

        "landlord must pay for major repairs",
        "landlord must pay for structural repairs",
        "landlord shall pay for major repairs",
        "landlord shall pay for structural repairs",
    ]

    tenant_major = any(
        pattern in text
        for pattern in tenant_major_repair_patterns
    )

    landlord_major = any(
        pattern in text
        for pattern in landlord_major_repair_patterns
    )

    # --------------------------------------------------------
    # No clear responsibility found
    # --------------------------------------------------------

    if not tenant_major and not landlord_major:

        if major_repair_mentioned:
            return {
                "status": "REVIEW",
                "reason": (
                    "Major or structural repairs are "
                    "mentioned, but responsibility for "
                    "them could not be clearly determined."
                )
            }

        return {
            "status": "REVIEW",
            "reason": (
                "The clause describes maintenance or "
                "cleaning responsibilities, but does not "
                "clearly specify responsibility for major repairs."
            )
        }

    # --------------------------------------------------------
    # Conflicting responsibility
    # --------------------------------------------------------

    if tenant_major and landlord_major:
        return {
            "status": "REVIEW",
            "reason": (
                "The clause assigns major or structural "
                "repair responsibility to both the tenant "
                "and landlord."
            )
        }

    # --------------------------------------------------------
    # Compare with company standard
    # --------------------------------------------------------

    actual_tenant_responsibility = tenant_major

    if (
        actual_tenant_responsibility
        == tenant_major_repairs
    ):
        return {
            "status": "COMPLIANT",
            "reason": (
                "Responsibility for major or structural "
                "repairs matches the company standard."
            )
        }

    return {
        "status": "NON_COMPLIANT",
        "reason": (
            "Responsibility for major or structural "
            "repairs does not match the company standard."
        )
    }


# ============================================================
# NOTICE
# ============================================================

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

    text = clause.get(
        "text",
        ""
    ).strip()

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


# ============================================================
# PROHIBITED CONDITIONS
# ============================================================

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

    original_text = clause.get(
        "text",
        ""
    )

    text = original_text.lower()

    violations = []

    # --------------------------------------------------------
    # Unrestricted landlord entry
    # --------------------------------------------------------

    if standard.get(
        "unrestricted_landlord_entry",
        False
    ):

        unrestricted_entry_patterns = [
            "landlord may enter at any time",
            "landlord can enter at any time",
            "landlord may enter without notice",
            "landlord can enter without notice",
            "landlord may enter the premises at any time",
            "landlord can enter the premises at any time",
            "landlord may enter the property at any time",
            "landlord can enter the property at any time",
            "unrestricted entry",
        ]

        if any(
            pattern in text
            for pattern in unrestricted_entry_patterns
        ):
            violations.append(
                "unrestricted landlord entry"
            )

    # --------------------------------------------------------
    # Deposit forfeiture
    # --------------------------------------------------------

    if standard.get(
        "deposit_forfeiture",
        False
    ):

        forfeiture_patterns = [
            "deposit forfeited",
            "deposit forfeiture",
            "deposit will be forfeited",
            "deposit shall be forfeited",
            "security deposit will be forfeited",
            "security deposit shall be forfeited",
            "security deposit forfeited",
        ]

        if any(
            pattern in text
            for pattern in forfeiture_patterns
        ):
            violations.append(
                "deposit forfeiture"
            )

    # --------------------------------------------------------
    # Unilateral rent modification
    # --------------------------------------------------------

    if standard.get(
        "unilateral_rent_modification",
        False
    ):

        unilateral_rent_patterns = [
            "landlord may modify rent",
            "landlord may increase rent",
            "landlord can modify rent",
            "landlord can increase rent",
            "landlord may change the rent",
            "landlord can change the rent",
            "landlord may revise the rent",
            "landlord can revise the rent",
            "unilateral rent modification",
        ]

        if any(
            pattern in text
            for pattern in unilateral_rent_patterns
        ):
            violations.append(
                "unilateral rent modification"
            )

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

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


# ============================================================
# CLAUSE DISPATCHER
# ============================================================

def check_clause(
    clause: Dict,
    standards: Dict
) -> Dict:
    """
    Check one clause against the
    appropriate company standard.
    """

    clause_type = clause.get(
        "clause_type",
        ""
    )

    standard_key = clause_type.lower()

    # --------------------------------------------------------
    # Check whether a standard exists
    # --------------------------------------------------------

    if standard_key not in standards:

        return {
            "clause_id": clause.get(
                "clause_id"
            ),
            "clause_type": clause_type,
            "section_title": clause.get(
                "section_title"
            ),
            "status": "REVIEW",
            "reason": (
                "No company standard is defined "
                f"for clause type {clause_type}."
            ),
        }

    standard = standards[
        standard_key
    ]

    # --------------------------------------------------------
    # Select the correct compliance rule
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Return standardized result
    # --------------------------------------------------------

    return {
        "clause_id": clause.get(
            "clause_id"
        ),
        "clause_type": clause_type,
        "section_title": clause.get(
            "section_title"
        ),
        "status": result["status"],
        "reason": result["reason"],
    }


# ============================================================
# ALL CLAUSES
# ============================================================

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