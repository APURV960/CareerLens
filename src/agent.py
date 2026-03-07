from excel_writer import save_jobs
from tools.resume_tool import analyze_resume
from tools.job_search_tool import find_jobs
from tools.ranking_tool import rank_job_results
from tools.skill_gap_tool import analyze_skill_gap
from tools.cover_letter_tool import create_cover_letters


def run_agent():

    print("Goal: Find best jobs and prepare applications")

    resume_data = analyze_resume("data/resume.pdf")

    resume_text = resume_data["resume_text"]
    skills = resume_data["skills"]

    jobs = find_jobs(skills)

    ranked_jobs = rank_job_results(resume_text, jobs)
    ranked_jobs = list({j["url"]: j for j in ranked_jobs}.values())

    gap = analyze_skill_gap(skills, ranked_jobs)

    letters = create_cover_letters(resume_text, ranked_jobs)

    print("\nTop Missing Skills:")
    print(gap["missing_skills"])

    print("\nGenerated Cover Letters:")
    for l in letters:
        print(f"{l['company']}->{l['file']}")

    save_jobs(ranked_jobs)

if __name__ == "__main__":
    run_agent()