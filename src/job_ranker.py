from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


model = SentenceTransformer("all-MiniLM-L6-v2")


def rank_jobs(resume_text, jobs):

    if not jobs:
        return jobs

    # Resume embedding
    resume_embedding = model.encode([resume_text])

    # Combine job text
    job_texts = [
        job["title"] + " " + job["description"]
        for job in jobs
    ]

    # Batch embed all jobs
    job_embeddings = model.encode(job_texts)

    # Compute similarity scores
    scores = cosine_similarity(
        resume_embedding,
        job_embeddings
    )[0]

    # Attach scores
    for i, job in enumerate(jobs):
        job["match_score"] = float(scores[i])

    # Sort jobs by score
    ranked_jobs = sorted(
        jobs,
        key=lambda x: x["match_score"],
        reverse=True
    )

    return ranked_jobs