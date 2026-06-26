from services.embedding_service import EmbeddingService
from skillgap_analyzer import load_skill_db
from skill_extractor import extract_skills

def detect_experience_level(text):
    text_lower = text.lower()
    senior_keywords = ["senior", "sr.", "lead", "principal", "architect", "manager", "director", "head of", "5+ years", "8+ years", "10+ years"]
    junior_keywords = ["junior", "jr.", "entry", "intern", "graduate", "apprentice", "0-2 years", "1-2 years"]
    
    is_senior = any(kw in text_lower for kw in senior_keywords)
    is_junior = any(kw in text_lower for kw in junior_keywords)
    
    if is_senior:
        return "Senior"
    elif is_junior:
        return "Junior"
    else:
        return "Mid-Level"

def detect_work_setting(title, description):
    text = (title + " " + description).lower()
    if "remote" in text or "work from home" in text or "wfh" in text or "telecommute" in text:
        return "Remote"
    elif "hybrid" in text or "flexible" in text:
        return "Hybrid"
    else:
        return "Onsite"

def rank_jobs(resume_text, jobs):
    """
    Ranks job postings based on a weighted combination of semantic similarity,
    skill overlap, job title match, experience level match, and location preference.
    """
    if not jobs:
        return jobs

    from sklearn.metrics.pairwise import cosine_similarity
    emb_service = EmbeddingService()

    # 1. Resume embedding and title list extraction
    resume_embedding = emb_service.encode([resume_text])
    try:
        resume_skills = extract_skills(resume_text)
    except Exception as e:
        print(f"Error extracting resume skills in ranker: {e}")
        resume_skills = []
    
    resume_skills_set = set(resume_skills)
    user_experience = detect_experience_level(resume_text)

    # 2. Extract job skills using the skills db for keyword matching
    try:
        skill_db = load_skill_db()
        skill_list = list(skill_db.keys())
    except Exception as e:
        print(f"Error loading skills db in ranker: {e}")
        skill_list = []
        skill_db = {}

    # Combine job title and description for semantic similarity
    job_texts = [
        job["title"] + " " + job["description"]
        for job in jobs
    ]
    job_embeddings = emb_service.encode(job_texts)
    semantic_scores = cosine_similarity(resume_embedding, job_embeddings)[0]

    # Job title embedding for job title match
    job_titles = [job["title"] for job in jobs]
    title_embeddings = emb_service.encode(job_titles)
    title_scores = cosine_similarity(resume_embedding, title_embeddings)[0]

    # Calculate final scores for each job
    final_scores = []
    for i, job in enumerate(jobs):
        # Semantic Score (40%)
        semantic_score = max(0.0, float(semantic_scores[i]))

        # Skill Overlap (25%)
        description_lower = job["description"].lower()
        title_lower = job["title"].lower()
        job_skills = []
        for skill in skill_list:
            syns = skill_db[skill]
            if any(syn in description_lower or syn in title_lower for syn in syns):
                job_skills.append(skill)
        
        job_skills_set = set(job_skills)
        if job_skills_set:
            overlap = len(resume_skills_set.intersection(job_skills_set)) / len(job_skills_set)
        else:
            overlap = 0.5  # Neutral default
        
        # Job Title Match (15%)
        title_score = max(0.0, float(title_scores[i]))

        # Experience Match (10%)
        job_exp = detect_experience_level(job["title"] + " " + job["description"])
        job["experience_level"] = job_exp
        if user_experience == job_exp:
            exp_score = 1.0
        elif user_experience == "Mid-Level" or job_exp == "Mid-Level":
            exp_score = 0.5
        else:
            exp_score = 0.1

        # Location Preference (10%)
        job_setting = detect_work_setting(job["title"], job["description"])
        job["work_setting"] = job_setting
        loc_score = 0.4
        if job_setting == "Remote":
            loc_score = 1.0
        else:
            loc_lower = job["location"].lower()
            if loc_lower and loc_lower in resume_text.lower():
                loc_score = 1.0

        # Weighted calculation:
        # 40% Semantic Similarity, 25% Skill Overlap, 15% Job Title Match, 10% Experience Match, 10% Location Preference
        weighted_score = (
            0.40 * semantic_score +
            0.25 * overlap +
            0.15 * title_score +
            0.10 * exp_score +
            0.10 * loc_score
        )
        final_scores.append(weighted_score)

    # Normalize scores so the best matches surface with strong confidence values (e.g. max match is ~95%)
    max_raw_score = max(final_scores) if final_scores else 1.0
    if max_raw_score > 0:
        scale_factor = 0.95 / max_raw_score
        # Scale scores up to a max of 0.95
        normalized_scores = [min(1.0, s * scale_factor) for s in final_scores]
    else:
        normalized_scores = final_scores

    # Attach scores and other metadata
    for i, job in enumerate(jobs):
        job["match_score"] = float(normalized_scores[i])

    # Sort jobs by score descending
    ranked_jobs = sorted(
        jobs,
        key=lambda x: x["match_score"],
        reverse=True
    )

    return ranked_jobs