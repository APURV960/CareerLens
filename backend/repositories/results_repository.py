import json
from backend.repositories.db_pool import get_db_connection

def create_search_run(user_id: int, resume_id: int, job_id: str = None) -> str:
    """
    Creates a new search run history root record and returns its UUID.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO search_runs (user_id, resume_id, job_id, status)
                VALUES (%s, %s, %s, 'running')
                RETURNING id
                """,
                (user_id, resume_id, job_id)
            )
            return str(cur.fetchone()[0])

def update_search_run_status(run_id: str, status: str, completed_at=None):
    """
    Updates the status of a search run (e.g. success, failed).
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            if completed_at:
                cur.execute(
                    "UPDATE search_runs SET status = %s, completed_at = %s WHERE id = %s",
                    (status, completed_at, run_id)
                )
            else:
                cur.execute(
                    "UPDATE search_runs SET status = %s WHERE id = %s",
                    (status, run_id)
                )

def save_job_results(user_id: int, search_run_id: str, jobs: list):
    """
    Saves ranked job postings for a specific search run.
    Extracts analytics data: salary, employment_type, source.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            for job in jobs:
                # Handle default analytics keys safely
                salary = job.get("salary", "N/A")
                employment_type = job.get("employment_type", "N/A")
                source = job.get("source", "Adzuna")
                experience_level = job.get("experience_level", "Mid-Level")
                work_setting = job.get("work_setting", "Hybrid")
                posted_at = job.get("posted_at", "Recently")
                
                cur.execute(
                    """
                    INSERT INTO job_results 
                    (user_id, search_run_id, title, company, location, description, url, match_score, salary, employment_type, source, experience_level, work_setting, posted_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        user_id,
                        search_run_id,
                        job["title"],
                        job["company"],
                        job["location"],
                        job["description"],
                        job["url"],
                        job["match_score"],
                        salary,
                        employment_type,
                        source,
                        experience_level,
                        work_setting,
                        posted_at
                    )
                )

def save_skill_gap(user_id: int, search_run_id: str, gap: dict):
    """
    Saves skill gap outputs and market demand metrics for a specific search run.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO skill_gaps (user_id, search_run_id, missing_skills, market_demand)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    user_id,
                    search_run_id,
                    json.dumps(gap["missing_skills"]),
                    json.dumps(gap["market_demand"])
                )
            )

def save_cover_letters(user_id: int, search_run_id: str, letters: list):
    """
    Saves generated cover letters directly into the database.
    Content field is the source of truth; no file systems mapping stored.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            for letter in letters:
                cur.execute(
                    """
                    INSERT INTO cover_letters (user_id, search_run_id, company, role, content)
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        user_id,
                        search_run_id,
                        letter["company"],
                        letter.get("role", "Software Engineer"),
                        letter["content"]
                    )
                )
