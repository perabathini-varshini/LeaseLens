import json


def create_structured_json(
    documents: list[dict],
    sections: list[dict],
    clauses: list[dict],
    relationships: list[dict]
) -> dict:
    """
    Combine all document intelligence into one
    structured JSON-compatible dictionary.
    """

    structured_data = {
        "document": {
            "source": documents[0]["source"] if documents else None,
            "document_units": len(documents)
        },

        "sections": sections,

        "clauses": clauses,

        "relationships": relationships
    }

    return structured_data


def save_structured_json(
    data: dict,
    output_path: str
):
    """
    Save structured lease data as a JSON file.
    """

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )