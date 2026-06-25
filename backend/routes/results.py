from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from backend.auth.dependencies import get_current_user
from backend.repositories.results_repository import (
    get_user_history,
    verify_run_owner,
    get_run_jobs,
    get_run_skill_gaps,
    get_run_cover_letters,
    get_run_job_export_data,
    get_dashboard_stats,
    verify_job_owner,
    upsert_application_status,
    get_search_run_resume_id,
    get_resume_text_by_id,
    get_job_result_by_company,
    upsert_cover_letter
)
from uuid import UUID
from pydantic import BaseModel
import io
import json
import datetime
import pandas as pd

router = APIRouter(prefix="/results", tags=["Results"])

# Predefined database of common skills and their career guidance attributes
SKILLS_ENRICHMENT = {
    "python": {
        "importance": "Critical",
        "demand": "High",
        "difficulty": "Easy",
        "learning_time": "2-3 weeks",
        "resources": {
            "official_docs": "https://docs.python.org/3/",
            "free_course": "https://www.freecodecamp.org/news/learning-python-from-zero-to-hero-120c54f7d860/",
            "youtube": "https://www.youtube.com/watch?v=rfscVS0vtbw",
            "github_project": "https://github.com/vinta/awesome-python"
        }
    },
    "machine learning": {
        "importance": "High",
        "demand": "High",
        "difficulty": "Hard",
        "learning_time": "2-3 months",
        "resources": {
            "official_docs": "https://scikit-learn.org/stable/",
            "free_course": "https://www.coursera.org/learn/machine-learning",
            "youtube": "https://www.youtube.com/playlist?list=PLZHQObOWTQDNU6R1_67000Dx_ZCJB-3pi",
            "github_project": "https://github.com/josephmisiti/awesome-machine-learning"
        }
    },
    "deep learning": {
        "importance": "High",
        "demand": "Medium-High",
        "difficulty": "Very Hard",
        "learning_time": "3-4 months",
        "resources": {
            "official_docs": "https://pytorch.org/docs/stable/index.html",
            "free_course": "https://www.fast.ai/",
            "youtube": "https://www.youtube.com/playlist?list=PLtBw6njQRU-rWP5ae3CGeBCry1yRoUsJS",
            "github_project": "https://github.com/aymericdamien/TensorFlow-Examples"
        }
    },
    "aws": {
        "importance": "High",
        "demand": "High",
        "difficulty": "Medium",
        "learning_time": "3-4 weeks",
        "resources": {
            "official_docs": "https://aws.amazon.com/documentation/",
            "free_course": "https://www.freecodecamp.org/news/aws-certified-cloud-practitioner-study-course-pass-the-exam/",
            "youtube": "https://www.youtube.com/watch?v=3hLmDS179YE",
            "github_project": "https://github.com/donnemartin/system-design-primer"
        }
    },
    "docker": {
        "importance": "High",
        "demand": "High",
        "difficulty": "Medium",
        "learning_time": "1-2 weeks",
        "resources": {
            "official_docs": "https://docs.docker.com/",
            "free_course": "https://www.freecodecamp.org/news/docker-simplified/",
            "youtube": "https://www.youtube.com/watch?v=fqMOX6JJhGo",
            "github_project": "https://github.com/veggiemonk/awesome-docker"
        }
    },
    "kubernetes": {
        "importance": "High",
        "demand": "High",
        "difficulty": "Hard",
        "learning_time": "4-6 weeks",
        "resources": {
            "official_docs": "https://kubernetes.io/docs/home/",
            "free_course": "https://www.edx.org/course/introduction-to-kubernetes",
            "youtube": "https://www.youtube.com/watch?v=X48VuDVv0do",
            "github_project": "https://github.com/ramitsurana/awesome-kubernetes"
        }
    },
    "react": {
        "importance": "High",
        "demand": "High",
        "difficulty": "Medium",
        "learning_time": "3-4 weeks",
        "resources": {
            "official_docs": "https://react.dev/",
            "free_course": "https://react.dev/learn",
            "youtube": "https://www.youtube.com/watch?v=Ke90Tje7VS0",
            "github_project": "https://github.com/enaqx/awesome-react"
        }
    },
    "node": {
        "importance": "High",
        "demand": "High",
        "difficulty": "Medium",
        "learning_time": "2-3 weeks",
        "resources": {
            "official_docs": "https://nodejs.org/en/docs/",
            "free_course": "https://www.freecodecamp.org/news/free-node-js-course/",
            "youtube": "https://www.youtube.com/watch?v=TbQWn6f1t4s",
            "github_project": "https://github.com/sindresorhus/awesome-nodejs"
        }
    },
    "sql": {
        "importance": "Critical",
        "demand": "High",
        "difficulty": "Easy",
        "learning_time": "1-2 weeks",
        "resources": {
            "official_docs": "https://www.postgresql.org/docs/",
            "free_course": "https://www.khanacademy.org/computing/computer-programming/sql",
            "youtube": "https://www.youtube.com/watch?v=HXV3zeQKqGY",
            "github_project": "https://github.com/twostraws/sql-cheat-sheet"
        }
    },
    "data science": {
        "importance": "High",
        "demand": "High",
        "difficulty": "Medium-Hard",
        "learning_time": "2-3 months",
        "resources": {
            "official_docs": "https://pandas.pydata.org/docs/",
            "free_course": "https://www.freecodecamp.org/news/learn-data-science-complete-course-for-beginners/",
            "youtube": "https://www.youtube.com/watch?v=ua-CiDNNj30",
            "github_project": "https://github.com/academic/awesome-datascience"
        }
    }
}

def get_enriched_skill_data(skill_name):
    name_clean = skill_name.lower().strip()
    if name_clean in SKILLS_ENRICHMENT:
        return SKILLS_ENRICHMENT[name_clean]
    
    import urllib.parse
    query_encoded = urllib.parse.quote(skill_name)
    return {
        "importance": "High",
        "demand": "Medium",
        "difficulty": "Medium",
        "learning_time": "2-3 weeks",
        "resources": {
            "official_docs": f"https://www.google.com/search?q={query_encoded}+official+documentation",
            "free_course": f"https://www.google.com/search?q=free+{query_encoded}+course",
            "youtube": f"https://www.youtube.com/results?search_query={query_encoded}+tutorial",
            "github_project": f"https://github.com/search?q={query_encoded}"
        }
    }


class ApplicationStatusRequest(BaseModel):
    job_result_id: int
    status: str  # Generated, Applied, Interview, Rejected, Offer


class CoverLetterRegenerateRequest(BaseModel):
    run_id: str
    company: str
    role: str


@router.get("/history")
def get_user_history_route(current_user: dict = Depends(get_current_user)):
    """Retrieves all past search runs executed by the user."""
    return get_user_history(current_user["id"])


@router.get("/run/{run_id}")
def get_run_details(run_id: str, current_user: dict = Depends(get_current_user)):
    """Retrieves jobs, skill gaps, and cover letters for a specific historical run."""
    try:
        run_uuid = UUID(run_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format for run_id.")
        
    # Verify owner using repository
    if not verify_run_owner(str(run_uuid), current_user["id"]):
        raise HTTPException(status_code=404, detail="Run not found or unauthorized.")
    
    # Fetch jobs using repository
    jobs = get_run_jobs(str(run_uuid), current_user["id"])

    # Fetch skill gaps using repository
    gap_row = get_run_skill_gaps(str(run_uuid))
    if gap_row:
        missing = gap_row["missing_skills"]
        market = gap_row["market_demand"]
        enriched_missing = []
        for s in missing:
            enriched_missing.append({
                "name": s,
                **get_enriched_skill_data(s)
            })
        gap = {"missing_skills": enriched_missing, "market_demand": market}
    else:
        gap = None

    # Fetch letters using repository
    letters = get_run_cover_letters(str(run_uuid))

    return {
        "run_id": run_id,
        "jobs": jobs,
        "skill_gap": gap,
        "cover_letters": letters
    }


@router.get("/run/{run_id}/export")
def export_run_results(run_id: str, current_user: dict = Depends(get_current_user)):
    """Generates an Excel spreadsheet of job results dynamically from Postgres and streams it."""
    try:
        run_uuid = UUID(run_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format for run_id.")
    
    # Verify ownership using repository
    if not verify_run_owner(str(run_uuid), current_user["id"]):
        raise HTTPException(status_code=404, detail="Run not found or unauthorized.")
    
    # Query job result fields using repository
    rows = get_run_job_export_data(str(run_uuid))
            
    if not rows:
        raise HTTPException(status_code=400, detail="No job results available for export.")

    df = pd.DataFrame(
        rows, 
        columns=["Company", "Title", "Location", "Match Score", "Salary", "Type", "Source", "URL", "Experience Level", "Work Setting", "Posted At"]
    )
    
    # Convert Match Score float to percentage format
    df["Match Score"] = df["Match Score"].apply(lambda x: f"{int(x * 100)}%")
    
    # Save dataframe into an in-memory BytesIO buffer
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Job Matches")
    output.seek(0)

    headers = {
        'Content-Disposition': f'attachment; filename="job_matches_run_{run_id}.xlsx"'
    }
    return StreamingResponse(
        output, 
        headers=headers, 
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@router.get("/dashboard-stats")
def get_dashboard_statistics(current_user: dict = Depends(get_current_user)):
    """Computes total aggregated metrics, run logs, and application status breakdown for dashboard widgets."""
    stats = get_dashboard_stats(current_user["id"])
    if not stats:
        return {
            "has_resume": False,
            "resume_score": 0,
            "jobs_found": 0,
            "highest_match": 0,
            "applications_sent": 0,
            "missing_skills_count": 0,
            "search_runs_count": 0,
            "recent_activity": []
        }
    
    return {
        "has_resume": True,
        **stats
    }


@router.post("/applications/status")
def update_application_status(req: ApplicationStatusRequest, current_user: dict = Depends(get_current_user)):
    """Logs or updates an application status for a job result match."""
    # Verify job belongs to user
    if not verify_job_owner(req.job_result_id, current_user["id"]):
        raise HTTPException(status_code=404, detail="Job result not found or unauthorized.")
    
    # Insert or update application status
    upsert_application_status(current_user["id"], req.job_result_id, req.status)
    return {"status": "success", "message": f"Application status updated to {req.status}"}


@router.post("/cover-letter/regenerate")
def regenerate_cover_letter_route(req: CoverLetterRegenerateRequest, current_user: dict = Depends(get_current_user)):
    """Triggers an individual LLM regeneration for a specific company cover letter."""
    try:
        run_uuid = UUID(req.run_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format for run_id.")

    # Verify owner of search run and get resume ID using repository
    resume_id = get_search_run_resume_id(str(run_uuid), current_user["id"])
    if not resume_id:
        raise HTTPException(status_code=404, detail="Run not found or unauthorized.")

    # Get resume text using repository
    resume_text = get_resume_text_by_id(resume_id)
    if not resume_text:
        raise HTTPException(status_code=404, detail="Resume text not found.")

    # Find the job details using repository
    job_details = get_job_result_by_company(str(run_uuid), req.company)
    if not job_details:
        raise HTTPException(status_code=404, detail="Job result not found for this company.")
    
    job = {
        "title": job_details["title"],
        "company": job_details["company"],
        "description": job_details["description"]
    }

    # Generate new cover letter using Gemini
    from src.application_agent import generate_cover_letter
    try:
        new_content = generate_cover_letter(resume_text, job)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate cover letter: {str(e)}")

    # Save/Update in cover_letters database table using repository
    upsert_cover_letter(current_user["id"], str(run_uuid), req.company, req.role, new_content)

    return {
        "status": "success",
        "company": req.company,
        "role": req.role,
        "content": new_content
    }

