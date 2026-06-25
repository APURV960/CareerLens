import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    # DB_PASSWORD = os.getenv("DB_PASSWORD")
    JWT_SECRET = os.getenv("JWT_SECRET", "supersecretkey")
    ALGORITHM = "HS256"
    STORAGE_PROVIDER = os.getenv("STORAGE_PROVIDER", "local")  # local, s3
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "career-lens-resumes")

settings = Settings()
