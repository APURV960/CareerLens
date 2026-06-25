import numpy as np
import threading
from services.embedding_service import EmbeddingService

# Thread lock for memory access
_memory_lock = threading.Lock()

# Multi-tenant memory dictionary: user_id -> list of embeddings
_user_memory = {}

def store_vector(text, user_id=1):
    """
    Encodes and stores an embedding vector associated with a specific user.
    """
    global _user_memory
    emb_service = EmbeddingService()
    embedding = emb_service.encode(text)

    with _memory_lock:
        if user_id not in _user_memory:
            _user_memory[user_id] = []
        _user_memory[user_id].append(embedding)

    return embedding

def search_memory(query, user_id=1):
    """
    Searches vectors associated only with the specified user.
    """
    global _user_memory
    emb_service = EmbeddingService()
    query_embedding = emb_service.encode(query)

    with _memory_lock:
        user_vectors = _user_memory.get(user_id, [])

    if not user_vectors:
        return []

    similarities = []
    for vec in user_vectors:
        # Dot product for cosine similarity (assuming normalized vectors)
        score = float(np.dot(query_embedding, vec))
        similarities.append(score)

    return similarities