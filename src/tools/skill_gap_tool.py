from skillgap_analyzer import (
    extract_job_skills,
    compute_skill_gaps,
    market_skill_demand,
    load_skill_db
)


def analyze_skill_gap(resume_skills, jobs):

    skill_db = load_skill_db()

    job_skills = extract_job_skills(jobs, skill_db)

    missing = compute_skill_gaps(resume_skills, job_skills)

    demand = market_skill_demand(job_skills)

    return {
        "missing_skills": missing,
        "market_demand": demand
    }