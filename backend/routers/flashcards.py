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


class FlashcardUpdate(BaseModel):
    """Schema para actualizar flashcard"""
    front: str | None = None
    back: str | None = None
    tags: str | None = None
    legal_reference: str | None = None
    article_number: str | None = None
    law_name: str | None = None


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


@router.get("/", response_model=List[FlashcardResponse])
def get_flashcards(
    skip: int = 0, 
    limit: int = 100, 
    deck_id: int | None = None,
    db: Session = Depends(get_db)
):
    """Obtener todas las flashcards, opcionalmente filtradas por deck"""
    query = db.query(Flashcard)
    if deck_id:
        query = query.filter(Flashcard.deck_id == deck_id)
    return query.offset(skip).limit(limit).all()


@router.get("/{flashcard_id}", response_model=FlashcardResponse)
def get_flashcard(flashcard_id: int, db: Session = Depends(get_db)):
    """Obtener flashcard por ID"""
    flashcard = db.query(Flashcard).filter(Flashcard.id == flashcard_id).first()
    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard no encontrada")
    return flashcard


@router.put("/{flashcard_id}", response_model=FlashcardResponse)
def update_flashcard(
    flashcard_id: int, 
    flashcard_update: FlashcardUpdate, 
    db: Session = Depends(get_db)
):
    """Actualizar flashcard"""
    db_flashcard = db.query(Flashcard).filter(Flashcard.id == flashcard_id).first()
    if not db_flashcard:
        raise HTTPException(status_code=404, detail="Flashcard no encontrada")
    
    update_data = flashcard_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_flashcard, key, value)
    
    db.add(db_flashcard)
    db.commit()
    db.refresh(db_flashcard)
    return db_flashcard


@router.delete("/{flashcard_id}")
def delete_flashcard(flashcard_id: int, db: Session = Depends(get_db)):
    """Eliminar flashcard"""
    flashcard = db.query(Flashcard).filter(Flashcard.id == flashcard_id).first()
    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard no encontrada")
    
    db.delete(flashcard)
    db.commit()
    return {"message": "Flashcard eliminada"}
