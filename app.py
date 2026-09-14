from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from api.routes import router


BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = BASE_DIR / "frontend"


app = FastAPI(
    title="LeaseLens",
    description="AI-Powered Lease Agreement Review & Risk Assistant",
    version="0.1.0"
)


# -----------------------------
# API Routes
# -----------------------------

app.include_router(router)


# -----------------------------
# Frontend
# -----------------------------

app.mount(
    "/static",
    StaticFiles(directory=FRONTEND_DIR),
    name="static"
)


@app.get("/")
def home():
    return FileResponse(
        FRONTEND_DIR / "index.html"
    )