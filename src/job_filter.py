def is_relevant(job, skills):

    description = job["description"].lower()

    score = 0

    for skill in skills:
        if skill in description:
            score += 1

    return score >= 1