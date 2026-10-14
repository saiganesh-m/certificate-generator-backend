from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.db.database import engine, Base
from app import models
from app.routers import certificates, templates, auth

# 1. Automatically create all database tables on server startup (no manual SQL needed!)
Base.metadata.create_all(bind=engine)

# 2. OpenAPI Documentation Metadata & Tag Organization
tags_metadata = [
    {
        "name": "Authentication & Security",
        "description": "Admin access control and passkey verification.",
    },
    {
        "name": "Certificates",
        "description": "Operations for parsing recipient Excel files, generating batch PDF certificates, and verifying QR codes.",
    },
    {
        "name": "Templates",
        "description": "Manage reusable certificate designs, background PDFs, and layout schemas.",
    },
    {
        "name": "System",
        "description": "API health check and diagnostic endpoints.",
    },
]

# 3. Initialize FastAPI Application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="""
## Universal Certificate Studio API 🎓
A production-grade REST API for generating and verifying dynamic certificates.
* **Batch Vector PDF Generation**: Overlay text, auto-shrink fonts, and place QR codes dynamically.
* **Universal QR Verification**: Public verification route supporting dynamic student metadata.
* **Excel & CSV Ingestion**: Parses columns and formats names with acronym preservation.
    """,
    openapi_tags=tags_metadata,
    docs_url="/docs",      # Interactive Swagger UI URL
    redoc_url="/redoc"     # ReDoc alternative documentation URL
)

# 4. Configure CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Mount Static Storage for Template Previews
app.mount("/storage", StaticFiles(directory=settings.STORAGE_DIR), name="storage")

# 6. Include API Routers under the /api/v1 prefix
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(certificates.router, prefix=settings.API_V1_PREFIX)
app.include_router(templates.router, prefix=settings.API_V1_PREFIX)


# 7. System Health Check Endpoint
@app.get("/", tags=["System"], summary="API Root / Health Check")
def root():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "docs_url": "/docs",
        "version": "1.0.0"
    }
