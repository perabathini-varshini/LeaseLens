from src.document_parser import extract_document
from src.text_cleaner import clean_text
from src.section_detector import detect_sections


document_path = "data/leases/sample_lease.pdf"


print("\nEXTRACTING DOCUMENT")
print("=" * 60)

documents = extract_document(document_path)


# Clean extracted text
for document in documents:
    document["text"] = clean_text(document["text"])


print(f"Document units extracted: {len(documents)}")


print("\nDETECTING SECTIONS")
print("=" * 60)

sections = detect_sections(documents)


print(f"Sections detected: {len(sections)}")


for section in sections:

    print("\n" + "=" * 60)

    print(
        f"SECTION {section['section_number']}: "
        f"{section['title']}"
    )

    print("=" * 60)

    print(f"Source: {section['source']}")

    print(
        f"Location: "
        f"{section['location_type']} "
        f"{section['location']}"
    )

    print("\nContent:")

    print(section["text"])