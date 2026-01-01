"""
Router para sistema de estudio con SM-2
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from enum import Enum

from database import get_db
from models import Flashcard, StudySession, StudyLog
from sm2 import calculate_sm2

router = APIRouter()


def utc_now():
    """Helper para obtener datetime con timezone UTC"""
    return datetime.now(timezone.utc)


class StudyQuality(str, Enum):
    """Calidad de respuesta SM-2"""
    AGAIN = "again"  # 0 - No recordada
    HARD = "hard"    # 2 - Difícil
    GOOD = "good"    # 3 - Bien
    EASY = "easy"    # 4 - Fácil


class StudyRequest(BaseModel):
    """Request para estudiar flashcard"""
    flashcard_id: int
    quality: StudyQuality
    time_spent_seconds: int


class StudyResponse(BaseModel):
    """Response después de estudiar"""
    flashcard_id: int
    next_review: datetime
    interval_days: int
    repetitions: int
    easiness_factor: float

    class Config:
        from_attributes = True


class FlashcardStudy(BaseModel):
    """Flashcard para estudiar"""
    id: int
    front: str
    back: str
    article_number: str | None
    law_name: str | None
    repetitions: int
    interval_days: int

    class Config:
        from_attributes = True


@router.get("/next", response_model=FlashcardStudy | None)
def get_next_flashcard(deck_id: int | None = None, db: Session = Depends(get_db)):
    """Obtener siguiente flashcard para estudiar"""
    query = db.query(Flashcard).filter(Flashcard.next_review <= utc_now())

    if deck_id:
        query = query.filter(Flashcard.deck_id == deck_id)

    # Ordenar por fecha de revisión (las más atrasadas primero)
    flashcard = query.order_by(Flashcard.next_review.asc()).first()

    if not flashcard:
        return None

    return flashcard


@router.post("/review", response_model=StudyResponse)
def review_flashcard(review: StudyRequest, session_id: int | None = None, db: Session = Depends(get_db)):
    """Revisar flashcard con algoritmo SM-2"""
    flashcard = db.query(Flashcard).filter(Flashcard.id == review.flashcard_id).first()

    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard no encontrada")

    # Guardar valores antes del review
    rep_before = flashcard.repetitions
    ease_before = flashcard.easiness_factor
    interval_before = flashcard.interval_days

    # Mapear calidad a valor numérico SM-2
    quality_map = {
        StudyQuality.AGAIN: 0,
        StudyQuality.HARD: 2,
        StudyQuality.GOOD: 3,
        StudyQuality.EASY: 4
    }
    quality_value = quality_map[review.quality]

    # Calcular nuevos valores con SM-2
    result = calculate_sm2(
        quality=quality_value,
        repetitions=flashcard.repetitions,
        easiness=flashcard.easiness_factor,
        interval=flashcard.interval_days
    )

    # Actualizar flashcard
    flashcard.repetitions = result['repetitions']
    flashcard.easiness_factor = result['easiness']
    flashcard.interval_days = result['interval']
    flashcard.next_review = utc_now() + timedelta(days=result['interval'])

    # Crear o obtener sesión de estudio
    if not session_id:
        # Crear sesión temporal para testing
        study_session = StudySession(
            user_id=1,  # Usuario de prueba
            started_at=utc_now()
        )
        db.add(study_session)
        db.flush()  # Para obtener el ID sin hacer commit
        session_id = study_session.id

    # Crear log de estudio con valores antes/después
    study_log = StudyLog(
        session_id=session_id,
        flashcard_id=flashcard.id,
        quality=review.quality.value,
        time_spent_seconds=review.time_spent_seconds,
        repetitions_before=rep_before,
        easiness_before=ease_before,
        interval_before=interval_before,
        repetitions_after=result['repetitions'],
        easiness_after=result['easiness'],
        interval_after=result['interval'],
        next_review_after=flashcard.next_review,
        reviewed_at=utc_now()
    )
    db.add(study_log)

    db.commit()
    db.refresh(flashcard)

    return StudyResponse(
        flashcard_id=flashcard.id,
        next_review=flashcard.next_review,
        interval_days=flashcard.interval_days,
        repetitions=flashcard.repetitions,
        easiness_factor=flashcard.easiness_factor
    )


@router.get("/stats")
def get_study_stats(deck_id: int | None = None, db: Session = Depends(get_db)):
    """Obtener estadísticas de estudio"""
    query = db.query(Flashcard)

    if deck_id:
        query = query.filter(Flashcard.deck_id == deck_id)

    total_cards = query.count()
    cards_to_review = query.filter(Flashcard.next_review <= utc_now()).count()
    cards_learning = query.filter(Flashcard.repetitions < 3).count()
    cards_mastered = query.filter(Flashcard.repetitions >= 3).count()

    return {
        "total_cards": total_cards,
        "cards_to_review": cards_to_review,
        "cards_learning": cards_learning,
        "cards_mastered": cards_mastered
    }
