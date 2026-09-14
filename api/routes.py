from pathlib import Path
import shutil

from fastapi import APIRouter, UploadFile, File, HTTPException

from src.pipeline import run_pipeline


BASE_DIR = Path(__file__).resolve().parent.parent

LEASES_DIR = BASE_DIR / "data" / "leases"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

LEASES_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


router = APIRouter(
    prefix="/api",
    tags=["LeaseLens API"]
)


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
    input_path = LEASES_DIR / safe_filename

    output_name = (
        Path(safe_filename).stem
        + "_pipeline.json"
    )

    output_path = PROCESSED_DIR / output_name

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
        "filename": safe_filename,
        "result": frontend_result
    }