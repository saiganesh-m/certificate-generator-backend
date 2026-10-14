import os
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application Settings
    Pydantic automatically reads values from environment variables or a .env file.
    If not found in environment, it falls back to the default values below.
    """

    # 1. Project Info
    PROJECT_NAME: str = "Universal Certificate Studio API"
    API_V1_PREFIX: str = "/api/v1"

    # 2. Database Connection URL
    # - Local development: SQLite file 'certificates.db' in the server root
    # - Production deployment: set DATABASE_URL in .env to:
    #   "mysql+pymysql://username:password@hostname:3306/database_name"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./certificates.db")

    # 3. Verification URL Template
    # This is the base URL encoded into the QR code on every certificate.
    # When scanned by a phone, it directs to this URL + certificate_id.
    VERIFICATION_BASE_URL: str = os.getenv(
        "VERIFICATION_BASE_URL", 
        "http://localhost:5173/verify?id="
    )

    # 4. CORS (Cross-Origin Resource Sharing)
    # The browser blocks frontend (port 5173) from calling backend (port 8000)
    # unless the backend explicitly lists the frontend URL in CORS_ORIGINS.
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",  # Vite default local dev server
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    # 5. File Storage Paths
    # We resolve paths relative to this file so it works on any OS (Windows/Linux/Mac)
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    STORAGE_DIR: str = os.path.join(BASE_DIR, "storage")
    TEMPLATES_DIR: str = os.path.join(STORAGE_DIR, "templates")
    OUTPUTS_DIR: str = os.path.join(STORAGE_DIR, "outputs")

    # 6. Security & Admin Authentication
    ADMIN_SECRET_KEY: str = os.getenv("ADMIN_SECRET_KEY", "zap10x-admin-2026")

    class Config:
        # If an .env file exists in the server folder, load variables from it
        env_file = ".env"
        case_sensitive = True


# Create a single shared instance to be imported by other files
settings = Settings()

# Automatically create the storage directories on startup if they don't exist
os.makedirs(settings.TEMPLATES_DIR, exist_ok=True)
os.makedirs(settings.OUTPUTS_DIR, exist_ok=True)
