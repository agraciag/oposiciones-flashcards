"""
Router para temarios estructurados (Syllabi)
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from models import (
    Syllabus, StructuredTopic, NormativeSource, ProcessingLog,
    User, SourceType, ContentStatus, NormativeSourceType
)
from auth_utils import get_current_user
from services.pdf_indexer import PDFIndexerService, index_normativa_folder, search_normativa

router = APIRouter()


# ============================================================================
# SCHEMAS
# ============================================================================

class TopicBase(BaseModel):
    """Base schema para temas"""
    title: str
    code: Optional[str] = None
    content: Optional[str] = None
    source_type: Optional[SourceType] = SourceType.PENDING
    source_reference: Optional[str] = None
    content_status: Optional[ContentStatus] = ContentStatus.EMPTY


class TopicCreate(TopicBase):
    """Schema para crear tema"""
    parent_id: Optional[int] = None
    order_index: int = 0
    level: int = 0


class TopicUpdate(BaseModel):
    """Schema para actualizar tema"""
    title: Optional[str] = None
    code: Optional[str] = None
    content: Optional[str] = None
    source_type: Optional[SourceType] = None
    source_reference: Optional[str] = None
    source_excerpt: Optional[str] = None
    content_status: Optional[ContentStatus] = None
    is_expanded: Optional[bool] = None


class TopicResponse(TopicBase):
    """Schema respuesta tema"""
    id: int
    syllabus_id: int
    parent_id: Optional[int]
    order_index: int
    level: int
    source_excerpt: Optional[str]
    content_status: ContentStatus
    is_expanded: bool
    last_processed_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class TopicTreeResponse(TopicResponse):
    """Schema respuesta tema con hijos"""
    children: List['TopicTreeResponse'] = []

    class Config:
        from_attributes = True


class SyllabusCreate(BaseModel):
    """Schema para crear temario"""
    name: str
    description: Optional[str] = None
    source_file: Optional[str] = None


class SyllabusUpdate(BaseModel):
    """Schema para actualizar temario"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None


class SyllabusResponse(BaseModel):
    """Schema respuesta temario"""
    id: int
    user_id: int
    name: str
    description: Optional[str]
    source_file: Optional[str]
    total_topics: int
    processed_topics: int
    is_public: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class SyllabusDetailResponse(SyllabusResponse):
    """Schema respuesta temario con árbol de temas"""
    topics: List[TopicTreeResponse] = []

    class Config:
        from_attributes = True


class NormativeSourceCreate(BaseModel):
    """Schema para crear fuente normativa"""
    name: str
    code: Optional[str] = None
    source_type: NormativeSourceType = NormativeSourceType.CUSTOM
    file_path: Optional[str] = None
    url: Optional[str] = None


class NormativeSourceResponse(BaseModel):
    """Schema respuesta fuente normativa"""
    id: int
    name: str
    code: Optional[str]
    source_type: NormativeSourceType
    file_path: Optional[str]
    url: Optional[str]
    is_indexed: bool
    indexed_at: Optional[datetime]
    file_size: Optional[int]
    page_count: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# HELPERS
# ============================================================================

def build_topic_tree(topics: List[StructuredTopic], parent_id: Optional[int] = None) -> List[dict]:
    """Construir árbol de temas recursivamente"""
    result = []
    for topic in topics:
        if topic.parent_id == parent_id:
            topic_dict = {
                "id": topic.id,
                "syllabus_id": topic.syllabus_id,
                "parent_id": topic.parent_id,
                "order_index": topic.order_index,
                "level": topic.level,
                "title": topic.title,
                "code": topic.code,
                "content": topic.content,
                "source_type": topic.source_type,
                "source_reference": topic.source_reference,
                "source_excerpt": topic.source_excerpt,
                "content_status": topic.content_status,
                "is_expanded": topic.is_expanded,
                "last_processed_at": topic.last_processed_at,
                "created_at": topic.created_at,
                "updated_at": topic.updated_at,
                "children": build_topic_tree(topics, topic.id)
            }
            result.append(topic_dict)
    return sorted(result, key=lambda x: x["order_index"])


def count_topics_by_status(topics: List[StructuredTopic]) -> tuple:
    """Contar temas totales y procesados"""
    total = len(topics)
    processed = sum(1 for t in topics if t.content_status in [ContentStatus.COMPLETE, ContentStatus.VERIFIED])
    return total, processed


# ============================================================================
# ENDPOINTS - SYLLABI
# ============================================================================

@router.post("/syllabi", response_model=SyllabusResponse, status_code=status.HTTP_201_CREATED)
def create_syllabus(
    syllabus: SyllabusCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear nuevo temario"""
    db_syllabus = Syllabus(
        user_id=current_user.id,
        name=syllabus.name,
        description=syllabus.description,
        source_file=syllabus.source_file
    )
    db.add(db_syllabus)
    db.commit()
    db.refresh(db_syllabus)
    return db_syllabus


@router.get("/syllabi", response_model=List[SyllabusResponse])
def get_my_syllabi(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener mis temarios"""
    syllabi = db.query(Syllabus).filter(Syllabus.user_id == current_user.id).all()

    # Actualizar contadores
    for syllabus in syllabi:
        topics = db.query(StructuredTopic).filter(StructuredTopic.syllabus_id == syllabus.id).all()
        total, processed = count_topics_by_status(topics)
        syllabus.total_topics = total
        syllabus.processed_topics = processed

    db.commit()
    return syllabi


@router.get("/syllabi/{syllabus_id}", response_model=SyllabusDetailResponse)
def get_syllabus(
    syllabus_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener temario con árbol de temas"""
    syllabus = db.query(Syllabus).filter(Syllabus.id == syllabus_id).first()
    if not syllabus:
        raise HTTPException(status_code=404, detail="Temario no encontrado")

    if syllabus.user_id != current_user.id and not syllabus.is_public:
        raise HTTPException(status_code=403, detail="No tienes acceso a este temario")

    # Obtener todos los temas y construir árbol
    topics = db.query(StructuredTopic).filter(StructuredTopic.syllabus_id == syllabus_id).all()
    total, processed = count_topics_by_status(topics)

    return {
        "id": syllabus.id,
        "user_id": syllabus.user_id,
        "name": syllabus.name,
        "description": syllabus.description,
        "source_file": syllabus.source_file,
        "total_topics": total,
        "processed_topics": processed,
        "is_public": syllabus.is_public,
        "created_at": syllabus.created_at,
        "updated_at": syllabus.updated_at,
        "topics": build_topic_tree(topics)
    }


@router.put("/syllabi/{syllabus_id}", response_model=SyllabusResponse)
def update_syllabus(
    syllabus_id: int,
    syllabus_update: SyllabusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar temario"""
    db_syllabus = db.query(Syllabus).filter(Syllabus.id == syllabus_id).first()
    if not db_syllabus:
        raise HTTPException(status_code=404, detail="Temario no encontrado")

    if db_syllabus.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este temario")

    update_data = syllabus_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_syllabus, field, value)

    db.commit()
    db.refresh(db_syllabus)
    return db_syllabus


@router.delete("/syllabi/{syllabus_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_syllabus(
    syllabus_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar temario"""
    db_syllabus = db.query(Syllabus).filter(Syllabus.id == syllabus_id).first()
    if not db_syllabus:
        raise HTTPException(status_code=404, detail="Temario no encontrado")

    if db_syllabus.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este temario")

    db.delete(db_syllabus)
    db.commit()
    return None


# ============================================================================
# ENDPOINTS - TOPICS
# ============================================================================

@router.post("/syllabi/{syllabus_id}/topics", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
def create_topic(
    syllabus_id: int,
    topic: TopicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear nuevo tema en un temario"""
    syllabus = db.query(Syllabus).filter(Syllabus.id == syllabus_id).first()
    if not syllabus:
        raise HTTPException(status_code=404, detail="Temario no encontrado")

    if syllabus.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este temario")

    # Verificar parent_id si existe
    if topic.parent_id:
        parent = db.query(StructuredTopic).filter(
            StructuredTopic.id == topic.parent_id,
            StructuredTopic.syllabus_id == syllabus_id
        ).first()
        if not parent:
            raise HTTPException(status_code=400, detail="Tema padre no encontrado")

    db_topic = StructuredTopic(
        user_id=current_user.id,
        syllabus_id=syllabus_id,
        parent_id=topic.parent_id,
        order_index=topic.order_index,
        level=topic.level,
        title=topic.title,
        code=topic.code,
        content=topic.content,
        source_type=topic.source_type,
        source_reference=topic.source_reference,
        content_status=topic.content_status
    )
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic


@router.put("/topics/{topic_id}", response_model=TopicResponse)
def update_topic(
    topic_id: int,
    topic_update: TopicUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar tema"""
    db_topic = db.query(StructuredTopic).filter(StructuredTopic.id == topic_id).first()
    if not db_topic:
        raise HTTPException(status_code=404, detail="Tema no encontrado")

    if db_topic.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este tema")

    update_data = topic_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_topic, field, value)

    db.commit()
    db.refresh(db_topic)
    return db_topic


@router.delete("/topics/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar tema"""
    db_topic = db.query(StructuredTopic).filter(StructuredTopic.id == topic_id).first()
    if not db_topic:
        raise HTTPException(status_code=404, detail="Tema no encontrado")

    if db_topic.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este tema")

    db.delete(db_topic)
    db.commit()
    return None


@router.post("/topics/{topic_id}/toggle-expand")
def toggle_topic_expand(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Alternar estado expandido/colapsado de un tema"""
    db_topic = db.query(StructuredTopic).filter(StructuredTopic.id == topic_id).first()
    if not db_topic:
        raise HTTPException(status_code=404, detail="Tema no encontrado")

    if db_topic.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este tema")

    db_topic.is_expanded = not db_topic.is_expanded
    db.commit()

    return {"is_expanded": db_topic.is_expanded}


# ============================================================================
# ENDPOINTS - NORMATIVE SOURCES
# ============================================================================

@router.get("/normative-sources", response_model=List[NormativeSourceResponse])
def get_normative_sources(
    indexed_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener fuentes normativas"""
    query = db.query(NormativeSource)
    if indexed_only:
        query = query.filter(NormativeSource.is_indexed == True)
    return query.all()


@router.post("/normative-sources", response_model=NormativeSourceResponse, status_code=status.HTTP_201_CREATED)
def create_normative_source(
    source: NormativeSourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Registrar nueva fuente normativa"""
    db_source = NormativeSource(
        name=source.name,
        code=source.code,
        source_type=source.source_type,
        file_path=source.file_path,
        url=source.url
    )
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source


@router.delete("/normative-sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_normative_source(
    source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar fuente normativa"""
    db_source = db.query(NormativeSource).filter(NormativeSource.id == source_id).first()
    if not db_source:
        raise HTTPException(status_code=404, detail="Fuente no encontrada")

    db.delete(db_source)
    db.commit()
    return None


# ============================================================================
# ENDPOINTS - STATS
# ============================================================================

@router.get("/syllabi/{syllabus_id}/stats")
def get_syllabus_stats(
    syllabus_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener estadísticas de progreso del temario"""
    syllabus = db.query(Syllabus).filter(Syllabus.id == syllabus_id).first()
    if not syllabus:
        raise HTTPException(status_code=404, detail="Temario no encontrado")

    if syllabus.user_id != current_user.id and not syllabus.is_public:
        raise HTTPException(status_code=403, detail="No tienes acceso a este temario")

    topics = db.query(StructuredTopic).filter(StructuredTopic.syllabus_id == syllabus_id).all()

    by_status = {
        "empty": 0,
        "partial": 0,
        "complete": 0,
        "verified": 0
    }
    by_source = {
        "normativa": 0,
        "manual": 0,
        "ai_generated": 0,
        "pending": 0
    }

    for topic in topics:
        by_status[topic.content_status.value] += 1
        by_source[topic.source_type.value] += 1

    total = len(topics)
    processed = by_status["complete"] + by_status["verified"]

    return {
        "total_topics": total,
        "processed_topics": processed,
        "progress_percentage": round((processed / total * 100) if total > 0 else 0, 1),
        "by_status": by_status,
        "by_source": by_source
    }


# ============================================================================
# ENDPOINTS - INDEXACIÓN Y BÚSQUEDA
# ============================================================================

@router.post("/index-normativa")
def index_normativa_endpoint(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Indexa todos los PDFs de la carpeta de normativa.
    Se ejecuta en background.
    """
    # Ejecutar en background para no bloquear
    def do_indexing():
        try:
            results = index_normativa_folder(db)
            print(f"✅ Indexación completada: {len(results)} archivos")
        except Exception as e:
            print(f"❌ Error en indexación: {e}")

    background_tasks.add_task(do_indexing)

    return {
        "status": "started",
        "message": "Indexación iniciada en background"
    }


@router.post("/normative-sources/{source_id}/index")
def index_single_source(
    source_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Indexar una fuente normativa específica"""
    source = db.query(NormativeSource).filter(NormativeSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Fuente no encontrada")

    if not source.file_path:
        raise HTTPException(status_code=400, detail="La fuente no tiene archivo asociado")

    indexer = PDFIndexerService(db)
    try:
        updated = indexer.index_pdf(source.file_path, source.name)
        return {
            "status": "success",
            "source_id": updated.id,
            "is_indexed": updated.is_indexed,
            "page_count": updated.page_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al indexar: {str(e)}")


class SearchQuery(BaseModel):
    """Schema para búsqueda"""
    query: str
    source_type: Optional[NormativeSourceType] = None
    limit: int = 10


@router.post("/search-normativa")
def search_normativa_endpoint(
    search: SearchQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Busca en las fuentes normativas indexadas.
    Retorna fragmentos relevantes con contexto.
    """
    indexer = PDFIndexerService(db)
    results = indexer.search_in_sources(
        query=search.query,
        source_type=search.source_type,
        limit=search.limit
    )

    return {
        "query": search.query,
        "total_results": len(results),
        "results": results
    }


@router.get("/indexing-stats")
def get_indexing_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener estadísticas de indexación"""
    indexer = PDFIndexerService(db)
    return indexer.get_indexing_stats()
