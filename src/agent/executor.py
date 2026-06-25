from agent.planner import decide_next_action
from tools.resume_tool import analyze_resume
from tools.job_search_tool import find_jobs
from tools.ranking_tool import rank_job_results
from tools.skill_gap_tool import analyze_skill_gap
from tools.cover_letter_tool import create_cover_letters
from memory.memory_store import save_resume, save_jobs
from query_generator import generate_queries

def run_agent(goal, resume_path, user_id=1):
    """
    Executes the job agent pipeline for a specific user and goals.
    Fully parameterized to isolate state between multiple users.
    """
    context = {}

    for _ in range(5):
        action = decide_next_action(goal, context)
        print(f"Agent action: {action}")

        if action == "analyze_resume":
            result = analyze_resume(resume_path)
            context.update(result)
            save_resume(user_id, context["resume_text"])

        elif action == "search_jobs":
            # Predict top job roles based on parsed resume text instead of skills keywords
            queries = generate_queries(context["resume_text"])
            jobs = find_jobs(queries)
            context["jobs"] = jobs

        elif action == "rank_jobs":
            ranked = rank_job_results(
                context["resume_text"],
                context["jobs"]
            )
            context["ranked_jobs"] = ranked
            # Save top 20 matches for this specific user
            save_jobs(user_id, ranked[:20])

        elif action == "analyze_skill_gap":
            gap = analyze_skill_gap(
                context["skills"],
                context["ranked_jobs"]
            )
            context["skill_gap"] = gap
            # Decoupled the RAG career advice LLM query from the core automated pipeline loop 
            # to save rate limits and model calls. In production, this can be triggered on-demand.
            print("Skill gap analysis completed.")

        elif action == "generate_cover_letters":
            # Generate cover letters only for the single best match by default (limit=1)
            letters = create_cover_letters(
                context["resume_text"],
                context["ranked_jobs"],
                limit=1
            )
            context["letters"] = letters
            break

    return context