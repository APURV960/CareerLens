from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from backend.auth.dependencies import get_current_user
from backend.repositories.db_pool import get_db_connection
from backend.repositories.resume_repository import get_latest_active_resume
from backend.services.agent_service import run_agent_background_task
import uuid

router = APIRouter(prefix="/agent", tags=["Agent"])

@router.post("/run")
def trigger_agent_run(background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    """
    Triggers an asynchronous job run for the user's active resume.
    Returns a unique job ID immediately.
    """
    # 1. Verify user has uploaded a resume
    resume = get_latest_active_resume(current_user["id"])
    if not resume:
        raise HTTPException(status_code=400, detail="Please upload a resume before running the agent.")

    job_id = str(uuid.uuid4())
    
    # 2. Insert queued job status record
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO agent_jobs (id, user_id, status) VALUES (%s, %s, 'queued')",
                (job_id, current_user["id"])
            )
            
    # 3. Add to FastAPI BackgroundTasks (easily swappable to Celery workers later)
    background_tasks.add_task(
        run_agent_background_task, 
        job_id, 
        current_user["id"], 
        resume["id"]
    )
    
    return {
        "job_id": job_id, 
        "status": "queued"
    }

@router.get("/status/{job_id}")
def get_job_status(job_id: str, current_user: dict = Depends(get_current_user)):
    """
    Returns the execution state (queued, running, completed, failed) of a background job.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT status, error_message FROM agent_jobs WHERE id = %s AND user_id = %s",
                (job_id, current_user["id"])
            )
            row = cur.fetchone()
            if not row:
                raise HTTPException(status_code=404, detail="Job not found.")
            
            # Fetch corresponding search_run_id if it exists
            cur.execute(
                "SELECT id FROM search_runs WHERE job_id = %s AND user_id = %s",
                (job_id, current_user["id"])
            )
            run_row = cur.fetchone()
            run_id = str(run_row[0]) if run_row else None
            
            return {
                "job_id": job_id, 
                "status": row[0], 
                "error_message": row[1],
                "run_id": run_id
            }
