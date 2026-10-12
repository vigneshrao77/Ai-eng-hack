from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import get_settings
from app.core.logging import logger, mask_secrets
from app.db.session import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing ModernRx datastores and database schema...")
    init_db()
    logger.info("ModernRx Backend ready for service.")
    yield
    logger.info("ModernRx Backend shutting down.")


app = FastAPI(
    title="ModernRx API",
    description="GxP-Aware AI Application Modernization Advisor for Pharma IT/Cloud",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming {request.method} {request.url.path}")
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        logger.error(f"Unhandled server error on {request.url.path}: {mask_secrets(str(exc))}")
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal server error occurred.", "path": request.url.path},
        )


from app.api.routes_health import router as health_router
from app.api.routes_auth import router as auth_router
from app.api.routes_projects import router as projects_router
from app.api.routes_jobs import router as jobs_router
from app.api.routes_audit import router as audit_router
from app.api.routes_twin import router as twin_router
from app.api.routes_gxp import router as gxp_router
from app.api.routes_readiness import router as readiness_router
from app.api.routes_decomp import router as decomp_router
from app.api.routes_council import router as council_router
from app.api.routes_approvals import router as approvals_router
from app.api.routes_roadmap import router as roadmap_router
from app.api.routes_evidence import router as evidence_router

# Register Core Routes
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(jobs_router)
app.include_router(audit_router)
app.include_router(twin_router)
app.include_router(gxp_router)
app.include_router(readiness_router)
app.include_router(decomp_router)
app.include_router(council_router)
app.include_router(approvals_router)
app.include_router(roadmap_router)
app.include_router(evidence_router)


@app.get("/")
def get_root():
    return {
        "name": "ModernRx API",
        "description": "AI-Powered Application Modernization Advisor for Pharma IT/Cloud",
        "docs_url": "/docs",
        "status": "online",
        "version": "1.0.0",
    }
