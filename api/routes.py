from pathlib import Path
import shutil

from fastapi import APIRouter, UploadFile, File, HTTPException

from src.pipeline import run_pipeline

from uuid import UUID, uuid4

from pydantic import BaseModel

from src.indexing_service import IndexingService
from src.vector_store import LocalVectorStore
from src.rag_service import RAGService

BASE_DIR = Path(__file__).resolve().parent.parent

LEASES_DIR = BASE_DIR / "data" / "leases"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
VECTOR_DIR = PROCESSED_DIR / "vectors"

LEASES_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DIR.mkdir(parents=True, exist_ok=True)


router = APIRouter(
    prefix="/api",
    tags=["LeaseLens API"]
)

class AskRequest(BaseModel):
    lease_id: str
    question: str

@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "LeaseLens"
    }


@router.post("/analyze")
def analyze_lease(file: UploadFile = File(...)):
    """
    Upload and analyze a lease document.

    Supported formats:
        - PDF
        - DOCX
    """

    # -----------------------------------------
    # 1. Validate filename
    # -----------------------------------------
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided."
        )

    safe_filename = Path(file.filename).name

    if not safe_filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename."
        )

    filename_lower = safe_filename.lower()

    # -----------------------------------------
    # 2. Validate file type
    # -----------------------------------------
    extension = Path(safe_filename).suffix.lower()

    if extension not in {".pdf", ".docx"}:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Please upload a PDF or DOCX file."
            )
        )

    # -----------------------------------------
    # 3. Reject duplicate or confusing extensions
    # -----------------------------------------
    filename_without_extension = Path(safe_filename).stem.lower()

    if filename_without_extension.endswith((".pdf", ".docx")):
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid filename. "
                "Please upload a file with only one PDF or DOCX extension."
            )
        )

    # -----------------------------------------
    # 4. Prepare paths
    # -----------------------------------------
    lease_id = str(uuid4())

    input_path = LEASES_DIR / f"{lease_id}{extension}"

    output_path = (
        PROCESSED_DIR / f"{lease_id}_pipeline.json"
    )

    vector_path = VECTOR_DIR / f"{lease_id}.json"

    # -----------------------------------------
    # 5. Save uploaded file
    # -----------------------------------------
    try:
        with input_path.open("wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        # -----------------------------------------
        # 6. Reject empty files
        # -----------------------------------------
        if input_path.stat().st_size == 0:
            raise HTTPException(
                status_code=400,
                detail="The uploaded file is empty."
            )

        # -----------------------------------------
        # 7. Run document processing pipeline
        # -----------------------------------------
        result = run_pipeline(
            str(input_path),
            str(output_path)
        )

        rag_indexing = {
            "status": "failed",
            "chunks_indexed": 0,
            "message": "RAG indexing did not complete."
        }

        try:
            vector_store = LocalVectorStore(
                str(vector_path)
            )

            indexing_service = IndexingService(
                vector_store
            )

            indexing_result = indexing_service.index_clauses(
                result.get("clauses", [])
            )

            rag_indexing = {
                "status": "success",
                "chunks_indexed": indexing_result["chunks_indexed"],
                "message": "Lease indexed successfully."
            }

        except Exception as exc:
            rag_indexing = {
                "status": "failed",
                "chunks_indexed": 0,
                "message": f"RAG indexing failed: {exc}"
            }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Lease analysis failed: {str(exc)}"
        )

    finally:
        file.file.close()

    # -----------------------------------------
    # 8. Get compliance results
    # -----------------------------------------
    compliance = result.get(
        "compliance",
        []
    )

    # -----------------------------------------
    # 9. Calculate summary
    # -----------------------------------------
    compliant_count = sum(
        1
        for item in compliance
        if item.get("status") == "COMPLIANT"
    )

    non_compliant_count = sum(
        1
        for item in compliance
        if item.get("status") == "NON_COMPLIANT"
    )

    review_count = sum(
        1
        for item in compliance
        if item.get("status") == "REVIEW"
    )

    # -----------------------------------------
    # 10. Build frontend-friendly result
    # -----------------------------------------
    frontend_result = {
        "filename": safe_filename,

        "summary": {
            "total_clauses": len(
                result.get("clauses", [])
            ),
            "compliant": compliant_count,
            "non_compliant": non_compliant_count,
            "review": review_count
        },

        "clauses": result.get(
            "clauses",
            []
        ),

        "compliance": compliance,

        "relationships": result.get(
            "relationships",
            []
        )
    }

    # -----------------------------------------
    # 11. Return API response
    # -----------------------------------------
    return {
        "status": "success",
        "lease_id": lease_id,
        "filename": safe_filename,
        "rag_indexing": rag_indexing,
        "result": frontend_result
    }

@router.post("/ask")
def ask_lease_question(request: AskRequest):
    if not request.question or not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:
        lease_id = str(UUID(request.lease_id))
    except (ValueError, AttributeError, TypeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid lease ID."
        )

    vector_path = VECTOR_DIR / f"{lease_id}.json"

    if not vector_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="No indexed lease found for this lease ID."
        )

    try:
        vector_store = LocalVectorStore(str(vector_path))
        vector_store.load()

        if vector_store.count() == 0:
            raise HTTPException(
                status_code=404,
                detail="No searchable clauses found for this lease."
            )

        rag_service = RAGService(vector_store)
        result = rag_service.answer(request.question.strip())

        return {
            "status": "success",
            "lease_id": lease_id,
            "question": request.question.strip(),
            "answer": result["answer"],
            "sources": result["sources"]
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Lease question answering failed: {exc}"
        )