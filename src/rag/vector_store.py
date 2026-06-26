import faiss
import numpy as np
import os
import json
import threading
from services.embedding_service import EmbeddingService

INDEX_PATH = "data/career_doc_index.faiss"
CHUNKS_PATH = "data/career_doc_chunks.json"

_index = None
_documents = None
_lock = threading.Lock()

def load_index():
    """
    Thread-safe lazy loading of the FAISS index and documents from disk.
    """
    global _index, _documents
    if _index is None:
        with _lock:
            if _index is None:
                if not os.path.exists(INDEX_PATH) or not os.path.exists(CHUNKS_PATH):
                    raise RuntimeError(
                        f"FAISS Index files not initialized at {INDEX_PATH}. "
                        "Please run 'src/rag/initialize_index.py' first."
                    )
                print(f"[FAISS] Loading FAISS index from {INDEX_PATH} lazily...")
                _index = faiss.read_index(INDEX_PATH)
                with open(CHUNKS_PATH, "r", encoding="utf-8") as f:
                    _documents = json.load(f)
                print(f"[FAISS] FAISS index loaded successfully with {len(_documents)} documents.")

def build_index(text_chunks):
    """
    Builds and registers index in-memory (useful for dynamic scenarios or testing).
    Updates global state in a thread-safe manner.
    """
    global _index, _documents
    emb_service = EmbeddingService()
    embeddings = emb_service.encode(text_chunks)
    
    embeddings_np = np.array(embeddings).astype("float32")
    dimension = embeddings_np.shape[1]

    new_index = faiss.IndexFlatL2(dimension)
    new_index.add(embeddings_np)

    with _lock:
        _index = new_index
        _documents = text_chunks

def search(query, k=3):
    """
    Searches the FAISS index for the most similar career advice chunks.
    """
    global _index, _documents
    
    # Ensure index is loaded (from disk if not already built in memory)
    if _index is None:
        load_index()

    emb_service = EmbeddingService()
    query_vector = emb_service.encode([query])
    query_np = np.array(query_vector).astype("float32")

    distances, indices = _index.search(query_np, k)

    results = []
    for i in indices[0]:
        # Protect against out of range index results
        if 0 <= i < len(_documents):
            results.append(_documents[i])

    return results