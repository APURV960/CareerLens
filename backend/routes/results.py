from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from backend.auth.dependencies import get_current_user
from backend.repositories.db_pool import get_db_connection
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
def get_user_history(current_user: dict = Depends(get_current_user)):
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
                (current_user["id"],)
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


@router.get("/run/{run_id}")
def get_run_details(run_id: str, current_user: dict = Depends(get_current_user)):
    """Retrieves jobs, skill gaps, and cover letters for a specific historical run."""
    try:
        run_uuid = UUID(run_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format for run_id.")
        
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Verify owner
            cur.execute(
                "SELECT id FROM search_runs WHERE id = %s AND user_id = %s", 
                (str(run_uuid), current_user["id"])
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Run not found or unauthorized.")
            
            # Fetch jobs with left join on applications to get track status
            cur.execute(
                """
                SELECT jr.id, jr.title, jr.company, jr.location, jr.match_score, jr.salary, jr.employment_type, jr.source, jr.url, jr.experience_level, jr.work_setting, jr.posted_at, ap.status 
                FROM job_results jr
                LEFT JOIN applications ap ON jr.id = ap.job_result_id AND ap.user_id = %s
                WHERE jr.search_run_id = %s
                ORDER BY jr.match_score DESC
                """,
                (current_user["id"], str(run_uuid))
            )
            jobs = [
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

            # Fetch skill gaps
            cur.execute(
                "SELECT missing_skills, market_demand FROM skill_gaps WHERE search_run_id = %s", 
                (str(run_uuid),)
            )
            gap_row = cur.fetchone()
            if gap_row:
                missing = gap_row[0]
                market = gap_row[1]
                enriched_missing = []
                for s in missing:
                    enriched_missing.append({
                        "name": s,
                        **get_enriched_skill_data(s)
                    })
                gap = {"missing_skills": enriched_missing, "market_demand": market}
            else:
                gap = None

            # Fetch letters
            cur.execute(
                "SELECT company, role, content FROM cover_letters WHERE search_run_id = %s", 
                (str(run_uuid),)
            )
            letters = [
                {
                    "company": r[0], 
                    "role": r[1], 
                    "content": r[2]
                } 
                for r in cur.fetchall()
            ]

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
    
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Verify ownership
            cur.execute(
                "SELECT id FROM search_runs WHERE id = %s AND user_id = %s", 
                (str(run_uuid), current_user["id"])
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Run not found or unauthorized.")
            
            # Query job result fields
            cur.execute(
                """
                SELECT company, title, location, match_score, salary, employment_type, source, url, experience_level, work_setting, posted_at 
                FROM job_results 
                WHERE search_run_id = %s 
                ORDER BY match_score DESC
                """,
                (str(run_uuid),)
            )
            rows = cur.fetchall()
            
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
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # 1. Fetch latest active resume details
            cur.execute(
                "SELECT id, extracted_skills, version FROM resumes WHERE user_id = %s AND is_active = TRUE",
                (current_user["id"],)
            )
            resume_row = cur.fetchone()
            if not resume_row:
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
            
            resume_id = resume_row[0]
            skills = resume_row[1]
            if isinstance(skills, str):
                skills = json.loads(skills)
            version = resume_row[2]
            
            # Calculate a resume score out of 100 based on extracted skills
            # (e.g. 60 base score + 5 per skill, capped at 98)
            resume_score = min(98, 60 + 5 * len(skills))
            
            # 2. Count search runs
            cur.execute("SELECT COUNT(*) FROM search_runs WHERE user_id = %s", (current_user["id"],))
            search_runs_count = cur.fetchone()[0]
            
            # 3. Fetch latest run
            cur.execute(
                "SELECT id FROM search_runs WHERE user_id = %s ORDER BY started_at DESC LIMIT 1",
                (current_user["id"],)
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
            
            # 6. Count applications sent (status in Applied, Interview, Offer)
            cur.execute(
                "SELECT COUNT(*) FROM applications WHERE user_id = %s AND status IN ('Applied', 'Interview', 'Offer')",
                (current_user["id"],)
            )
            applications_sent = cur.fetchone()[0]
            
            # Get application statuses breakdown
            cur.execute(
                "SELECT status, COUNT(*) FROM applications WHERE user_id = %s GROUP BY status",
                (current_user["id"],)
            )
            app_breakdown = {r[0]: r[1] for r in cur.fetchall()}
            
            # Ensure standard tracker statuses exist
            for s in ["Generated", "Applied", "Interview", "Rejected", "Offer"]:
                if s not in app_breakdown:
                    app_breakdown[s] = 0
            
            # 7. Collect recent activities
            activities = []
            
            # Resume uploads
            cur.execute("SELECT version, created_at FROM resumes WHERE user_id = %s ORDER BY created_at DESC LIMIT 3", (current_user["id"],))
            for r in cur.fetchall():
                activities.append({
                    "type": "upload",
                    "message": f"Uploaded resume version {r[0]}",
                    "timestamp": r[1].isoformat() if r[1] else None
                })
                
            # Search runs
            cur.execute("SELECT started_at, status FROM search_runs WHERE user_id = %s ORDER BY started_at DESC LIMIT 3", (current_user["id"],))
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
                (current_user["id"],)
            )
            for r in cur.fetchall():
                activities.append({
                    "type": "application",
                    "message": f"Status updated to '{r[0]}' for {r[1]} at {r[2]}",
                    "timestamp": r[3].isoformat() if r[3] else None
                })
            
            # Sort activities by timestamp descending
            activities = [act for act in activities if act["timestamp"] is not None]
            activities.sort(key=lambda x: x["timestamp"], reverse=True)
            activities = activities[:5]
            
            return {
                "has_resume": True,
                "resume_score": resume_score,
                "jobs_found": jobs_found,
                "highest_match": highest_match,
                "applications_sent": applications_sent,
                "missing_skills_count": missing_skills_count,
                "search_runs_count": search_runs_count,
                "recent_activity": activities,
                "app_breakdown": app_breakdown
            }


@router.post("/applications/status")
def update_application_status(req: ApplicationStatusRequest, current_user: dict = Depends(get_current_user)):
    """Logs or updates an application status for a job result match."""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Verify job belongs to user
            cur.execute(
                "SELECT id FROM job_results WHERE id = %s AND user_id = %s",
                (req.job_result_id, current_user["id"])
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail="Job result not found or unauthorized.")
            
            # Insert or update
            cur.execute(
                "SELECT id FROM applications WHERE job_result_id = %s AND user_id = %s",
                (req.job_result_id, current_user["id"])
            )
            row = cur.fetchone()
            now = datetime.datetime.now(datetime.timezone.utc)
            if row:
                cur.execute(
                    "UPDATE applications SET status = %s, updated_at = %s WHERE id = %s",
                    (req.status, now, row[0])
                )
            else:
                cur.execute(
                    "INSERT INTO applications (user_id, job_result_id, status, created_at, updated_at) VALUES (%s, %s, %s, %s, %s)",
                    (current_user["id"], req.job_result_id, req.status, now, now)
                )
            return {"status": "success", "message": f"Application status updated to {req.status}"}


@router.post("/cover-letter/regenerate")
def regenerate_cover_letter_route(req: CoverLetterRegenerateRequest, current_user: dict = Depends(get_current_user)):
    """Triggers an individual LLM regeneration for a specific company cover letter."""
    try:
        run_uuid = UUID(req.run_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format for run_id.")

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Verify owner of search run
            cur.execute(
                "SELECT resume_id FROM search_runs WHERE id = %s AND user_id = %s",
                (str(run_uuid), current_user["id"])
            )
            run_row = cur.fetchone()
            if not run_row:
                raise HTTPException(status_code=404, detail="Run not found or unauthorized.")
            resume_id = run_row[0]

            # Get resume text
            cur.execute(
                "SELECT resume_text FROM resumes WHERE id = %s",
                (resume_id,)
            )
            resume_text = cur.fetchone()[0]

            # Find the job details
            cur.execute(
                "SELECT title, company, description FROM job_results WHERE search_run_id = %s AND company = %s",
                (str(run_uuid), req.company)
            )
            job_row = cur.fetchone()
            if not job_row:
                raise HTTPException(status_code=404, detail="Job result not found for this company.")
            
            job = {
                "title": job_row[0],
                "company": job_row[1],
                "description": job_row[2]
            }

    # Generate new cover letter using Gemini
    from src.application_agent import generate_cover_letter
    try:
        new_content = generate_cover_letter(resume_text, job)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate cover letter: {str(e)}")

    # Save/Update in cover_letters database table
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM cover_letters WHERE search_run_id = %s AND company = %s",
                (str(run_uuid), req.company)
            )
            letter_row = cur.fetchone()
            if letter_row:
                cur.execute(
                    "UPDATE cover_letters SET content = %s, role = %s WHERE id = %s",
                    (new_content, req.role, letter_row[0])
                )
            else:
                cur.execute(
                    "INSERT INTO cover_letters (user_id, search_run_id, company, role, content) VALUES (%s, %s, %s, %s, %s)",
                    (current_user["id"], str(run_uuid), req.company, req.role, new_content)
                )

    return {
        "status": "success",
        "company": req.company,
        "role": req.role,
        "content": new_content
    }
