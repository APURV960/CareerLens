import pandas as pd


def save_jobs(jobs):

    if not jobs:
        print("No jobs to save.")
        return
    # Align column names with the rest of the pipeline,
    # which uses lowercase snake_case keys.
    df = pd.DataFrame(jobs)

    desired_columns = [
        "company",
        "title",
        "location",
        "match_score",
        "job_skills",
        "url",
    ]

    # keep only columns that actually exist
    columns = [c for c in desired_columns if c in df.columns]

    if not columns:
        print("No recognized columns on job data; nothing to save.")
        return

    df = df[columns]

    # Deduplicate results: prefer unique posting URL if present; otherwise fall back
    # to a composite identity. Keep the best-scoring row when duplicates exist.
    if "match_score" in df.columns:
        df = df.sort_values("match_score", ascending=False, kind="stable")

    if "url" in df.columns:
        df = df.drop_duplicates(subset=["url"], keep="first")
    else:
        identity_cols = [c for c in ["company", "title", "location"] if c in df.columns]
        if identity_cols:
            df = df.drop_duplicates(subset=identity_cols, keep="first")

    # Make job_skills readable in Excel if it's a list.
    if "job_skills" in df.columns:
        df["job_skills"] = df["job_skills"].apply(
            lambda v: ", ".join(v) if isinstance(v, list) else v
        )

    output_path = "output/job_matches.xlsx"
    try:
        df.to_excel(output_path, index=False)
        print(f"Saved job results to {output_path}")
    except PermissionError:
        # Common on Windows when the file is open in Excel.
        fallback_path = "output/job_matches_NEW.xlsx"
        df.to_excel(fallback_path, index=False)
        print(
            f"Could not overwrite {output_path} (file may be open). "
            f"Saved job results to {fallback_path} instead."
        )