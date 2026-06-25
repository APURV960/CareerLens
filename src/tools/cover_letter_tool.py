import os
import re
from application_agent import generate_cover_letter

OUTPUT_DIR = "output/cover_letters"

def create_cover_letters(resume_text, jobs, limit=1):
    """
    Creates cover letters for the top matching jobs.
    Defaults to generating for the top 1 job (reducing LLM calls by 80%).
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    letters = []

    # Limit the number of jobs we generate letters for
    target_jobs = jobs[:limit]

    for job in target_jobs:
        try:
            print(f"Generating cover letter for {job['title']} at {job['company']}...")
            letter = generate_cover_letter(resume_text, job)

            # Sanitize company name for file systems
            safe_company = re.sub(r'[^a-zA-Z0-9_]', '_', job["company"].replace(" ", "_"))
            filename = f"{OUTPUT_DIR}/{safe_company}.txt"

            with open(filename, "w", encoding="utf-8") as f:
                f.write(letter)

            letters.append({
                "company": job["company"],
                "file": filename
            })
            print(f"Successfully generated cover letter: {filename}")

        except Exception as e:
            print(f"Cover letter generation failed for {job['company']}: {e}")

    return letters