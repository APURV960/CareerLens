import datetime
import uuid
from backend.repositories.db_pool import get_db_connection
from backend.repositories.results_repository import (
    create_search_run,
    update_search_run_status,
    save_job_results,
    save_skill_gap,
    save_cover_letters
)
from tools.job_search_tool import find_jobs
from tools.ranking_tool import rank_job_results
from tools.skill_gap_tool import analyze_skill_gap
from tools.cover_letter_tool import create_cover_letters

def run_agent_background_task(job_id: str, user_id: int, resume_id: int):
    """
    Background worker that runs the full AI career agent pipeline.
    It reads resume details from Postgres, runs search/rank/gap/letters,
    writes all results to Postgres search_runs, and updates the agent_jobs state.
    """
    # 1. Update job to 'running'
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE agent_jobs SET status = 'running' WHERE id = %s",
                (job_id,)
            )

    # 2. Create the search run log root
    run_id = create_search_run(user_id, resume_id, job_id)
    
    try:
        # 3. Retrieve resume text and extracted skills from PostgreSQL
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT resume_text, extracted_skills FROM resumes WHERE id = %s",
                    (resume_id,)
                )
                row = cur.fetchone()
                if not row:
                    raise ValueError(f"Resume ID {resume_id} not found in database.")
                resume_text, skills_json = row[0], row[1]
                
                # If skills_json is stored as string or JSONB
                if isinstance(skills_json, str):
                    import json
                    skills = json.loads(skills_json)
                else:
                    skills = skills_json

        # 4. Search Jobs (Adzuna API)
        from query_generator import generate_queries
        queries = generate_queries(resume_text)
        print(f"[{job_id}] Searching jobs for queries: {queries}")
        jobs = find_jobs(queries)

        # 5. Semantic Job Ranking (SentenceTransformer Singleton)
        print(f"[{job_id}] Ranking {len(jobs)} jobs...")
        ranked_jobs = rank_job_results(resume_text, jobs)
        save_job_results(user_id, run_id, ranked_jobs)

        # 6. Skill Gap Analysis
        print(f"[{job_id}] Analysing skill gaps...")
        gap = analyze_skill_gap(skills, ranked_jobs)
        save_skill_gap(user_id, run_id, gap)

        # 7. Cover Letter Generation
        print(f"[{job_id}] Generating cover letters (limit 1)...")
        letters = create_cover_letters(resume_text, ranked_jobs, limit=1)
        
        # Parse letter contents from text file outputs to save to Postgres
        db_letters = []
        for l in letters:
            try:
                with open(l["file"], "r", encoding="utf-8") as f:
                    content = f.read()
                db_letters.append({
                    "company": l["company"],
                    "role": "Software Engineer",
                    "content": content
                })
            except Exception as file_err:
                print(f"[{job_id}] Failed to read letter output file {l['file']}: {file_err}")
                
        save_cover_letters(user_id, run_id, db_letters)

        # 8. Update Job & Search Run state to completed successfully
        completed_at = datetime.datetime.now(datetime.timezone.utc)
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE agent_jobs SET status = 'completed', completed_at = %s WHERE id = %s",
                    (completed_at, job_id)
                )
        update_search_run_status(run_id, 'success', completed_at)
        print(f"[{job_id}] Agent task completed successfully.")

    except Exception as e:
        completed_at = datetime.datetime.now(datetime.timezone.utc)
        print(f"[{job_id}] Agent task failed with error: {e}")
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE agent_jobs SET status = 'failed', completed_at = %s, error_message = %s WHERE id = %s",
                    (completed_at, str(e), job_id)
                )
        update_search_run_status(run_id, 'failed', completed_at)
