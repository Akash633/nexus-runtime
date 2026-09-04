from fastapi import FastAPI
from app.api.agents import router as agents_router

app = FastAPI(
    title="Nexus Runtime",
    description="Enterprise AI Runtime Platform with Adaptive Runtime Intelligence",
    version="0.1.0"
)
app.include_router(agents_router)


@app.get("/")
def root():
    return {
        "project": "Nexus Runtime",
        "status": "running",
        "version": "0.1.0"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }