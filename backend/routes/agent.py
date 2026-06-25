from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from backend.auth.dependencies import get_current_user
from backend.repositories.resume_repository import get_latest_active_resume
from backend.repositories.agent_repository import create_agent_job, get_agent_job
from backend.repositories.results_repository import get_search_run_id_by_job_id
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
    
    # 2. Insert queued job status record using repository
    create_agent_job(job_id, current_user["id"], "queued")
            
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
    # Use repository to fetch job details
    job = get_agent_job(job_id, current_user["id"])
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    
    # Fetch corresponding search_run_id using repository
    run_id = get_search_run_id_by_job_id(job_id, current_user["id"])
    
    return {
        "job_id": job_id, 
        "status": job["status"], 
        "error_message": job["error_message"],
        "run_id": run_id
    }

