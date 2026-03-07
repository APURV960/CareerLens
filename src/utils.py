def deduplicate(jobs):

    seen = set()
    unique = []

    for job in jobs:

        key = job["title"] + job["company"]

        if key not in seen:
            seen.add(key)
            unique.append(job)

    return unique