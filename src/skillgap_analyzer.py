import json
from collections import Counter


def load_skill_db():

    with open("data/skillsdb.json") as f:
        return json.load(f)


def extract_job_skills(jobs, skill_db):

    job_skills = []

    skill_list = list(skill_db.keys())

    for job in jobs:

        description = job["description"].lower()

        skills_found = []

        for skill in skill_list:
            if skill in description:
                skills_found.append(skill)

        job["job_skills"] = skills_found

        job_skills.extend(skills_found)

    return job_skills


def compute_skill_gaps(resume_skills, job_skills):

    missing = []

    for skill in job_skills:

        if skill not in resume_skills:
            missing.append(skill)

    return list(set(missing))


def market_skill_demand(job_skills):

    counter = Counter(job_skills)

    return counter.most_common(10)