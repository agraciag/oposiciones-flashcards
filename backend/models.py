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
