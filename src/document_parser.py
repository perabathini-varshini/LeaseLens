import fitz


def extract_pdf_text(file_path: str) -> list[dict]:
    """
    Extract text from a PDF page by page.

    Returns:
        A list of dictionaries containing:
        - page number
        - extracted text
    """

    pages = []

    document = fitz.open(file_path)

    for page_number, page in enumerate(document, start=1):

        text = page.get_text("text")

        pages.append({
            "page": page_number,
            "text": text
        })

    document.close()

    return pages

from docx import Document


def extract_docx_text(file_path: str) -> list[dict]:
    """
    Extract text from a DOCX document paragraph by paragraph.

    Returns:
        A list of dictionaries containing:
        - paragraph number
        - extracted text
    """

    paragraphs = []

    try:
        document = Document(file_path)

    except Exception as error:

        raise ValueError(
            f"Could not open DOCX: {error}"
        )

    for paragraph_number, paragraph in enumerate(
        document.paragraphs,
        start=1
    ):

        text = paragraph.text.strip()

        if text:

            paragraphs.append({
                "paragraph": paragraph_number,
                "text": text
            })

    return paragraphs

def normalize_pdf_pages(
    pages: list[dict],
    source: str
) -> list[dict]:
    """
    Convert PDF extraction output into
    LeaseLens' common document format.
    """

    documents = []

    for page in pages:

        documents.append({
            "source": source,
            "file_type": "pdf",
            "location": page["page"],
            "location_type": "page",
            "text": page["text"].strip()
        })

    return documents

def normalize_docx_paragraphs(
    paragraphs: list[dict],
    source: str
) -> list[dict]:
    """
    Convert DOCX extraction output into
    LeaseLens' common document format.
    """

    documents = []

    for paragraph in paragraphs:

        documents.append({
            "source": source,
            "file_type": "docx",
            "location": paragraph["paragraph"],
            "location_type": "paragraph",
            "text": paragraph["text"].strip()
        })

    return documents

from pathlib import Path


def extract_document(file_path: str) -> list[dict]:
    """
    Extract and normalize a supported document.

    Supported formats:
        - PDF
        - DOCX
    """

    path = Path(file_path).resolve()

    if not path.exists():
        raise ValueError(
            f"Document not found: {path}"
        )

    extension = path.suffix.lower()

    if extension == ".pdf":

        pages = extract_pdf_text(str(path))

        return normalize_pdf_pages(
            pages,
            path.name
        )

    elif extension == ".docx":

        paragraphs = extract_docx_text(str(path))

        return normalize_docx_paragraphs(
            paragraphs,
            path.name
        )

    else:

        raise ValueError(
            f"Unsupported document type: {extension}"
        )