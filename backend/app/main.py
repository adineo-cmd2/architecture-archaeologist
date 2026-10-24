from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.session import Base, engine
import app.models.user  # noqa: F401
import app.models.codebase  # noqa: F401
import app.models.source_file  # noqa: F401
import app.models.analysis_report  # noqa: F401
import app.models.drift_record  # noqa: F401
from app.api.routes import codebase, analysis, report, qa

settings = get_settings()
Base.metadata.create_all(bind=engine)
app = FastAPI(title="Architecture Archaeologist")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://127.0.0.1:4327"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthz():
    return {"ok": True}


app.include_router(codebase.router, prefix="/api/codebase", tags=["codebase"])
app.include_router(analysis.router, prefix="/api/codebase", tags=["analysis"])
app.include_router(report.router, prefix="/api/codebase", tags=["report"])
app.include_router(qa.router, prefix="/api/codebase", tags=["qa"])
