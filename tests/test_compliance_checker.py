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


def main():

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
        },

        {
            "clause_id": "CLAUSE-003",
            "section_title": "SECURITY DEPOSIT",
            "clause_type": "SECURITY_DEPOSIT",
            "text": (
                "The Tenant shall provide a "
                "security deposit of INR 100,000."
            )
        },

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

    print()
    print("=" * 60)
    print("LEASELENS COMPLIANCE CHECK")
    print("=" * 60)

    for result in results:

        print()
        print(
            f"{result['clause_id']} "
            f"-> {result['clause_type']}"
        )

        print(
            f"Status: {result['status']}"
        )

        print(
            f"Reason: {result['reason']}"
        )


if __name__ == "__main__":
    main()