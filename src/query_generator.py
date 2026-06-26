import json
import threading
import numpy as np
from services.embedding_service import EmbeddingService

_roles = None
_role_embeddings = None
_cache_lock = threading.Lock()


def load_roles():
    global _roles
    if _roles is None:
        with open("data/job_roles.json", encoding="utf-8") as f:
            _roles = json.load(f)
    return _roles


def get_cached_role_embeddings():
    global _roles, _role_embeddings

    if _role_embeddings is None:
        with _cache_lock:
            if _role_embeddings is None:
                roles = load_roles()
                emb_service = EmbeddingService()
                _role_embeddings = emb_service.encode(roles)

    return _roles, _role_embeddings


def generate_queries(resume_text, top_k=5):

    if not resume_text:
        return []

    from sklearn.metrics.pairwise import cosine_similarity
    roles, role_embeddings = get_cached_role_embeddings()

    emb_service = EmbeddingService()

    resume_embedding = emb_service.encode([resume_text])

    similarities = cosine_similarity(
        resume_embedding,
        role_embeddings
    )[0]

    top_indices = np.argsort(similarities)[::-1][:top_k]

    return [roles[i] for i in top_indices]

