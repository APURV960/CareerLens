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
            # Extract salary
            salary_min = job.get("salary_min")
            salary_max = job.get("salary_max")
            salary_str = "N/A"
            if salary_min and salary_max:
                salary_str = f"${int(salary_min):,} - ${int(salary_max):,}"
            elif salary_min:
                salary_str = f"${int(salary_min):,}+"
            elif salary_max:
                salary_str = f"Up to ${int(salary_max):,}"

            # Extract employment type
            contract_time = job.get("contract_time") or ""
            contract_type = job.get("contract_type") or ""
            emp_parts = []
            if contract_time:
                emp_parts.append(contract_time.replace("_", "-").title())
            if contract_type:
                emp_parts.append(contract_type.title())
            emp_type = " / ".join(emp_parts) if emp_parts else "Full-Time"

            # Extract created date
            created_raw = job.get("created") or ""
            posted_at = "Recently"
            if created_raw:
                try:
                    posted_at = created_raw.split("T")[0]
                except Exception:
                    pass

            jobs.append({
                "company": job["company"]["display_name"] if job.get("company") else "N/A",
                "title": job["title"],
                "location": job["location"]["display_name"] if job.get("location") else "N/A",
                "description": job["description"],
                "url": job["redirect_url"],
                "salary": salary_str,
                "employment_type": emp_type,
                "posted_at": posted_at,
                "source": "Adzuna"
            })

        return jobs


MOCK_JOBS = [
    {
        "company": "Google",
        "title": "Software Engineer, Python",
        "location": "Mountain View, CA",
        "description": "We are looking for a Software Engineer with expertise in Python, machine learning, and SQL. You will build and scale deep learning models, design PostgreSQL databases, and deploy containers on Kubernetes.",
        "url": "https://careers.google.com",
        "salary": "$150,000 - $190,000",
        "employment_type": "Full-Time",
        "posted_at": "2026-06-24",
        "source": "Google Careers"
    },
    {
        "company": "Vercel",
        "title": "Senior Frontend Engineer (React)",
        "location": "Remote, US",
        "description": "Join Vercel to build the future of the web. Experience with React, Node, CSS, and modern web applications. You will collaborate on core rendering features and optimize page loads.",
        "url": "https://vercel.com/careers",
        "salary": "$160,000 - $210,000",
        "employment_type": "Full-Time",
        "posted_at": "2026-06-23",
        "source": "Vercel Careers"
    },
    {
        "company": "Stripe",
        "title": "Backend Systems Engineer",
        "location": "San Francisco, CA",
        "description": "Work on Stripe's core payments infrastructure. Expertise in SQL, node, Python, and system architecture. Experience with AWS, docker, and kubernetes is highly desired.",
        "url": "https://stripe.com/jobs",
        "salary": "$175,000 - $220,000",
        "employment_type": "Full-Time",
        "posted_at": "2026-06-25",
        "source": "Stripe Jobs"
    },
    {
        "company": "Netflix",
        "title": "Machine Learning Engineer",
        "location": "Los Gatos, CA",
        "description": "Design and build Netflix's recommendation algorithms. Required skills include machine learning, deep learning, python, and data science. Experience with SQL and AWS is a plus.",
        "url": "https://netflix.com/careers",
        "salary": "$250,000 - $350,000",
        "employment_type": "Full-Time",
        "posted_at": "2026-06-22",
        "source": "Netflix Careers"
    },
    {
        "company": "Amazon",
        "title": "Cloud Architect (AWS / Kubernetes)",
        "location": "Seattle, WA",
        "description": "Help customers architect and migrate scalable web applications to AWS. Extensive experience with Kubernetes, Docker, and SQL is required. Excellent communication and design skills.",
        "url": "https://amazon.jobs",
        "salary": "$140,000 - $185,000",
        "employment_type": "Full-Time",
        "posted_at": "2026-06-20",
        "source": "Amazon Jobs"
    }
]


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

        if not jobs:
            print("No jobs found via Adzuna API, returning fallback MOCK_JOBS.")
            return MOCK_JOBS

        return jobs