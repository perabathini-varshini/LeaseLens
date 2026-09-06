from src.clause_retriever import retrieve_clauses


clauses = [
    {
        "clause_id": "CLAUSE-001",
        "section_title": "PARTIES",
        "clause_type": "PARTIES",
        "text": "This agreement is between the landlord and tenant."
    },

    {
        "clause_id": "CLAUSE-002",
        "section_title": "RENT",
        "clause_type": "RENT",
        "text": "The Tenant shall pay a monthly rent of INR 50,000."
    },

    {
        "clause_id": "CLAUSE-003",
        "section_title": "SECURITY DEPOSIT",
        "clause_type": "SECURITY_DEPOSIT",
        "text": "The Tenant shall pay a security deposit of INR 100,000."
    }
]


query = "What is the monthly rent?"


results = retrieve_clauses(
    query,
    clauses
)


print("QUERY")
print("=" * 60)
print(query)


print("\nRETRIEVED CLAUSES")
print("=" * 60)


for rank, clause in enumerate(
    results,
    start=1
):

    print(
        f"{rank}. "
        f"{clause['clause_id']} -> "
        f"{clause['section_title']}"
    )