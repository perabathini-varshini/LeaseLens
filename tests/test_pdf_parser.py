from src.document_parser import extract_pdf_text


pdf_path = "data/leases/sample_lease.pdf"

pages = extract_pdf_text(pdf_path)

for page in pages:
    print("=" * 50)
    print(f"PAGE {page['page']}")
    print("=" * 50)
    print(page["text"])