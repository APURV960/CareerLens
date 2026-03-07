import os
from application_agent import generate_cover_letter


OUTPUT_DIR = "output/cover_letters"


def create_cover_letters(resume_text, jobs):

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    letters = []

    for job in jobs[:5]:

        try:

            letter = generate_cover_letter(resume_text, job)

            company = job["company"].replace(" ", "_")

            filename = f"{OUTPUT_DIR}/{company}.txt"

            with open(filename, "w", encoding="utf-8") as f:
                f.write(letter)

            letters.append({
                "company": job["company"],
                "file": filename
            })

        except Exception as e:

            print("Cover letter generation failed:", e)

    return letters