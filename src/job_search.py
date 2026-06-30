import aiohttp
import asyncio
from dotenv import load_dotenv
import os   
load_dotenv()

APP_ID = os.getenv("APP_ID")
APP_KEY = os.getenv("APP_KEY")


def determine_job_source(company_name, description):
    desc_lower = (description or "").lower()
    comp_lower = (company_name or "").lower()
    
    # Check for known platforms in description or company name
    if "linkedin" in desc_lower or "linkedin" in comp_lower:
        return "LinkedIn"
    elif "indeed" in desc_lower or "indeed" in comp_lower:
        return "Indeed"
    elif "workday" in desc_lower or "myworkday" in desc_lower:
        return "Workday"
    elif "greenhouse" in desc_lower or "greenhouse.io" in desc_lower:
        return "Greenhouse"
    elif "lever" in desc_lower or "lever.co" in desc_lower:
        return "Lever"
    elif "glassdoor" in desc_lower:
        return "Glassdoor"
    elif "monster" in desc_lower:
        return "Monster"
    elif "simplyhired" in desc_lower:
        return "SimplyHired"
    elif "careerbuilder" in desc_lower:
        return "CareerBuilder"
    elif "ziprecruiter" in desc_lower:
        return "ZipRecruiter"
    else:
        return "Company Careers"


async def fetch_jobs(session, query):

    url = "https://api.adzuna.com/v1/api/jobs/gb/search/1"

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
            try:
                # 1. Print the entire raw job object before any parsing
                import json
                try:
                    print(f"[DEBUG] Raw job object from API: {json.dumps(job, indent=2)}")
                except Exception:
                    pass

                # 2. Validate incoming data (must have title and redirect_url)
                if not job.get("title") or not job.get("redirect_url"):
                    print(f"[WARNING] Skipping job record missing required fields (title/redirect_url): {job}")
                    continue

                # 3. Safely extract salary
                salary_min = job.get("salary_min")
                salary_max = job.get("salary_max")
                if salary_min is not None and salary_max is not None:
                    salary_str = f"INR {salary_min} - {salary_max}"
                elif salary_min is not None:
                    salary_str = f"INR {salary_min}"
                elif salary_max is not None:
                    salary_str = f"INR {salary_max}"
                else:
                    salary_str = "N/A"

                # 4. Safely extract employment type
                emp_type = job.get("contract_time") or "N/A"
                if emp_type != "N/A":
                    emp_type = emp_type.replace("_", " ").title()

                # 4. Safely extract location and work setting
                # (For setting we fallback to Hybrid if not specified, 
                # or derive if remote mentioned in title/description)
                title_lower = job.get("title", "").lower()
                desc_lower = job.get("description", "").lower()
                if "remote" in title_lower or "remote" in desc_lower or "work from home" in title_lower or "work from home" in desc_lower:
                    job["work_setting"] = "Remote"
                else:
                    job["work_setting"] = "Hybrid"

                # 5. Safely extract posted date
                posted_at = job.get("created") or "Just now"

                # 6. Safely extract company name
                company_obj = job.get("company")
                company_name = "N/A"
                if company_obj and isinstance(company_obj, dict):
                    company_name = company_obj.get("display_name") or "N/A"
                elif company_obj and isinstance(company_obj, str):
                    company_name = company_obj

                # 7. Safely extract location name
                location_obj = job.get("location")
                location_name = "N/A"
                if location_obj and isinstance(location_obj, dict):
                    location_name = location_obj.get("display_name") or "N/A"
                elif location_obj and isinstance(location_obj, str):
                    location_name = location_obj

                # 8. Use raw API redirect_url directly
                details_url = job.get("redirect_url") or "N/A"
                original_apply_url = details_url

                # 9. Determine the source platform label
                desc = job.get("description", "N/A")
                source_platform = determine_job_source(company_name, desc)

                jobs.append({
                    "company": company_name,
                    "title": job["title"],
                    "location": location_name,
                    "description": desc,
                    "url": details_url,
                    "original_apply_url": original_apply_url,
                    "salary": salary_str,
                    "employment_type": emp_type,
                    "posted_at": posted_at,
                    "source": source_platform
                })
            except Exception as single_job_err:
                import traceback
                tb_str = traceback.format_exc()
                print(f"[WARNING] Schema-resilience trigger: failed to parse a single job record. Error: {single_job_err}\nTraceback: {tb_str}\nMalformed Job Record: {job}")
                continue

        return jobs


MOCK_JOBS = [
    {
        "company": "Google",
        "title": "Software Engineer, Python",
        "location": "Mountain View, CA",
        "description": "We are looking for a Software Engineer with expertise in Python, machine learning, and SQL. You will build and scale deep learning models, design PostgreSQL databases, and deploy containers on Kubernetes.",
        "url": "https://careers.google.com",
        "original_apply_url": "https://careers.google.com",
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
        "original_apply_url": "https://vercel.com/careers",
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
        "original_apply_url": "https://stripe.com/jobs",
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
        "original_apply_url": "https://netflix.com/careers",
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
        "original_apply_url": "https://amazon.jobs",
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