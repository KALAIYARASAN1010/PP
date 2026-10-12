import os

class Settings:
    PROJECT_NAME: str = "IPMPRS - Police Proposal Management & Precedent Retrieval"
    SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "super-secret-police-ipmprs-key-2026-secure")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./ipmprs.db")
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads")
    SIMILARITY_THRESHOLD: float = 0.35  # Threshold below which "no strong precedent" is flagged

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
