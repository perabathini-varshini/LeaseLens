from src.document_parser import extract_document
from src.section_detector import detect_sections
from src.clause_extractor import extract_clauses
from src.relationship_detector import detect_relationships


DOC_PATH = "data/leases/sample_lease.pdf"


def main():

    print("\nEXTRACTING DOCUMENT")
    print("=" * 60)

    units = extract_document(DOC_PATH)

    print(f"Document units extracted: {len(units)}")

    print("\nDETECTING SECTIONS")
    print("=" * 60)

    sections = detect_sections(units)

    print(f"Sections detected: {len(sections)}")

    print("\nEXTRACTING CLAUSES")
    print("=" * 60)

    clauses = extract_clauses(sections)

    print(f"Clauses extracted: {len(clauses)}")

    print("\nDETECTING RELATIONSHIPS")
    print("=" * 60)

    relationships = detect_relationships(clauses)

    print(f"Relationships detected: {len(relationships)}")

    for relationship in relationships:
        print("\n" + "-" * 40)
        print(
            f"Relationship: {relationship['source']} --> "
            f"{relationship['target']}"
        )
        print(
            f"Type: {relationship['type']}"
        )
        print(
            f"Reason: {relationship['reason']}"
        )

if __name__ == "__main__":
    main()