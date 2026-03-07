import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


model = SentenceTransformer("all-MiniLM-L6-v2")


def load_roles():

    with open("data/job_roles.json") as f:
        return json.load(f)


def generate_queries(skills):

    roles = load_roles()

    role_embeddings = model.encode(roles)

    queries = []

    for skill in skills:

        skill_embedding = model.encode([skill])

        similarities = cosine_similarity(
            skill_embedding,
            role_embeddings
        )[0]

        best_index = similarities.argmax()

        queries.append(roles[best_index])

    return list(set(queries))