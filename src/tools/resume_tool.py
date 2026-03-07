from resume_parser import parse_resume
from skill_extractor import extract_skills


def analyze_resume(resume_path):

    resume_text = parse_resume(resume_path)

    skills = extract_skills(resume_text)

    return {
        "resume_text": resume_text,
        "skills": skills
    }