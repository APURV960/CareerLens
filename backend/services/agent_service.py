import datetime
import traceback
import json
from backend.repositories.agent_repository import update_agent_job_status
from backend.repositories.resume_repository import get_resume_by_id
from backend.repositories.results_repository import (
    create_search_run,
    update_search_run_status,
    save_job_results,
    save_skill_gap,
    save_cover_letters
)
from src.tools.job_search_tool import find_jobs
from src.tools.ranking_tool import rank_job_results
from src.tools.skill_gap_tool import analyze_skill_gap
from src.tools.cover_letter_tool import create_cover_letters
from src.query_generator import generate_queries

def format_stage_error(stage_name: str, exc: Exception) -> str:
    """
    Formats exception tracebacks into structured failure details.
    """
    tb = exc.__traceback__
    summary = traceback.extract_tb(tb)
    if summary:
        last_frame = summary[-1]
        file_name = last_frame.filename
        func_name = last_frame.name
        line_no = last_frame.lineno
    else:
        file_name = "Unknown"
        func_name = "Unknown"
        line_no = "Unknown"
        
    exc_type = type(exc).__name__
    exc_msg = str(exc)
    
    formatted = (
        f"[{stage_name.upper()}]\n\n"
        f"FAILED\n\n"
        f"File: {file_name}\n"
        f"Function: {func_name}\n"
        f"Line: {line_no}\n"
        f"Reason:\n\n"
        f"{exc_type}: {exc_msg}"
    )
    return formatted


def run_agent_background_task(job_id: str, user_id: int, resume_id: int):
    """
    Background worker that runs the full AI career agent pipeline.
    It reads resume details from Postgres, runs search/rank/gap/letters,
    writes all results to Postgres search_runs, and updates the agent_jobs state.
    
    Guarantees exception safety so that jobs are never left stuck in 'running' status.
    """
    run_id = None
    try:
        # 1. Update job to 'running'
        print(f"[{job_id}] Starting agent background task...")
        update_agent_job_status(job_id, 'running')

        # 2. Create the search run log root
        try:
            run_id = create_search_run(user_id, resume_id, job_id)
            print(f"[{job_id}] Created search run ID: {run_id}")
        except Exception as e:
            raise RuntimeError(format_stage_error("Database persistence", e)) from e
        
        # 3. Retrieve resume text and extracted skills from PostgreSQL using repository
        try:
            resume = get_resume_by_id(resume_id)
            if not resume:
                raise ValueError(f"Resume ID {resume_id} not found in database.")
            
            resume_text = resume["resume_text"]
            skills_json = resume["extracted_skills"]
            
            # Parse skills_json if it is stored as string
            if isinstance(skills_json, str):
                skills = json.loads(skills_json)
            else:
                skills = skills_json
        except Exception as e:
            raise RuntimeError(format_stage_error("Resume analysis", e)) from e

        # 4. Search Jobs (Adzuna API)
        try:
            queries = generate_queries(resume_text)
            print(f"[{job_id}] Searching jobs for queries: {queries}")
        except Exception as e:
            raise RuntimeError(format_stage_error("Query generation", e)) from e

        try:
            jobs = find_jobs(queries)
        except Exception as e:
            raise RuntimeError(format_stage_error("Job search", e)) from e

        # 5. Semantic Job Ranking (SentenceTransformer Singleton)
        try:
            print(f"[{job_id}] Ranking {len(jobs)} jobs...")
            ranked_jobs = rank_job_results(resume_text, jobs)
        except Exception as e:
            raise RuntimeError(format_stage_error("Job ranking", e)) from e

        try:
            save_job_results(user_id, run_id, ranked_jobs)
        except Exception as e:
            raise RuntimeError(format_stage_error("Database persistence", e)) from e

        # 6. Skill Gap Analysis
        try:
            print(f"[{job_id}] Analysing skill gaps...")
            gap = analyze_skill_gap(skills, ranked_jobs)
        except Exception as e:
            raise RuntimeError(format_stage_error("Skill-gap analysis", e)) from e

        try:
            save_skill_gap(user_id, run_id, gap)
        except Exception as e:
            raise RuntimeError(format_stage_error("Database persistence", e)) from e

        # 7. Cover Letter Generation
        try:
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
        except Exception as e:
            raise RuntimeError(format_stage_error("Cover-letter generation", e)) from e
                
        try:
            save_cover_letters(user_id, run_id, db_letters)
        except Exception as e:
            raise RuntimeError(format_stage_error("Database persistence", e)) from e

        # 8. Update Job & Search Run state to completed successfully
        try:
            completed_at = datetime.datetime.now(datetime.timezone.utc)
            update_agent_job_status(job_id, 'completed', completed_at=completed_at)
            update_search_run_status(run_id, 'success', completed_at)
            print(f"[{job_id}] Agent task completed successfully.")
        except Exception as e:
            raise RuntimeError(format_stage_error("Database persistence", e)) from e

    except Exception as e:
        completed_at = datetime.datetime.now(datetime.timezone.utc)
        error_msg = str(e)
        tb_str = traceback.format_exc()
        print(f"[{job_id}] Agent task failed with error: {error_msg}\n{tb_str}")
        
        # Ensure job is marked as failed in agent_jobs
        try:
            update_agent_job_status(job_id, 'failed', completed_at=completed_at, error_message=error_msg)
        except Exception as update_err:
            print(f"[{job_id}] Critical: Failed to update agent job status to failed: {update_err}")
            
        # Ensure search run is marked as failed if it was created
        if run_id:
            try:
                update_search_run_status(run_id, 'failed', completed_at)
            except Exception as run_update_err:
                print(f"[{job_id}] Critical: Failed to update search run status to failed: {run_update_err}")

