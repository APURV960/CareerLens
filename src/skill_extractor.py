import json
import spacy
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


nlp = spacy.load("en_core_web_sm")
model = SentenceTransformer("all-MiniLM-L6-v2")


def load_skill_db():

    with open("data/skillsdb.json") as f:
        return json.load(f)


def extract_phrases(text):

    doc = nlp(text)

    phrases = []

    for chunk in doc.noun_chunks:
        phrases.append(chunk.text.lower())

    return phrases


def build_skill_embeddings(skill_db):

    skills = list(skill_db.keys())

    embeddings = model.encode(skills)

    return skills, embeddings


def detect_skills(phrases, skills, skill_embeddings):

    detected = []

    phrase_embeddings = model.encode(phrases)

    for phrase_emb in phrase_embeddings:

        similarities = cosine_similarity(
            [phrase_emb], skill_embeddings
        )[0]

        best_index = similarities.argmax()
        score = similarities[best_index]

        if score > 0.55:
            detected.append(skills[best_index])

    return list(set(detected))


def extract_skills(resume_text):

    skill_db = load_skill_db()

    phrases = extract_phrases(resume_text)

    skills, skill_embeddings = build_skill_embeddings(skill_db)

    detected_skills = detect_skills(
        phrases, skills, skill_embeddings
    )

    return detected_skills