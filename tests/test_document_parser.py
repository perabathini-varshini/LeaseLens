from src.document_parser import extract_document


pdf_path = "data/leases/sample_lease.pdf"
docx_path = "data/leases/sample_lease.docx"


print("\nPDF TEST")
print("=" * 60)

pdf_documents = extract_document(pdf_path)

for document in pdf_documents:

    print(
        f"{document['location_type'].upper()} "
        f"{document['location']}"
    )

    print(f"Source: {document['source']}")
    print(f"Text: {document['text'][:100]}")
    print("-" * 60)


print("\nDOCX TEST")
print("=" * 60)

docx_documents = extract_document(docx_path)

for document in docx_documents:

    print(
        f"{document['location_type'].upper()} "
        f"{document['location']}"
    )

    print(f"Source: {document['source']}")
    print(f"Text: {document['text'][:100]}")
    print("-" * 60)