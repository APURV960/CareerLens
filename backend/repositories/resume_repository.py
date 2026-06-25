from backend.repositories.db_pool import get_db_connection
import json

def get_latest_active_resume(user_id: int):
    """Retrieves the active resume for a user."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, storage_key, resume_text, extracted_skills, version 
                FROM resumes 
                WHERE user_id = %s AND is_active = TRUE
                """,
                (user_id,)
            )
            row = cur.fetchone()
            if not row:
                return None
            return {
                "id": row[0],
                "storage_key": row[1],
                "resume_text": row[2],
                "extracted_skills": row[3],
                "version": row[4]
            }

def save_new_resume(user_id: int, storage_key: str, resume_text: str, skills: list) -> dict:
    """
    Saves a new resume version, archiving older versions.
    Includes concurrency locks to ensure serialization under concurrent threads.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Lock the user row to prevent race conditions during versioning checks
            cur.execute("SELECT 1 FROM users WHERE id = %s FOR UPDATE", (user_id,))
            
            # Get current maximum version number
            cur.execute("SELECT COALESCE(MAX(version), 0) FROM resumes WHERE user_id = %s", (user_id,))
            max_version = cur.fetchone()[0]
            new_version = max_version + 1

            # Deactivate previous active resumes for this user
            cur.execute("UPDATE resumes SET is_active = FALSE WHERE user_id = %s", (user_id,))

            # Insert the new active resume
            cur.execute(
                """
                INSERT INTO resumes (user_id, storage_key, resume_text, extracted_skills, version, is_active)
                VALUES (%s, %s, %s, %s, %s, TRUE)
                RETURNING id, version
                """,
                (user_id, storage_key, resume_text, json.dumps(skills), new_version)
            )
            row = cur.fetchone()
            return {"id": row[0], "version": row[1]}
