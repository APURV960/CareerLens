import json
import datetime
from memory.database import get_connection


def save_resume(user_id, resume_text, skills=None):
    if skills is None:
        skills = []

    conn = get_connection()
    cur = conn.cursor()
    try:
        # 1. Ensure user exists
        cur.execute(
            "INSERT INTO users (id, is_anonymous) VALUES (%s, TRUE) ON CONFLICT (id) DO NOTHING",
            (user_id,)
        )

        # 2. Get current maximum version number
        cur.execute("SELECT COALESCE(MAX(version), 0) FROM resumes WHERE user_id = %s", (user_id,))
        max_version = cur.fetchone()[0]
        new_version = max_version + 1

        # 3. Deactivate previous active resumes for this user
        cur.execute("UPDATE resumes SET is_active = FALSE WHERE user_id = %s", (user_id,))

        # 4. Insert the new active resume
        cur.execute(
            """
            INSERT INTO resumes (user_id, storage_key, resume_text, extracted_skills, version, is_active)
            VALUES (%s, %s, %s, %s, %s, TRUE)
            RETURNING id
            """,
            (user_id, f"local_user_{user_id}/resume.pdf", resume_text, json.dumps(skills), new_version)
        )
        resume_id = cur.fetchone()[0]

        # 5. Create a search run record
        cur.execute(
            """
            INSERT INTO search_runs (user_id, resume_id, status)
            VALUES (%s, %s, 'running')
            """,
            (user_id, resume_id)
        )

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()


def save_jobs(user_id, jobs):
    conn = get_connection()
    cur = conn.cursor()
    try:
        # 1. Find the active resume for this user
        cur.execute("SELECT id FROM resumes WHERE user_id = %s AND is_active = TRUE ORDER BY id DESC LIMIT 1", (user_id,))
        row = cur.fetchone()
        if not row:
            save_resume(user_id, "Dummy resume text")
            cur.execute("SELECT id FROM resumes WHERE user_id = %s AND is_active = TRUE ORDER BY id DESC LIMIT 1", (user_id,))
            row = cur.fetchone()
        resume_id = row[0]

        # 2. Find the latest active search run for this user
        cur.execute("SELECT id FROM search_runs WHERE user_id = %s AND status = 'running' ORDER BY started_at DESC LIMIT 1", (user_id,))
        run_row = cur.fetchone()
        if run_row:
            run_id = run_row[0]
        else:
            cur.execute(
                """
                INSERT INTO search_runs (user_id, resume_id, status)
                VALUES (%s, %s, 'running')
                RETURNING id
                """,
                (user_id, resume_id)
            )
            run_id = cur.fetchone()[0]

        # 3. Save the job results
        for job in jobs:
            salary = job.get("salary", "N/A")
            employment_type = job.get("employment_type", "N/A")
            source = job.get("source", "Adzuna")
            cur.execute(
                """
                INSERT INTO job_results 
                (user_id, search_run_id, title, company, location, description, url, match_score, salary, employment_type, source)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    user_id,
                    run_id,
                    job["title"],
                    job["company"],
                    job.get("location", "N/A"),
                    job.get("description", ""),
                    job.get("url", ""),
                    job["match_score"],
                    salary,
                    employment_type,
                    source
                )
            )

        # Update the search run status to success
        cur.execute(
            "UPDATE search_runs SET status = 'success', completed_at = %s WHERE id = %s",
            (datetime.datetime.now(datetime.timezone.utc), run_id)
        )

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cur.close()
        conn.close()