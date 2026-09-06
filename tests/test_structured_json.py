from src.document_parser import extract_document
from src.text_cleaner import clean_text
from src.section_detector import detect_sections
from src.clause_extractor import extract_clauses
from src.relationship_detector import detect_relationships
from src.structured_json import (
    create_structured_json,
    save_structured_json
)


DOCUMENT_PATH = "data/leases/sample_lease.pdf"

OUTPUT_PATH = "data/processed/sample_lease.json"


print("\n1. EXTRACTING DOCUMENT")
print("=" * 60)

documents = extract_document(DOCUMENT_PATH)

for document in documents:
    document["text"] = clean_text(document["text"])

print(
    f"Document units extracted: "
    f"{len(documents)}"
)


print("\n2. DETECTING SECTIONS")
print("=" * 60)

sections = detect_sections(documents)

print(
    f"Sections detected: "
    f"{len(sections)}"
)


print("\n3. EXTRACTING CLAUSES")
print("=" * 60)

clauses = extract_clauses(sections)

print(
    f"Clauses extracted: "
    f"{len(clauses)}"
)


print("\n4. DETECTING RELATIONSHIPS")
print("=" * 60)

relationships = detect_relationships(clauses)

print(
    f"Relationships detected: "
    f"{len(relationships)}"
)


print("\n5. CREATING STRUCTURED JSON")
print("=" * 60)

structured_data = create_structured_json(
    documents,
    sections,
    clauses,
    relationships
)

print("Structured JSON object created.")


print("\n6. SAVING JSON")
print("=" * 60)

save_structured_json(
    structured_data,
    OUTPUT_PATH
)

print(
    f"Saved to: {OUTPUT_PATH}"
)