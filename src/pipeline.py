from src.document_parser import extract_document
from src.text_cleaner import clean_text
from src.section_detector import detect_sections
from src.clause_extractor import extract_clauses
from src.relationship_detector import detect_relationships
from src.structured_json import (
    create_structured_json,
    save_structured_json
)


def run_pipeline(input_path: str, output_path: str) -> dict:
    """
    Run the complete LeaseLens document intelligence pipeline.

    Flow:
        Document
        -> Clean Text
        -> Sections
        -> Clauses
        -> Relationships
        -> Structured JSON
    """

    print("\n" + "=" * 60)
    print("LEASELENS DOCUMENT INTELLIGENCE PIPELINE")
    print("=" * 60)

    # --------------------------------------------------
    # 1. Extract document
    # --------------------------------------------------

    print("\n[1/5] Extracting document...")

    documents = extract_document(input_path)

    print(
        f"       Document units extracted: "
        f"{len(documents)}"
    )

    # --------------------------------------------------
    # 2. Clean extracted text
    # --------------------------------------------------

    print("\n[2/5] Cleaning text...")

    for document in documents:
        document["text"] = clean_text(
            document["text"]
        )

    print("       Text cleaning completed.")

    # --------------------------------------------------
    # 3. Detect sections
    # --------------------------------------------------

    print("\n[3/5] Detecting sections...")

    sections = detect_sections(documents)

    print(
        f"       Sections detected: "
        f"{len(sections)}"
    )

    # --------------------------------------------------
    # 4. Extract clauses
    # --------------------------------------------------

    print("\n[4/5] Extracting clauses...")

    clauses = extract_clauses(sections)

    print(
        f"       Clauses extracted: "
        f"{len(clauses)}"
    )

    # --------------------------------------------------
    # 5. Detect relationships
    # --------------------------------------------------

    print("\n[5/5] Detecting relationships...")

    relationships = detect_relationships(
        clauses
    )

    print(
        f"       Relationships detected: "
        f"{len(relationships)}"
    )

    # --------------------------------------------------
    # Create structured JSON
    # --------------------------------------------------

    print("\nCreating structured JSON...")

    structured_data = create_structured_json(
        documents,
        sections,
        clauses,
        relationships
    )

    # --------------------------------------------------
    # Save structured JSON
    # --------------------------------------------------

    save_structured_json(
        structured_data,
        output_path
    )

    print(
        f"\nStructured JSON saved to:\n"
        f"       {output_path}"
    )

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)

    return structured_data