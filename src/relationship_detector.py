"""
Relationship Detector for LeaseLens.

Detects meaningful relationships between extracted clauses.
"""

from typing import List, Dict


def detect_relationships(clauses: List[Dict]) -> List[Dict]:
    """
    Detect semantic relationships between clauses.

    Relationships currently supported:
    - APPLIES_TO
    - RELATED_TO
    """

    relationships = []

    for i, source in enumerate(clauses):
        for j, target in enumerate(clauses):

            # Don't relate a clause to itself
            if i == j:
                continue

            source_type = source["clause_type"]
            target_type = target["clause_type"]

            # -------------------------------------------------
            # 1. PARTIES -> contractual obligations
            # -------------------------------------------------
            if source_type == "PARTIES":
                if target_type in {
                    "RENT",
                    "SECURITY_DEPOSIT",
                    "MAINTENANCE",
                    "TERMINATION",
                    "GOVERNING_LAW",
                }:
                    relationships.append({
                        "source": source["clause_id"],
                        "target": target["clause_id"],
                        "type": "APPLIES_TO",
                        "reason": (
                            "The clause identifies the parties involved "
                            "in the agreement."
                        )
                    })

            # -------------------------------------------------
            # 2. RENT <-> SECURITY DEPOSIT
            # -------------------------------------------------
            elif (
                source_type == "RENT"
                and target_type == "SECURITY_DEPOSIT"
            ):
                relationships.append({
                    "source": source["clause_id"],
                    "target": target["clause_id"],
                    "type": "RELATED_TO",
                    "reason": (
                        "Both clauses define financial obligations "
                        "of the tenant."
                    )
                })

            # -------------------------------------------------
            # 3. MAINTENANCE -> TERMINATION
            # -------------------------------------------------
            elif (
                source_type == "MAINTENANCE"
                and target_type == "TERMINATION"
            ):
                relationships.append({
                    "source": source["clause_id"],
                    "target": target["clause_id"],
                    "type": "RELATED_TO",
                    "reason": (
                        "Maintenance obligations may affect the "
                        "continuation or termination of the lease."
                    )
                })

    return relationships