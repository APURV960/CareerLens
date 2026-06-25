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

def get_user_history(user_id: int) -> list:
    """Retrieves all past search runs executed by the user."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, resume_id, started_at, completed_at, status 
                FROM search_runs 
                WHERE user_id = %s 
                ORDER BY started_at DESC
                """,
                (user_id,)
            )
            rows = cur.fetchall()
            return [
                {
                    "run_id": str(r[0]),
                    "resume_id": r[1],
                    "started_at": r[2],
                    "completed_at": r[3],
                    "status": r[4]
                }
                for r in rows
            ]

def verify_run_owner(run_id: str, user_id: int) -> bool:
    """Verifies that a search run belongs to the specified user."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM search_runs WHERE id = %s AND user_id = %s", 
                (run_id, user_id)
            )
            return cur.fetchone() is not None

def get_run_jobs(run_id: str, user_id: int) -> list:
    """Retrieves jobs with left join on applications to get track status."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT jr.id, jr.title, jr.company, jr.location, jr.match_score, jr.salary, jr.employment_type, jr.source, jr.url, jr.experience_level, jr.work_setting, jr.posted_at, ap.status 
                FROM job_results jr
                LEFT JOIN applications ap ON jr.id = ap.job_result_id AND ap.user_id = %s
                WHERE jr.search_run_id = %s
                ORDER BY jr.match_score DESC
                """,
                (user_id, run_id)
            )
            return [
                {
                    "id": r[0],
                    "title": r[1], 
                    "company": r[2], 
                    "location": r[3], 
                    "match_score": r[4], 
                    "salary": r[5] or "N/A", 
                    "employment_type": r[6] or "N/A", 
                    "source": r[7] or "Adzuna", 
                    "url": r[8],
                    "experience_level": r[9] or "Mid-Level",
                    "work_setting": r[10] or "Hybrid",
                    "posted_at": r[11] or "Just now",
                    "application_status": r[12] or "Generated"
                }
                for r in cur.fetchall()
            ]

def get_run_skill_gaps(run_id: str) -> dict:
    """Retrieves missing skills and market demand for a search run."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT missing_skills, market_demand FROM skill_gaps WHERE search_run_id = %s", 
                (run_id,)
            )
            row = cur.fetchone()
            if not row:
                return None
            return {
                "missing_skills": row[0],
                "market_demand": row[1]
            }

def get_run_cover_letters(run_id: str) -> list:
    """Retrieves cover letters generated for a search run."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT company, role, content FROM cover_letters WHERE search_run_id = %s", 
                (run_id,)
            )
            return [
                {
                    "company": r[0], 
                    "role": r[1], 
                    "content": r[2]
                } 
                for r in cur.fetchall()
            ]

def get_run_job_export_data(run_id: str) -> list:
    """Retrieves raw job result rows for dynamc spreadsheet generation."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT company, title, location, match_score, salary, employment_type, source, url, experience_level, work_setting, posted_at 
                FROM job_results 
                WHERE search_run_id = %s 
                ORDER BY match_score DESC
                """,
                (run_id,)
            )
            return cur.fetchall()

def get_dashboard_stats(user_id: int) -> dict:
    """Computes total aggregated metrics, run logs, and application status breakdown for dashboard widgets."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # 1. Fetch latest active resume details
            cur.execute(
                "SELECT id, extracted_skills, version FROM resumes WHERE user_id = %s AND is_active = TRUE",
                (user_id,)
            )
            resume_row = cur.fetchone()
            if not resume_row:
                return None
            
            resume_id = resume_row[0]
            skills = resume_row[1]
            if isinstance(skills, str):
                skills = json.loads(skills)
            version = resume_row[2]
            
            # Calculate a resume score out of 100 based on extracted skills
            resume_score = min(98, 60 + 5 * len(skills))
            
            # 2. Count search runs
            cur.execute("SELECT COUNT(*) FROM search_runs WHERE user_id = %s", (user_id,))
            search_runs_count = cur.fetchone()[0]
            
            # 3. Fetch latest run
            cur.execute(
                "SELECT id FROM search_runs WHERE user_id = %s ORDER BY started_at DESC LIMIT 1",
                (user_id,)
            )
            run_row = cur.fetchone()
            latest_run_id = str(run_row[0]) if run_row else None
            
            jobs_found = 0
            highest_match = 0
            missing_skills_count = 0
            
            if latest_run_id:
                # 4. Count jobs and find max match in latest run
                cur.execute(
                    "SELECT COUNT(*), COALESCE(MAX(match_score), 0) FROM job_results WHERE search_run_id = %s",
                    (latest_run_id,)
                )
                jobs_row = cur.fetchone()
                jobs_found = jobs_row[0]
                highest_match = int(jobs_row[1] * 100)
                
                # 5. Count missing skills
                cur.execute(
                    "SELECT missing_skills FROM skill_gaps WHERE search_run_id = %s",
                    (latest_run_id,)
                )
                gap_row = cur.fetchone()
                if gap_row:
                    gap_list = gap_row[0]
                    if isinstance(gap_list, str):
                        gap_list = json.loads(gap_list)
                    missing_skills_count = len(gap_list)
            
            # 6. Count applications sent
            cur.execute(
                "SELECT COUNT(*) FROM applications WHERE user_id = %s AND status IN ('Applied', 'Interview', 'Offer')",
                (user_id,)
            )
            applications_sent = cur.fetchone()[0]
            
            # Get application statuses breakdown
            cur.execute(
                "SELECT status, COUNT(*) FROM applications WHERE user_id = %s GROUP BY status",
                (user_id,)
            )
            app_breakdown = {r[0]: r[1] for r in cur.fetchall()}
            
            for s in ["Generated", "Applied", "Interview", "Rejected", "Offer"]:
                if s not in app_breakdown:
                    app_breakdown[s] = 0
            
            # 7. Collect recent activities
            activities = []
            
            # Resume uploads
            cur.execute("SELECT version, created_at FROM resumes WHERE user_id = %s ORDER BY created_at DESC LIMIT 3", (user_id,))
            for r in cur.fetchall():
                activities.append({
                    "type": "upload",
                    "message": f"Uploaded resume version {r[0]}",
                    "timestamp": r[1].isoformat() if r[1] else None
                })
                
            # Search runs
            cur.execute("SELECT started_at, status FROM search_runs WHERE user_id = %s ORDER BY started_at DESC LIMIT 3", (user_id,))
            for r in cur.fetchall():
                activities.append({
                    "type": "run",
                    "message": f"Ran AI job discovery ({r[1]})",
                    "timestamp": r[0].isoformat() if r[0] else None
                })
                
            # Applications
            cur.execute(
                """
                SELECT ap.status, jr.title, jr.company, ap.updated_at 
                FROM applications ap 
                JOIN job_results jr ON ap.job_result_id = jr.id 
                WHERE ap.user_id = %s 
                ORDER BY ap.updated_at DESC LIMIT 3
                """,
                (user_id,)
            )
            for r in cur.fetchall():
                activities.append({
                    "type": "application",
                    "message": f"Status updated to '{r[0]}' for {r[1]} at {r[2]}",
                    "timestamp": r[3].isoformat() if r[3] else None
                })
            
            activities = [act for act in activities if act["timestamp"] is not None]
            activities.sort(key=lambda x: x["timestamp"], reverse=True)
            activities = activities[:5]
            
            return {
                "resume_score": resume_score,
                "jobs_found": jobs_found,
                "highest_match": highest_match,
                "applications_sent": applications_sent,
                "missing_skills_count": missing_skills_count,
                "search_runs_count": search_runs_count,
                "recent_activity": activities,
                "app_breakdown": app_breakdown
            }

def verify_job_owner(job_result_id: int, user_id: int) -> bool:
    """Verifies that a job result record belongs to the specified user."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM job_results WHERE id = %s AND user_id = %s",
                (job_result_id, user_id)
            )
            return cur.fetchone() is not None

def upsert_application_status(user_id: int, job_result_id: int, status: str) -> None:
    """Creates or updates an application status log for a job match."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM applications WHERE job_result_id = %s AND user_id = %s",
                (job_result_id, user_id)
            )
            row = cur.fetchone()
            import datetime
            now = datetime.datetime.now(datetime.timezone.utc)
            if row:
                cur.execute(
                    "UPDATE applications SET status = %s, updated_at = %s WHERE id = %s",
                    (status, now, row[0])
                )
            else:
                cur.execute(
                    "INSERT INTO applications (user_id, job_result_id, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)",
                    (user_id, job_result_id, status, now, now)
                )

def get_search_run_resume_id(run_id: str, user_id: int) -> int:
    """Retrieves the resume ID associated with a search run."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT resume_id FROM search_runs WHERE id = %s AND user_id = %s",
                (run_id, user_id)
            )
            row = cur.fetchone()
            return row[0] if row else None

def get_resume_text_by_id(resume_id: int) -> str:
    """Retrieves raw resume text corresponding to the resume ID."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT resume_text FROM resumes WHERE id = %s",
                (resume_id,)
            )
            row = cur.fetchone()
            return row[0] if row else None

def get_job_result_by_company(run_id: str, company: str) -> dict:
    """Retrieves job details (title, company, description) for letter generation."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT title, company, description FROM job_results WHERE search_run_id = %s AND company = %s",
                (run_id, company)
            )
            row = cur.fetchone()
            if not row:
                return None
            return {
                "title": row[0],
                "company": row[1],
                "description": row[2]
            }

def upsert_cover_letter(user_id: int, run_id: str, company: str, role: str, content: str) -> None:
    """Creates or updates a cover letter record."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM cover_letters WHERE search_run_id = %s AND company = %s",
                (run_id, company)
            )
            row = cur.fetchone()
            if row:
                cur.execute(
                    "UPDATE cover_letters SET content = %s, role = %s WHERE id = %s",
                    (content, role, row[0])
                )
            else:
                cur.execute(
                    "INSERT INTO cover_letters (user_id, search_run_id, company, role, content) VALUES (%s, %s, %s, %s, %s)",
                    (user_id, run_id, company, role, content)
                )

def get_search_run_id_by_job_id(job_id: str, user_id: int) -> str:
    """Retrieves the search run UUID associated with a background job ID."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM search_runs WHERE job_id = %s AND user_id = %s",
                (job_id, user_id)
            )
            row = cur.fetchone()
            return str(row[0]) if row else None

