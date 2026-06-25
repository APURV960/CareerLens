import sys
import os

# Programmatically add project root and AI src directories to python search path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)
sys.path.append(os.path.join(PROJECT_ROOT, "src"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import uploads, agent, results

# Initialize FastAPI application
app = FastAPI(
    title="CareerLens API",
    description="Production-grade AI Career Assistant Web Backend",
    version="1.0.0"
)

# Apply CORS policies for local dev and public staging deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(uploads.router, prefix="/api")
app.include_router(agent.router, prefix="/api")
app.include_router(results.router, prefix="/api")

from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

@app.get("/")
def root():
    return {
        "message": "CareerLens API Running",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/routes")
def list_routes():
    routes = []
    for route in app.routes:
        routes.append({
            "type": type(route).__name__,
            "name": getattr(route, "name", None),
            "path": getattr(route, "path", None)
        })
    return routes

@app.get("/health")
def health_check():
    """Health probe for deployment target validation."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    # Execute uvicorn server target relative to root search path
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
