# Technical Walkthrough — Google Cloud Run Production Startup Refactoring

This document summarizes the changes, refactoring patterns, and verification tests completed to prepare CareerLens for Google Cloud Run deployment by moving to lazy resource initialization.

---

## 1. Architectural Changes for Startup Probe Compliance

To satisfy Google Cloud Run's strict startup check constraints (where Uvicorn must bind to the dynamic port immediately), we migrated heavy initialization steps from server boot time to thread-safe lazy loaders:

### 1. Lazy Database Connection Pooling (`backend/repositories/db_pool.py`)
* Wrapped the `ThreadedConnectionPool` initialization inside a thread-safe helper `_get_pool()`.
* The connection pool is no longer initialized during module import, avoiding blocking on startup if the database is in a cold state.
* Added detailed logs when the pool is created.

### 2. Lifespan Optimization (`backend/main.py`)
* Removed all heavy preloading blocks inside the `lifespan` handler. The lifespan now only logs server startup and shutdown messages.
* Enabled immediate port binding, allowing the server process to start within milliseconds.
* The `/health` endpoint is registered before static files to ensure immediate responsiveness.

### 3. AI Service Lazy Loading & Logs
* **SentenceTransformer** (`src/services/embedding_service.py`): Injected logs before and after `SentenceTransformer` instantiation inside the lazy model getter property.
* **spaCy & Skills Cache** (`src/skill_extractor.py`): Added lazy-load print statements in `_get_nlp()` and `get_cached_skills_embeddings()`.
* **FAISS Index** (`src/rag/vector_store.py`): Configured `load_index()` to log before and after reading the FAISS index from disk.
* **Gemini Client** (`src/application_agent.py` & `src/rag/rag_agent.py`): Injected lazy initialization log tags before and after `genai.Client` instantiation.

### 4. Docker Dynamic Port Binding (`Dockerfile`)
* Changed `EXPOSE` to `8080`.
* Configured the container `CMD` to shell format to dynamically bind to the `$PORT` environment variable:
  `CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8080}"]`

---

## 2. Local Verification Results

### 1. Millisecond Server Boot & Immediate Health Check Response
We started Uvicorn locally on port `8080` and queried the `/health` endpoint:
```
INFO:     Started server process [25232]
INFO:     Waiting for application startup.
[LIFESPAN] CareerLens server process starting...
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8080 (Press CTRL+C to quit)
INFO:     127.0.0.1:52494 - "GET /health HTTP/1.1" 200 OK
```
Startup completes in milliseconds, and the health check responds with `{"status": "healthy"}` instantly without loading any heavy AI models.

### 2. Lazy Model and Pool Initialization Logs
We executed a simulated resume upload to trigger processing. The logs confirm that the connection pool, SentenceTransformer model, skills database embeddings, and spaCy models are initialized dynamically only on first request:
```
[DATABASE] Creating ThreadedConnectionPool lazily...
[DATABASE] ThreadedConnectionPool initialized successfully.
[SKILL CACHE] Generating skill database embeddings lazily...
[AI MODEL] Initializing SentenceTransformer('all-MiniLM-L6-v2') lazily...
[AI MODEL] SentenceTransformer model loaded successfully.
[SKILL CACHE] Successfully cached 10 skill embeddings.
[SPACY] Loading model 'en_core_web_sm' lazily...
[SPACY] Model 'en_core_web_sm' loaded successfully.
Upload Response Status: 200
Upload Response JSON: {'resume_id': 2, 'version': 1, 'skills': ['sql', 'docker', 'node', 'react', 'machine learning', 'python'], 'session_id': '11111111-1111-1111-1111-111111111111'}
```
Subsequent requests bypass the initialization overhead completely, running instantly.
