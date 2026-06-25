import asyncio
from job_search import search_jobs_parallel

def find_jobs(queries):
    """
    Finds job postings by searching the Adzuna API in parallel 
    using the provided predicted role queries.
    """
    jobs = asyncio.run(
        search_jobs_parallel(queries[:3])
    )
    print(f"Jobs found: {len(jobs)}")

    for job in jobs[:10]:
        print(job["title"], "-", job["company"])
    return jobs