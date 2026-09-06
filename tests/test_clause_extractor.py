from src.document_parser import extract_document
from src.text_cleaner import clean_text
from src.section_detector import detect_sections
from src.clause_extractor import extract_clauses


document_path = "data/leases/sample_lease.pdf"


print("\nEXTRACTING DOCUMENT")
print("=" * 60)

documents = extract_document(document_path)

for document in documents:
    document["text"] = clean_text(document["text"])

print(f"Document units extracted: {len(documents)}")


print("\nDETECTING SECTIONS")
print("=" * 60)

sections = detect_sections(documents)

print(f"Sections detected: {len(sections)}")


print("\nEXTRACTING CLAUSES")
print("=" * 60)

clauses = extract_clauses(sections)

print(f"Clauses extracted: {len(clauses)}")


for clause in clauses:

    print("\n" + "-" * 60)

    print(f"Clause ID: {clause['clause_id']}")

    print(
        f"Section: "
        f"{clause['section_number']}. "
        f"{clause['section_title']}"
    )

    print(f"Type: {clause['clause_type']}")

    print(f"Source: {clause['source']}")

    print(
        f"Location: "
        f"{clause['location_type']} "
        f"{clause['location']}"
    )

    print("\nText:")

    print(clause["text"])