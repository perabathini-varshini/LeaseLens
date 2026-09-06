from src.pipeline import run_pipeline


INPUT_PATH = "data/leases/realistic_lease_test.docx"
OUTPUT_PATH = "data/processed/realistic_lease_pipeline.json"


print("\nStarting LeaseLens pipeline...")

data = run_pipeline(
    INPUT_PATH,
    OUTPUT_PATH
)

print("\nPipeline verification")
print("=" * 60)

print(
    "Document source:",
    data["document"]["source"]
)

print(
    "Document units:",
    data["document"]["document_units"]
)

print(
    "Sections:",
    len(data["sections"])
)

print(
    "Clauses:",
    len(data["clauses"])
)

print(
    "Relationships:",
    len(data["relationships"])
)

print("\nVerification completed successfully.")