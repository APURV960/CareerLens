import json
import os
import spacy
import threading
from services.embedding_service import EmbeddingService
from sklearn.metrics.pairwise import cosine_similarity

_nlp = None
_skill_db = None
_skills_list = None
_skills_embeddings = None
_cache_lock = threading.Lock()

def _get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp

def load_skill_db():
    global _skill_db
    if _skill_db is None:
        with open("data/skillsdb.json", encoding="utf-8") as f:
            _skill_db = json.load(f)
    return _skill_db

def extract_phrases(text):
    nlp = _get_nlp()
    doc = nlp(text)
    phrases = []
    for chunk in doc.noun_chunks:
        phrases.append(chunk.text.lower())
    return phrases

def get_cached_skills_embeddings():
    """
    Retrieves or generates the cached skill database embeddings.
    Guarantees embeddings are computed only once.
    """
    global _skills_list, _skills_embeddings
    if _skills_embeddings is None:
        with _cache_lock:
            if _skills_embeddings is None:
                skill_db = load_skill_db()
                _skills_list = list(skill_db.keys())
                emb_service = EmbeddingService()
                _skills_embeddings = emb_service.encode(_skills_list)
    return _skills_list, _skills_embeddings

def detect_skills(phrases, skills, skill_embeddings):
    if not phrases:
        return []
        
    detected = []
    emb_service = EmbeddingService()
    phrase_embeddings = emb_service.encode(phrases)

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
    # Ensure skills database is loaded and cached
    skills, skill_embeddings = get_cached_skills_embeddings()
    phrases = extract_phrases(resume_text)
    detected_skills = detect_skills(phrases, skills, skill_embeddings)
    return detected_skills