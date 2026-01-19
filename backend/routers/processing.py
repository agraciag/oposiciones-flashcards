"""
Router para procesamiento de temas con IA (Ollama)
Endpoints para procesar, re-procesar y consultar estado de jobs
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from models import (
    Syllabus, StructuredTopic, NormativeSource, ProcessingLog,
    User, SourceType, ContentStatus
)
from auth_utils import get_current_user
from services.ollama_client import OllamaClient, test_ollama_connection, OllamaError
from services.rag_processor import RAGProcessor
from services.job_queue import job_queue, JobStatus

router = APIRouter()


# ============================================================================
# SCHEMAS
# ============================================================================

class ProcessRequest(BaseModel):
    """Request para procesar un tema"""
    extra_context: Optional[str] = None
    use_embeddings: bool = False
    priority: int = 0


class ProcessAllRequest(BaseModel):
    """Request para procesar todos los temas pendientes"""
    extra_context: Optional[str] = None
    only_empty: bool = True  # Solo temas sin contenido


class JobStatusResponse(BaseModel):
    """Respuesta de estado de job"""
    topic_id: int
    status: str
    created_at: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    success: Optional[bool] = None
    error: Optional[str] = None


class TopicSourcesResponse(BaseModel):
    """Respuesta con fuentes de un tema"""
    topic_id: int
    topic_title: str
    source_type: Optional[str] = None
    source_reference: Optional[str] = None
    source_excerpt: Optional[str] = None
    last_processed_at: Optional[str] = None


class QueueStatusResponse(BaseModel):
    """Estado de la cola de procesamiento"""
    pending_jobs: int
    processing_jobs: int
    processing_topic_ids: List[str]
    status: str


class OllamaStatusResponse(BaseModel):
    """Estado de Ollama"""
    available: bool
    url: str
    model: str
    model_available: bool
    models: List[str]
    error: Optional[str] = None


# ============================================================================
# ENDPOINTS - OLLAMA STATUS
# ============================================================================

@router.get("/ollama/status", response_model=OllamaStatusResponse)
async def get_ollama_status(
    current_user: User = Depends(get_current_user)
):
    """Verifica el estado de Ollama"""
    result = await test_ollama_connection()
    return result


@router.post("/ollama/test")
async def test_ollama_generation(
    prompt: str = "Di 'Hola, estoy funcionando' en español",
    current_user: User = Depends(get_current_user)
):
    """Prueba la generación con Ollama"""
    try:
        client = OllamaClient()
        response = await client.generate(prompt, temperature=0.5)
        return {
            "success": True,
            "response": response,
            "model": client.model
        }
    except OllamaError as e:
        raise HTTPException(status_code=503, detail=str(e))


# ============================================================================
# ENDPOINTS - SINGLE TOPIC PROCESSING
# ============================================================================

@router.post("/topics/{topic_id}/process")
async def process_topic(
    topic_id: int,
    request: ProcessRequest = ProcessRequest(),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Inicia el procesamiento de un tema con IA.
    El procesamiento se ejecuta en background a través de la cola.
    """
    # Verificar que el tema existe y pertenece al usuario
    topic = db.query(StructuredTopic).filter(StructuredTopic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Tema no encontrado")

    if topic.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este tema")

    # Verificar que Ollama está disponible
    client = OllamaClient()
    if not await client.is_available():
        raise HTTPException(
            status_code=503,
            detail="Ollama no está disponible. Asegúrate de que está corriendo (ollama serve)"
        )

    # Encolar job
    job_id = await job_queue.enqueue(
        topic_id=topic_id,
        extra_context=request.extra_context,
        use_embeddings=request.use_embeddings,
        priority=request.priority
    )

    return {
        "status": "queued",
        "job_id": job_id,
        "topic_id": topic_id,
        "message": "El tema ha sido encolado para procesamiento"
    }


@router.post("/topics/{topic_id}/process-sync")
async def process_topic_sync(
    topic_id: int,
    request: ProcessRequest = ProcessRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Procesa un tema de forma síncrona (espera el resultado).
    Útil para procesamiento individual donde el usuario espera.
    """
    # Verificar acceso
    topic = db.query(StructuredTopic).filter(StructuredTopic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Tema no encontrado")

    if topic.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este tema")

    # Verificar Ollama
    client = OllamaClient()
    if not await client.is_available():
        raise HTTPException(
            status_code=503,
            detail="Ollama no está disponible"
        )

    # Procesar directamente
    processor = RAGProcessor(db)
    result = await processor.process_topic(
        topic_id=topic_id,
        extra_context=request.extra_context,
        use_embeddings=request.use_embeddings
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=422,
            detail=result.get("error", "Error al procesar el tema")
        )

    return result


@router.post("/topics/{topic_id}/reprocess")
async def reprocess_topic(
    topic_id: int,
    request: ProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Re-procesa un tema con contexto adicional y/o embeddings.
    Útil cuando el primer procesamiento no fue satisfactorio.
    """
    # Verificar acceso
    topic = db.query(StructuredTopic).filter(StructuredTopic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Tema no encontrado")

    if topic.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este tema")

    # Verificar Ollama
    client = OllamaClient()
    if not await client.is_available():
        raise HTTPException(
            status_code=503,
            detail="Ollama no está disponible"
        )

    # Encolar con prioridad alta
    job_id = await job_queue.enqueue(
        topic_id=topic_id,
        extra_context=request.extra_context,
        use_embeddings=request.use_embeddings,
        priority=10  # Alta prioridad para re-procesamiento
    )

    return {
        "status": "queued",
        "job_id": job_id,
        "topic_id": topic_id,
        "message": "El tema ha sido encolado para re-procesamiento",
        "use_embeddings": request.use_embeddings
    }


@router.get("/topics/{topic_id}/job-status")
async def get_job_status(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtiene el estado del procesamiento de un tema"""
    # Verificar acceso
    topic = db.query(StructuredTopic).filter(StructuredTopic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Tema no encontrado")

    if topic.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este tema")

    # Obtener estado de la cola
    job_status = await job_queue.get_status(topic_id)

    if not job_status:
        # No hay job activo, verificar si tiene contenido generado
        if topic.source_type == SourceType.AI_GENERATED and topic.content:
            return {
                "topic_id": topic_id,
                "status": "completed",
                "has_content": True,
                "last_processed_at": topic.last_processed_at.isoformat() if topic.last_processed_at else None
            }
        else:
            return {
                "topic_id": topic_id,
                "status": "not_started",
                "has_content": bool(topic.content)
            }

    return job_status


@router.get("/topics/{topic_id}/sources")
async def get_topic_sources(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene las fuentes originales usadas para generar el contenido de un tema.
    Permite verificar de dónde se extrajo la información.
    """
    # Verificar acceso
    topic = db.query(StructuredTopic).filter(StructuredTopic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Tema no encontrado")

    if topic.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este tema")

    # Obtener fuentes del procesador
    processor = RAGProcessor(db)
    sources = await processor.get_topic_sources(topic_id)

    return sources


# ============================================================================
# ENDPOINTS - BULK PROCESSING
# ============================================================================

@router.post("/syllabi/{syllabus_id}/process-all")
async def process_all_topics(
    syllabus_id: int,
    request: ProcessAllRequest = ProcessAllRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Encola todos los temas pendientes de un temario para procesamiento.
    """
    # Verificar acceso al temario
    syllabus = db.query(Syllabus).filter(Syllabus.id == syllabus_id).first()
    if not syllabus:
        raise HTTPException(status_code=404, detail="Temario no encontrado")

    if syllabus.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este temario")

    # Verificar Ollama
    client = OllamaClient()
    if not await client.is_available():
        raise HTTPException(
            status_code=503,
            detail="Ollama no está disponible"
        )

    # Obtener temas a procesar
    query = db.query(StructuredTopic).filter(
        StructuredTopic.syllabus_id == syllabus_id
    )

    if request.only_empty:
        query = query.filter(
            (StructuredTopic.content == None) |
            (StructuredTopic.content == "") |
            (StructuredTopic.content_status == ContentStatus.EMPTY)
        )

    topics = query.order_by(StructuredTopic.order_index).all()

    if not topics:
        return {
            "status": "no_topics",
            "message": "No hay temas pendientes de procesar"
        }

    # Encolar todos los temas
    topic_ids = [t.id for t in topics]
    job_ids = await job_queue.enqueue_bulk(
        topic_ids=topic_ids,
        extra_context=request.extra_context
    )

    return {
        "status": "queued",
        "topics_queued": len(job_ids),
        "topic_ids": topic_ids,
        "message": f"Se han encolado {len(job_ids)} temas para procesamiento"
    }


@router.get("/syllabi/{syllabus_id}/processing-status")
async def get_syllabus_processing_status(
    syllabus_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Obtiene el estado global de procesamiento de un temario.
    """
    # Verificar acceso
    syllabus = db.query(Syllabus).filter(Syllabus.id == syllabus_id).first()
    if not syllabus:
        raise HTTPException(status_code=404, detail="Temario no encontrado")

    if syllabus.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este temario")

    # Obtener todos los temas del temario
    topics = db.query(StructuredTopic).filter(
        StructuredTopic.syllabus_id == syllabus_id
    ).all()

    # Contar estados
    status_counts = {
        "total": len(topics),
        "empty": 0,
        "processing": 0,
        "completed": 0,
        "ai_generated": 0,
        "manual": 0
    }

    processing_topics = []
    queue_status = await job_queue.get_queue_status()

    for topic in topics:
        # Verificar si está en cola
        job_status = await job_queue.get_status(topic.id)

        if job_status and job_status.get("status") in ["pending", "processing"]:
            status_counts["processing"] += 1
            processing_topics.append({
                "topic_id": topic.id,
                "title": topic.title,
                "status": job_status.get("status")
            })
        elif topic.content and topic.content_status in [ContentStatus.COMPLETE, ContentStatus.VERIFIED]:
            status_counts["completed"] += 1
            if topic.source_type == SourceType.AI_GENERATED:
                status_counts["ai_generated"] += 1
            elif topic.source_type == SourceType.MANUAL:
                status_counts["manual"] += 1
        else:
            status_counts["empty"] += 1

    return {
        "syllabus_id": syllabus_id,
        "syllabus_name": syllabus.name,
        "status_counts": status_counts,
        "processing_topics": processing_topics,
        "queue_status": queue_status,
        "progress_percentage": round(
            (status_counts["completed"] / status_counts["total"] * 100)
            if status_counts["total"] > 0 else 0, 1
        )
    }


# ============================================================================
# ENDPOINTS - QUEUE MANAGEMENT
# ============================================================================

@router.get("/queue/status", response_model=QueueStatusResponse)
async def get_queue_status(
    current_user: User = Depends(get_current_user)
):
    """Obtiene el estado de la cola de procesamiento"""
    status = await job_queue.get_queue_status()
    return status


@router.delete("/queue/clear")
async def clear_queue(
    current_user: User = Depends(get_current_user)
):
    """Limpia la cola de procesamiento (admin only)"""
    # En producción, verificar permisos de admin
    await job_queue.clear_all()
    return {"status": "cleared", "message": "Cola limpiada"}


@router.delete("/topics/{topic_id}/job")
async def clear_topic_job(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancela/limpia el job de un tema específico"""
    # Verificar acceso
    topic = db.query(StructuredTopic).filter(StructuredTopic.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Tema no encontrado")

    if topic.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este tema")

    await job_queue.clear_job(topic_id)

    return {"status": "cleared", "topic_id": topic_id}
