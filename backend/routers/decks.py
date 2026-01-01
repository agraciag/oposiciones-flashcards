"""
Router para gestión de decks (mazos)
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from models import Deck

router = APIRouter()


class DeckCreate(BaseModel):
    """Schema para crear deck"""
    name: str
    description: str | None = None
    user_id: int = 1  # Por defecto user 1 para testing


class DeckResponse(BaseModel):
    """Schema respuesta deck"""
    id: int
    user_id: int
    name: str
    description: str | None
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=DeckResponse)
def create_deck(deck: DeckCreate, db: Session = Depends(get_db)):
    """Crear nuevo deck"""
    db_deck = Deck(**deck.model_dump())
    db.add(db_deck)
    db.commit()
    db.refresh(db_deck)
    return db_deck


@router.get("/", response_model=List[DeckResponse])
def get_decks(db: Session = Depends(get_db)):
    """Obtener todos los decks"""
    decks = db.query(Deck).all()
    return decks


@router.get("/{deck_id}", response_model=DeckResponse)
def get_deck(deck_id: int, db: Session = Depends(get_db)):
    """Obtener deck por ID"""
    deck = db.query(Deck).filter(Deck.id == deck_id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck no encontrado")
    return deck


@router.delete("/{deck_id}")
def delete_deck(deck_id: int, db: Session = Depends(get_db)):
    """Eliminar deck"""
    deck = db.query(Deck).filter(Deck.id == deck_id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck no encontrado")
    db.delete(deck)
    db.commit()
    return {"message": "Deck eliminado"}
