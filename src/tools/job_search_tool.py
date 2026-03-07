import asyncio
from job_search import search_jobs_parallel
from query_generator import generate_queries


def find_jobs(skills):

    queries = generate_queries(skills)

    jobs = asyncio.run(
        search_jobs_parallel(queries[:3])
    )

    return jobs