"""
Router para gestión de flashcards
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from models import Flashcard, Deck

router = APIRouter()


class FlashcardCreate(BaseModel):
    """Schema para crear flashcard"""
    deck_id: int
    front: str
    back: str
    tags: str | None = None
    legal_reference: str | None = None
    article_number: str | None = None
    law_name: str | None = None


class FlashcardResponse(BaseModel):
    """Schema respuesta flashcard"""
    id: int
    deck_id: int
    front: str
    back: str
    tags: str | None
    repetitions: int
    easiness_factor: float
    interval_days: int
    next_review: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=FlashcardResponse)
def create_flashcard(flashcard: FlashcardCreate, db: Session = Depends(get_db)):
    """Crear nueva flashcard"""
    # Verificar que el deck existe
    deck = db.query(Deck).filter(Deck.id == flashcard.deck_id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck no encontrado")
    # Crear flashcard
    db_flashcard = Flashcard(**flashcard.model_dump())
    db.add(db_flashcard)
    db.commit()
    db.refresh(db_flashcard)
    return db_flashcard
