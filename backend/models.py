"""
Modelos de base de datos
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from database import Base


class StudyQuality(str, enum.Enum):
    """Calidad de respuesta en estudio"""
    AGAIN = "again"      # 0 - No la sabía
    HARD = "hard"        # 2 - Difícil
    GOOD = "good"        # 3 - Bien
    EASY = "easy"        # 4 - Fácil


class NoteType(str, enum.Enum):
    """Tipo de nota"""
    SECTION = "section"    # Sección/encabezado sin contenido propio
    CONTENT = "content"    # Contenido real (texto, markdown)


class CollectionType(str, enum.Enum):
    """Tipo de colección de notas"""
    TEMARIO = "temario"        # Temario de oposición
    NORMATIVA = "normativa"    # Normativa completa
    CUSTOM = "custom"          # Colección personalizada


class User(Base):
    """Usuario del sistema"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    telegram_id = Column(String, unique=True, nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    decks = relationship("Deck", back_populates="user", cascade="all, delete-orphan")
    study_sessions = relationship("StudySession", back_populates="user")
    notes = relationship("Note", back_populates="user", cascade="all, delete-orphan")
    note_collections = relationship("NoteCollection", back_populates="user", cascade="all, delete-orphan")
    study_documents = relationship("StudyDocument", back_populates="user", cascade="all, delete-orphan")
    syllabi = relationship("Syllabus", back_populates="user", cascade="all, delete-orphan")
    structured_topics = relationship("StructuredTopic", back_populates="user", cascade="all, delete-orphan")


class Deck(Base):
    """Mazo de flashcards"""
    __tablename__ = "decks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Sharing features
    is_public = Column(Boolean, default=False, index=True)
    original_deck_id = Column(Integer, ForeignKey("decks.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    user = relationship("User", back_populates="decks")
    flashcards = relationship("Flashcard", back_populates="deck", cascade="all, delete-orphan")
    
    # Self-referential relationship for clones (optional but good for tracking)
    clones = relationship("Deck", back_populates="original_deck", remote_side=[id])
    original_deck = relationship("Deck", back_populates="clones", remote_side=[original_deck_id])


class Flashcard(Base):
    """Tarjeta de estudio (flashcard)"""
    __tablename__ = "flashcards"

    id = Column(Integer, primary_key=True, index=True)
    deck_id = Column(Integer, ForeignKey("decks.id"), nullable=False)

    # Contenido
    front = Column(Text, nullable=False)  # Pregunta
    back = Column(Text, nullable=False)   # Respuesta
    tags = Column(String, nullable=True)  # Etiquetas separadas por comas

    # Metadatos legislativos (opcional)
    legal_reference = Column(String, nullable=True)  # Ej: "BOE-A-1978-31229"
    article_number = Column(String, nullable=True)   # Ej: "Art. 15 CE"
    law_name = Column(String, nullable=True)         # Ej: "Constitución Española"
    last_verified = Column(DateTime(timezone=True), nullable=True)  # Última verificación BOE

    # Referencia a notas/apuntes (opcional)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=True)

    # Algoritmo SM-2
    repetitions = Column(Integer, default=0)
    easiness_factor = Column(Float, default=2.5)
    interval_days = Column(Integer, default=0)
    next_review = Column(DateTime(timezone=True), default=func.now())

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    deck = relationship("Deck", back_populates="flashcards")
    study_logs = relationship("StudyLog", back_populates="flashcard")
    note = relationship("Note", back_populates="flashcards")


class StudySession(Base):
    """Sesión de estudio"""
    __tablename__ = "study_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)

    cards_studied = Column(Integer, default=0)
    cards_correct = Column(Integer, default=0)
    cards_incorrect = Column(Integer, default=0)

    # Relaciones
    user = relationship("User", back_populates="study_sessions")
    study_logs = relationship("StudyLog", back_populates="session")


class StudyLog(Base):
    """Registro de cada review de una flashcard"""
    __tablename__ = "study_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("study_sessions.id"), nullable=False)
    flashcard_id = Column(Integer, ForeignKey("flashcards.id"), nullable=False)

    quality = Column(Enum(StudyQuality), nullable=False)
    time_spent_seconds = Column(Integer, nullable=True)

    # SM-2 values ANTES de esta review
    repetitions_before = Column(Integer)
    easiness_before = Column(Float)
    interval_before = Column(Integer)

    # SM-2 values DESPUÉS de esta review
    repetitions_after = Column(Integer)
    easiness_after = Column(Float)
    interval_after = Column(Integer)
    next_review_after = Column(DateTime(timezone=True))

    reviewed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    session = relationship("StudySession", back_populates="study_logs")
    flashcard = relationship("Flashcard", back_populates="study_logs")


class LegislationUpdate(Base):
    """Registro de actualizaciones legislativas detectadas"""
    __tablename__ = "legislation_updates"

    id = Column(Integer, primary_key=True, index=True)

    # Identificación
    boe_id = Column(String, unique=True, index=True, nullable=False)  # Ej: BOE-A-2026-00234
    law_name = Column(String, nullable=False)
    publication_date = Column(DateTime(timezone=True), nullable=False)

    # Análisis
    summary = Column(Text, nullable=True)  # Resumen cambios (generado por IA)
    affects_flashcards = Column(Boolean, default=False)
    affected_cards_count = Column(Integer, default=0)

    # Notificación
    users_notified = Column(Integer, default=0)
    notified_at = Column(DateTime(timezone=True), nullable=True)

    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    processed = Column(Boolean, default=False)


class Note(Base):
    """Nota/apunte de contenido reutilizable"""
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Contenido
    title = Column(String, nullable=False)
    content = Column(Text, nullable=True)  # Markdown o texto plano
    note_type = Column(Enum(NoteType), default=NoteType.CONTENT, nullable=False)

    # Etiquetas y metadatos
    tags = Column(String, nullable=True)  # importante,examen,básico
    legal_reference = Column(String, nullable=True)  # Ej: "BOE-A-1978-31229"
    article_number = Column(String, nullable=True)   # Ej: "Art. 15 CE"

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    user = relationship("User", back_populates="notes")
    flashcards = relationship("Flashcard", back_populates="note")
    hierarchies = relationship("NoteHierarchy", back_populates="note", cascade="all, delete-orphan")


class NoteCollection(Base):
    """Colección/vista de notas (Temario, Normativa, etc.)"""
    __tablename__ = "note_collections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Información básica
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    collection_type = Column(Enum(CollectionType), default=CollectionType.CUSTOM, nullable=False)

    # Sharing features
    is_public = Column(Boolean, default=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    user = relationship("User", back_populates="note_collections")
    hierarchies = relationship("NoteHierarchy", back_populates="collection", cascade="all, delete-orphan")


class NoteHierarchy(Base):
    """Estructura de árbol que conecta notas con colecciones"""
    __tablename__ = "note_hierarchies"

    id = Column(Integer, primary_key=True, index=True)
    collection_id = Column(Integer, ForeignKey("note_collections.id"), nullable=False)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=False)

    # Jerarquía
    parent_id = Column(Integer, ForeignKey("note_hierarchies.id"), nullable=True)
    order_index = Column(Integer, default=0, nullable=False)  # Orden entre hermanos

    # Características especiales
    is_featured = Column(Boolean, default=False)  # Destacar en temario

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    collection = relationship("NoteCollection", back_populates="hierarchies")
    note = relationship("Note", back_populates="hierarchies")

    # Self-referential relationship para árbol
    children = relationship("NoteHierarchy", back_populates="parent", remote_side=[id])
    parent = relationship("NoteHierarchy", back_populates="children", remote_side=[parent_id])


class StudyDocument(Base):
    """Documento de estudio interactivo (tipo Wikipedia)"""
    __tablename__ = "study_documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Contenido
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)  # El texto base (temario)
    description = Column(Text, nullable=True)

    # Sharing
    is_public = Column(Boolean, default=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    user = relationship("User", back_populates="study_documents")
    annotations = relationship("StudyAnnotation", back_populates="document", cascade="all, delete-orphan")


class StudyAnnotation(Base):
    """Anotación/enlace dentro de un documento de estudio"""
    __tablename__ = "study_annotations"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("study_documents.id"), nullable=False)

    # Posición en el texto
    start_pos = Column(Integer, nullable=False)  # Posición inicial del texto seleccionado
    end_pos = Column(Integer, nullable=False)    # Posición final del texto seleccionado
    selected_text = Column(String, nullable=False)  # El texto seleccionado (para verificación)

    # Contenido vinculado
    annotation_title = Column(String, nullable=True)  # Título opcional para TOC
    linked_content = Column(Text, nullable=False)  # Contenido expandible (markdown)

    # Metadatos opcionales
    legal_reference = Column(String, nullable=True)
    article_number = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    document = relationship("StudyDocument", back_populates="annotations")


# ============================================================================
# NUEVOS MODELOS: Sistema de Temarios Estructurados
# ============================================================================

class SourceType(str, enum.Enum):
    """Tipo de fuente de contenido"""
    NORMATIVA = "normativa"      # Extraído de normativa local
    MANUAL = "manual"            # Introducido manualmente por el usuario
    AI_GENERATED = "ai_generated"  # Generado por IA (con fuente citada)
    PENDING = "pending"          # Pendiente de contenido


class ContentStatus(str, enum.Enum):
    """Estado del contenido de un tema"""
    EMPTY = "empty"          # Sin contenido
    PARTIAL = "partial"      # Contenido parcial
    COMPLETE = "complete"    # Contenido completo
    VERIFIED = "verified"    # Verificado por el usuario


class NormativeSourceType(str, enum.Enum):
    """Tipo de fuente normativa"""
    BOE = "boe"              # Boletín Oficial del Estado
    BOA = "boa"              # Boletín Oficial de Aragón
    CTE = "cte"              # Código Técnico de la Edificación
    CUSTOM = "custom"        # Otro tipo de normativa


class Syllabus(Base):
    """Temario oficial (ej: Anexo V Arquitectos Técnicos)"""
    __tablename__ = "syllabi"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Información básica
    name = Column(String, nullable=False)  # "Arquitectos Técnicos - Anexo V"
    description = Column(Text, nullable=True)
    source_file = Column(String, nullable=True)  # Ruta al PDF original

    # Metadatos de progreso
    total_topics = Column(Integer, default=0)
    processed_topics = Column(Integer, default=0)

    # Sharing
    is_public = Column(Boolean, default=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    user = relationship("User", back_populates="syllabi")
    topics = relationship("StructuredTopic", back_populates="syllabus", cascade="all, delete-orphan")


class StructuredTopic(Base):
    """Tema/subtema estructurado del temario"""
    __tablename__ = "structured_topics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    syllabus_id = Column(Integer, ForeignKey("syllabi.id"), nullable=False)

    # Jerarquía
    parent_id = Column(Integer, ForeignKey("structured_topics.id"), nullable=True)
    order_index = Column(Integer, default=0, nullable=False)  # Orden entre hermanos
    level = Column(Integer, default=0, nullable=False)  # 0=raíz, 1=parte, 2=tema, 3=subtema...

    # Contenido
    title = Column(String, nullable=False)
    code = Column(String, nullable=True)  # "1.2.3" o "Tema 1"
    content = Column(Text, nullable=True)  # Contenido procesado (markdown)

    # Fuente y trazabilidad
    source_type = Column(Enum(SourceType), default=SourceType.PENDING, nullable=False)
    source_reference = Column(String, nullable=True)  # Ruta al archivo o URL
    source_excerpt = Column(Text, nullable=True)  # Texto original extraído

    # Estado
    content_status = Column(Enum(ContentStatus), default=ContentStatus.EMPTY, nullable=False)
    last_processed_at = Column(DateTime(timezone=True), nullable=True)

    # UI state (persistido por usuario)
    is_expanded = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relaciones
    user = relationship("User", back_populates="structured_topics")
    syllabus = relationship("Syllabus", back_populates="topics")

    # Self-referential relationship para árbol
    children = relationship(
        "StructuredTopic",
        back_populates="parent",
        foreign_keys=[parent_id],
        cascade="all, delete-orphan"
    )
    parent = relationship(
        "StructuredTopic",
        back_populates="children",
        foreign_keys=[parent_id],
        remote_side=[id]
    )


class NormativeSource(Base):
    """Fuente normativa indexada para búsquedas"""
    __tablename__ = "normative_sources"

    id = Column(Integer, primary_key=True, index=True)

    # Identificación
    name = Column(String, nullable=False)  # "Constitución Española"
    code = Column(String, nullable=True, index=True)  # "BOE-A-1978-31229"
    source_type = Column(Enum(NormativeSourceType), default=NormativeSourceType.CUSTOM, nullable=False)

    # Ubicación
    file_path = Column(String, nullable=True)  # Ruta local al archivo
    url = Column(String, nullable=True)  # URL oficial

    # Contenido indexado
    full_text = Column(Text, nullable=True)  # Texto extraído del PDF
    is_indexed = Column(Boolean, default=False, index=True)
    indexed_at = Column(DateTime(timezone=True), nullable=True)

    # Metadatos
    file_size = Column(Integer, nullable=True)  # Tamaño en bytes
    page_count = Column(Integer, nullable=True)  # Número de páginas

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ProcessingLog(Base):
    """Log de procesamiento de contenido (trazabilidad)"""
    __tablename__ = "processing_logs"

    id = Column(Integer, primary_key=True, index=True)
    topic_id = Column(Integer, ForeignKey("structured_topics.id"), nullable=False)

    # Información del procesamiento
    action = Column(String, nullable=False)  # "search", "extract", "synthesize"
    agent_name = Column(String, nullable=True)  # "searcher", "synthesizer"
    status = Column(String, nullable=False)  # "started", "completed", "failed"

    # Detalles
    input_data = Column(Text, nullable=True)  # JSON con datos de entrada
    output_data = Column(Text, nullable=True)  # JSON con datos de salida
    error_message = Column(Text, nullable=True)

    # Fuentes consultadas
    sources_checked = Column(Text, nullable=True)  # JSON lista de fuentes consultadas
    source_found = Column(String, nullable=True)  # Fuente donde se encontró contenido

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relaciones
    topic = relationship("StructuredTopic")
