import pytest
import fitz

from docx import Document

from src.document_parser import extract_document


def test_extract_valid_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"

    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "Monthly rent is Rs. 25,000.")
    document.save(pdf_path)
    document.close()

    result = extract_document(str(pdf_path))

    assert len(result) == 1
    assert result[0]["file_type"] == "pdf"
    assert "Monthly rent" in result[0]["text"]


def test_extract_valid_docx(tmp_path):
    docx_path = tmp_path / "sample.docx"

    document = Document()
    document.add_paragraph("Monthly rent is Rs. 25,000.")
    document.save(docx_path)

    result = extract_document(str(docx_path))

    assert len(result) == 1
    assert result[0]["file_type"] == "docx"
    assert "Monthly rent" in result[0]["text"]


def test_missing_document():
    with pytest.raises(ValueError, match="Document not found"):
        extract_document("missing_lease.pdf")


def test_corrupted_pdf(tmp_path):
    pdf_path = tmp_path / "corrupted.pdf"
    pdf_path.write_bytes(b"This is not a valid PDF.")

    with pytest.raises(ValueError, match="Could not open PDF"):
        extract_document(str(pdf_path))


def test_corrupted_docx(tmp_path):
    docx_path = tmp_path / "corrupted.docx"
    docx_path.write_bytes(b"This is not a valid DOCX.")

    with pytest.raises(ValueError, match="Could not open DOCX"):
        extract_document(str(docx_path))


def test_unsupported_document_type(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("Some lease content.")

    with pytest.raises(ValueError, match="Unsupported document type"):
        extract_document(str(file_path))


def test_empty_pdf(tmp_path):
    pdf_path = tmp_path / "empty.pdf"

    document = fitz.open()
    document.new_page()
    document.save(pdf_path)
    document.close()

    with pytest.raises(ValueError, match="no extractable text"):
        extract_document(str(pdf_path))


def test_empty_docx(tmp_path):
    docx_path = tmp_path / "empty.docx"

    document = Document()
    document.save(docx_path)

    with pytest.raises(ValueError, match="no extractable text"):
        extract_document(str(docx_path))

def test_whitespace_only_docx(tmp_path):
    docx_path = tmp_path / "whitespace.docx"

    document = Document()
    document.add_paragraph("   ")
    document.add_paragraph("\t")
    document.save(docx_path)

    with pytest.raises(ValueError, match="no extractable text"):
        extract_document(str(docx_path))
