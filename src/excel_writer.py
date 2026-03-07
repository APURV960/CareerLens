import pandas as pd


def save_jobs(jobs):

    df = pd.DataFrame(jobs)

    columns = [
        "company",
        "title",
        "location",
        "match_score",
        "job_skills",
        "url"
    ]

    df = df[columns]

    df.to_excel("output/job_matches.xlsx", index=False)

    print("Saved to output/job_matches.xlsx")