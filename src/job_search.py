import aiohttp
import asyncio
from dotenv import load_dotenv
import os   
load_dotenv()

APP_ID = os.getenv("APP_ID")
APP_KEY = os.getenv("APP_KEY")


async def fetch_jobs(session, query):

    url = "https://api.adzuna.com/v1/api/jobs/in/search/1"

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "what": query,
        "results_per_page": 10
    }

    async with session.get(url, params=params) as response:

        if response.status != 200:
            print(f"API error for query '{query}' → {response.status}")
            return []

        try:
            data = await response.json()
        except Exception:
            print("Invalid JSON response from API")
            return []

        jobs = []

        for job in data.get("results", []):

            jobs.append({
                "company": job["company"]["display_name"],
                "title": job["title"],
                "location": job["location"]["display_name"],
                "description": job["description"],
                "url": job["redirect_url"]
            })

        return jobs


async def search_jobs_parallel(queries):

    semaphore = asyncio.Semaphore(1)  # only one request at a time

    async with aiohttp.ClientSession() as session:

        async def safe_fetch(query):
            async with semaphore:
                await asyncio.sleep(1)  # prevent rate limits
                return await fetch_jobs(session, query)

        tasks = [safe_fetch(q) for q in queries]

        results = await asyncio.gather(*tasks)

        jobs = []

        for r in results:
            jobs.extend(r)

        return jobs