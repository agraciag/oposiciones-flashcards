"""
OpositApp - Backend API
Sistema de flashcards con repetición espaciada para oposiciones
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from config import settings
from database import engine, Base
from routers import flashcards, decks, study, auth, legislation, profile, notes, study_docs, syllabi, processing


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events"""
    # Startup
    print("🚀 Iniciando OpositApp Backend...")
    print(f"📊 Conectando a base de datos...")
    Base.metadata.create_all(bind=engine)
    print("✅ Base de datos lista")

    # Iniciar worker de procesamiento con Ollama
    from services.job_queue import start_worker
    from database import SessionLocal
    await start_worker(SessionLocal)
    print("🤖 Worker de procesamiento Ollama iniciado")

    yield

    # Shutdown
    from services.job_queue import stop_worker
    await stop_worker()
    print("👋 Cerrando OpositApp Backend...")


app = FastAPI(
    title="OpositApp API",
    description="Sistema inteligente de flashcards para oposiciones",
    version="0.1.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(profile.router, prefix="/api/profile", tags=["profile"])
app.include_router(decks.router, prefix="/api/decks", tags=["decks"])
app.include_router(flashcards.router, prefix="/api/flashcards", tags=["flashcards"])
app.include_router(study.router, prefix="/api/study", tags=["study"])
app.include_router(legislation.router, prefix="/api/legislation", tags=["legislation"])
app.include_router(notes.router, prefix="/api/notes", tags=["notes"])
app.include_router(study_docs.router, prefix="/api/study-docs", tags=["study-docs"])
app.include_router(syllabi.router, prefix="/api/syllabi", tags=["syllabi"])
app.include_router(processing.router, prefix="/api/processing", tags=["processing"])


@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "ok",
        "app": "OpositApp",
        "version": "0.1.0",
        "message": "API funcionando correctamente 🚀"
    }


@app.get("/api/health")
async def health():
    """Health check detallado"""
    return {
        "status": "healthy",
        "database": "connected",
        "redis": "connected"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=7999,
        reload=settings.DEBUG
    )
