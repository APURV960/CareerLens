from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from backend.auth.dependencies import get_current_user
from backend.services.storage_service import LocalStorageProvider
from backend.repositories.resume_repository import save_new_resume
from resume_parser import parse_resume
from skill_extractor import extract_skills
import os
import tempfile
import time

router = APIRouter(prefix="/uploads", tags=["Uploads"])
storage = LocalStorageProvider()

@router.post("/resume")
async def upload_resume(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """
    Accepts PDF uploads, stores them securely under user-isolated storage keys,
    parses their skills, and saves versioned metadata in PostgreSQL.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF resumes are supported.")
    
    file_bytes = await file.read()
    
    # Sanitize and build user folder: user_<id>/resume.pdf
    user_dir = f"user_{current_user['id']}"
    storage_key = f"{user_dir}/resume.pdf"
    
    # 1. Save using Abstraction provider (will overwrite user's latest resume on disk)
    storage.save(file_bytes, storage_key)
    
    # 2. Parse text (using a temp file to pass bytes buffer to pdfplumber)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        resume_text = parse_resume(tmp_path)
        skills = extract_skills(resume_text)
    except Exception as parse_error:
        raise HTTPException(status_code=500, detail=f"Failed to parse resume: {str(parse_error)}")
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
    
    # 3. Store in Postgres as a new version history record
    meta = save_new_resume(
        user_id=current_user['id'], 
        storage_key=storage_key, 
        resume_text=resume_text, 
        skills=skills
    )
    
    return {
        "resume_id": meta["id"],
        "version": meta["version"],
        "skills": skills,
        "session_id": current_user.get("session_id")
    }
