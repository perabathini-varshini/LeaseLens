import json
from pathlib import Path

from src.document_parser import extract_document
from src.text_cleaner import clean_text
from src.section_detector import detect_sections
from src.clause_extractor import extract_clauses
from src.relationship_detector import detect_relationships

from src.standard_mapper import map_clauses_to_standards
from src.compliance_checker import check_compliance

from src.gemini_explainer import GeminiExplainer

from src.structured_json import (
    create_structured_json,
    save_structured_json
)


BASE_DIR = Path(__file__).resolve().parent.parent

STANDARDS_PATH = (
    BASE_DIR
    / "data"
    / "standards"
    / "company_standards.json"
)


def load_company_standards() -> dict:
    """
    Load company-defined compliance standards.
    """

    with open(
        STANDARDS_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def run_pipeline(
    input_path: str,
    output_path: str
) -> dict:

    """
    Run the complete LeaseLens document intelligence pipeline.

    Flow:

        Document
        -> Clean Text
        -> Sections
        -> Clauses
        -> Relationships
        -> Company Standards
        -> Standard Mapping
        -> Compliance Checking
        -> Structured JSON
    """

    print("\n" + "=" * 60)
    print("LEASELENS DOCUMENT INTELLIGENCE PIPELINE")
    print("=" * 60)

    # --------------------------------------------------
    # 1. Extract document
    # --------------------------------------------------

    print("\n[1/7] Extracting document...")

    documents = extract_document(input_path)

    print(
        f"       Document units extracted: "
        f"{len(documents)}"
    )

    # --------------------------------------------------
    # 2. Clean extracted text
    # --------------------------------------------------

    print("\n[2/7] Cleaning text...")

    for document in documents:

        document["text"] = clean_text(
            document["text"]
        )

    print("       Text cleaning completed.")

    # --------------------------------------------------
    # 3. Detect sections
    # --------------------------------------------------

    print("\n[3/7] Detecting sections...")

    sections = detect_sections(documents)

    print(
        f"       Sections detected: "
        f"{len(sections)}"
    )

    # --------------------------------------------------
    # 4. Extract clauses
    # --------------------------------------------------

    print("\n[4/7] Extracting clauses...")

    clauses = extract_clauses(sections)

    print(
        f"       Clauses extracted: "
        f"{len(clauses)}"
    )

    # --------------------------------------------------
    # 5. Detect relationships
    # --------------------------------------------------

    print("\n[5/7] Detecting relationships...")

    relationships = detect_relationships(
        clauses
    )

    print(
        f"       Relationships detected: "
        f"{len(relationships)}"
    )

    # --------------------------------------------------
    # 6. Load standards + compliance
    # --------------------------------------------------

    print("\n[6/7] Checking company compliance...")

    standards = load_company_standards()

    # Map each clause to its company standard
    standard_mappings = map_clauses_to_standards(
        clauses,
        standards
    )

    # Check each clause against the standard
    compliance_results = check_compliance(
        clauses,
        standards
    )

        # Generate AI explanations for compliance results

    print(
        "\n       Generating Gemini explanations..."
    )

    try:
        gemini_explainer = GeminiExplainer()
        gemini_init_error = None

    except Exception as exc:
        gemini_explainer = None
        gemini_init_error = str(exc)

    for compliance_result in compliance_results:

        if gemini_explainer is None:
            compliance_result["ai_explanation"] = (
                "AI explanation unavailable: "
                f"{gemini_init_error}"
            )
            continue

        clause_id = compliance_result.get(
            "clause_id"
        )

        clause = next(
            (
                item
                for item in clauses
                if item.get("clause_id") == clause_id
            ),
            None
        )

        if clause is None:
            compliance_result["ai_explanation"] = (
                "AI explanation unavailable because "
                "the related clause could not be found."
            )
            continue

        standard_key = compliance_result.get(
            "standard_key"
        )

        standard = standards.get(
            standard_key,
            {}
        )

        try:
            compliance_result["ai_explanation"] = (
                gemini_explainer.explain_compliance(
                    clause,
                    compliance_result,
                    standard
                )
            )

        except Exception as exc:
            compliance_result["ai_explanation"] = (
                "AI explanation unavailable: "
                f"{str(exc)}"
            )

    print(
        f"       Standards loaded: "
        f"{len(standards)}"
    )

    print(
        f"       Standard mappings: "
        f"{len(standard_mappings)}"
    )

    print(
        f"       Compliance results: "
        f"{len(compliance_results)}"
    )

    # --------------------------------------------------
    # 7. Create structured JSON
    # --------------------------------------------------

    print("\n[7/7] Creating structured JSON...")

    structured_data = create_structured_json(
        documents,
        sections,
        clauses,
        relationships
    )

    # Add Phase 3 business intelligence
    structured_data["standards"] = standards
    structured_data["standard_mappings"] = standard_mappings
    structured_data["compliance"] = compliance_results

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