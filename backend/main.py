import sys
import os
from contextlib import asynccontextmanager

print("==================================================")
print("CAREERLENS BUILD VERSION: 19e1a805a8f60be354f73853df1e1f86686b56bb (WITH_LAZY_IMPORTS)")
print("STARTUP MODE: LAZY")
print("MAIN.PY VERSION: 2026-06-26T19:35:00+05:30")
print("==================================================")

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
    Lifespan context manager that handles server lifecycle events.
    Heavy AI resources are initialized lazily on their first invocation
    to satisfy serverless startup probe constraints.
    """
    print("[LIFESPAN] CareerLens server process starting...")
    yield
    print("[LIFESPAN] CareerLens server process shutting down...")

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
    # Get port dynamically from environment variable to support Cloud Run/Render/Northflank
    port = int(os.getenv("PORT", "8000"))
    # Execute uvicorn server target relative to root search path
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=True)

