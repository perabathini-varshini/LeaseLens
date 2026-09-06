from src.document_parser import extract_docx_text


docx_path = "data/leases/sample_lease.docx"

paragraphs = extract_docx_text(docx_path)


for paragraph in paragraphs:

    print("=" * 50)

    print(f"PARAGRAPH {paragraph['paragraph']}")

    print("=" * 50)

    print(paragraph["text"])