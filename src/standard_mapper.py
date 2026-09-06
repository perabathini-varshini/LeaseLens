"""
Standard Mapper for LeaseLens.

Maps extracted clause types to the corresponding
company-defined compliance standards.
"""

from typing import Dict


def map_clause_to_standard(
    clause: Dict,
    standards: Dict
) -> Dict:
    """
    Find the company standard associated with a clause.

    Returns:
        A dictionary containing:
        - clause_id
        - clause_type
        - standard_key
        - standard
        - matched
    """

    clause_type = clause.get(
        "clause_type",
        ""
    )

    standard_key = clause_type.lower()

    standard = standards.get(
        standard_key
    )

    if standard is None:
        return {
            "clause_id": clause.get("clause_id"),
            "clause_type": clause_type,
            "standard_key": standard_key,
            "standard": {},
            "matched": False
        }

    return {
        "clause_id": clause.get("clause_id"),
        "clause_type": clause_type,
        "standard_key": standard_key,
        "standard": standard,
        "matched": True
    }


def map_clauses_to_standards(
    clauses: list[Dict],
    standards: Dict
) -> list[Dict]:
    """
    Map all extracted clauses to their
    corresponding company standards.
    """

    mappings = []

    for clause in clauses:

        mapping = map_clause_to_standard(
            clause,
            standards
        )

        mappings.append(mapping)

    return mappings