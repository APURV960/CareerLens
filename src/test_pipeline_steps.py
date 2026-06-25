import sys
import os
import dotenv
dotenv.load_dotenv()

print("Imports starting...", flush=True)

from agent.planner import decide_next_action
from tools.resume_tool import analyze_resume
from tools.job_search_tool import find_jobs
from tools.ranking_tool import rank_job_results
from tools.skill_gap_tool import analyze_skill_gap
from tools.cover_letter_tool import create_cover_letters
from memory.memory_store import save_resume, save_jobs
from rag.rag_agent import career_advice

print("Imports completed successfully!", flush=True)

# 1. Parse resume
print("\n--- STEP 1: Parse Resume ---", flush=True)
resume_path = "data/resume.pdf"
res = analyze_resume(resume_path)
print(f"Parsed Resume text length: {len(res['resume_text'])}", flush=True)
print(f"Extracted Skills: {res['skills']}", flush=True)

# 2. Save resume to DB
print("\n--- STEP 2: Save Resume to Database ---", flush=True)
save_resume(1, res["resume_text"], res["skills"])
print("Saved resume to database successfully!", flush=True)

# 3. Job search
print("\n--- STEP 3: Job Search ---", flush=True)
from query_generator import generate_queries
queries = generate_queries(res["resume_text"])
jobs = find_jobs(queries)
print(f"Found {len(jobs)} jobs.", flush=True)
if jobs:
    print(f"Sample Job: {jobs[0]}", flush=True)

# 4. Job ranking
print("\n--- STEP 4: Job Ranking ---", flush=True)
ranked_jobs = rank_job_results(res["resume_text"], jobs)
print(f"Ranked {len(ranked_jobs)} jobs.", flush=True)
if ranked_jobs:
    print(f"Top Job: {ranked_jobs[0]}", flush=True)

# 5. Save ranked jobs
print("\n--- STEP 5: Save Ranked Jobs to Database ---", flush=True)
save_jobs(1, ranked_jobs[:20])
print("Saved ranked jobs to database successfully!", flush=True)

# 6. Skill Gap Analysis & Career Advice
print("\n--- STEP 6: Skill Gap Analysis & Advice ---", flush=True)
gap = analyze_skill_gap(res["skills"], ranked_jobs)
print(f"Skill Gap Result: {gap}", flush=True)

print("Fetching career advice...", flush=True)
advice = career_advice("What skills should I learn to become a machine learning engineer?")
print(f"Career Advice output: {advice[:200]}...", flush=True)

# 7. Cover Letter Generation
print("\n--- STEP 7: Cover Letter Generation ---", flush=True)
letters = create_cover_letters(res["resume_text"], ranked_jobs)
print(f"Generated {len(letters)} cover letters.", flush=True)
