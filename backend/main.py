import sys
import os
from contextlib import asynccontextmanager

# Programmatically add project root and AI src directories to python search path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)
sys.path.append(os.path.join(PROJECT_ROOT, "src"))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import uploads, agent, results

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager that handles startup resource preloading
    to prevent first-request latency spikes on production targets.
    """
    print("----- [STARTUP] Preloading CareerLens AI Resources -----")
    
    # 1. Preload SentenceTransformer model
    try:
        from src.services.embedding_service import EmbeddingService
        emb_service = EmbeddingService()
        _ = emb_service.model
        print("[STARTUP] SentenceTransformer model loaded successfully.")
    except Exception as e:
        print(f"[STARTUP] Error loading SentenceTransformer: {e}")

    # 2. Preload spaCy English model
    try:
        from src.skill_extractor import _get_nlp
        _ = _get_nlp()
        print("[STARTUP] spaCy English model loaded successfully.")
    except Exception as e:
        print(f"[STARTUP] Error loading spaCy: {e}")

    # 3. Preload Skill Database and its embeddings cache
    try:
        from src.skill_extractor import get_cached_skills_embeddings
        _, _ = get_cached_skills_embeddings()
        print("[STARTUP] Skills database embeddings cached successfully.")
    except Exception as e:
        print(f"[STARTUP] Error preloading skills embeddings: {e}")

    # 4. Preload FAISS vector store index (from disk if initialized)
    try:
        from src.rag.vector_store import load_index
        load_index()
        print("[STARTUP] FAISS vector index loaded successfully.")
    except Exception as e:
        print(f"[STARTUP] Warning: FAISS index could not be preloaded: {e}")

    # 5. Preload Gemini client
    try:
        from src.application_agent import _get_client
        _ = _get_client()
        print("[STARTUP] Gemini AI Client initialized.")
    except Exception as e:
        print(f"[STARTUP] Warning: Gemini Client could not be preloaded: {e}")

    print("----- [STARTUP] CareerLens Preloading Complete -----")
    yield
    print("[SHUTDOWN] Cleaning up server resources.")

# Initialize FastAPI application with lifespan
app = FastAPI(
    title="CareerLens API",
    description="Production-grade AI Career Assistant Web Backend",
    version="1.0.0",
    lifespan=lifespan
)

# Apply CORS policies for local dev and public staging deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(uploads.router, prefix="/api")
app.include_router(agent.router, prefix="/api")
app.include_router(results.router, prefix="/api")

@app.get("/health")
def health_check():
    """Health probe for deployment target validation."""
    return {"status": "healthy"}

# Mount frontend files at the root of the server
# This matches relative links like dashboard.html and results.html directly
app.mount(
    "/",
    StaticFiles(directory="frontend", html=True),
    name="frontend"
)

if __name__ == "__main__":
    import uvicorn
    # Execute uvicorn server target relative to root search path
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)

