import os
import sys
import json
import numpy as np
import faiss

# Ensure the root project directory is in the import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from services.embedding_service import EmbeddingService

DATA_DIR = "data"
DOCS_DIR = os.path.join(DATA_DIR, "career_doc")
INDEX_PATH = os.path.join(DATA_DIR, "career_doc_index.faiss")
CHUNKS_PATH = os.path.join(DATA_DIR, "career_doc_chunks.json")

def load_documents():
    """Reads all career documents from the data directory."""
    if not os.path.exists(DOCS_DIR):
        print(f"Error: Directory {DOCS_DIR} not found.")
        return []
    
    docs = []
    for filename in os.listdir(DOCS_DIR):
        file_path = os.path.join(DOCS_DIR, filename)
        if os.path.isfile(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    docs.append(content)
    return docs

def build_and_save_index():
    print("Loading career documents...")
    docs = load_documents()
    if not docs:
        print("No documents found to index.")
        return

    print(f"Indexing {len(docs)} documents...")
    emb_service = EmbeddingService()
    embeddings = emb_service.encode(docs)
    
    # Cast to float32 as required by FAISS
    embeddings_np = np.array(embeddings).astype("float32")
    dimension = embeddings_np.shape[1]

    # Create L2 Flat FAISS index
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings_np)

    # Save to disk
    os.makedirs(DATA_DIR, exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    
    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2)

    print("Offline indexing completed successfully!")
    print(f"Saved FAISS index to: {INDEX_PATH}")
    print(f"Saved document chunks to: {CHUNKS_PATH}")

if __name__ == "__main__":
    build_and_save_index()
