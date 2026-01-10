"""
Router para gestión de flashcards
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, Field
from datetime import datetime

from database import get_db
from models import Flashcard, Deck, User
from auth_utils import get_current_user
from services.ai_card_generator import generate_cards_from_text

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
def create_flashcard(
    flashcard: FlashcardCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear nueva flashcard"""
    # Verificar que el deck existe y pertenece al usuario
    deck = db.query(Deck).filter(Deck.id == flashcard.deck_id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck no encontrado")
    
    if deck.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No puedes añadir tarjetas a un mazo que no es tuyo")

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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener flashcards. Si deck_id, comprueba acceso al deck. Si no, devuelve las del usuario."""
    if deck_id:
        # Check deck access
        deck = db.query(Deck).filter(Deck.id == deck_id).first()
        if not deck:
             return [] # Or 404
        
        # Access control: Owner OR Public
        if deck.user_id != current_user.id and not deck.is_public:
             raise HTTPException(status_code=403, detail="No tienes acceso a este mazo")
        
        return db.query(Flashcard).filter(Flashcard.deck_id == deck_id).offset(skip).limit(limit).all()
    else:
        # Return all cards owned by user (via decks)
        return db.query(Flashcard).join(Deck).filter(Deck.user_id == current_user.id).offset(skip).limit(limit).all()


@router.get("/{flashcard_id}", response_model=FlashcardResponse)
def get_flashcard(
    flashcard_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener flashcard por ID"""
    flashcard = db.query(Flashcard).filter(Flashcard.id == flashcard_id).first()
    if not flashcard:
        raise HTTPException(status_code=404, detail="Flashcard no encontrada")
    
    # Check access (Owner OR Public Deck)
    # Lazy loading deck might trigger query, safer to join or get
    deck = db.query(Deck).filter(Deck.id == flashcard.deck_id).first()
    if deck.user_id != current_user.id and not deck.is_public:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta tarjeta")

    return flashcard


@router.put("/{flashcard_id}", response_model=FlashcardResponse)
def update_flashcard(
    flashcard_id: int, 
    flashcard_update: FlashcardUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar flashcard"""
    # Join with Deck to check ownership in one query
    result = db.query(Flashcard, Deck).join(Deck).filter(Flashcard.id == flashcard_id).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Flashcard no encontrada")
    
    db_flashcard, deck = result

    if deck.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No puedes editar esta tarjeta")
    
    update_data = flashcard_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_flashcard, key, value)
    
    db.add(db_flashcard)
    db.commit()
    db.refresh(db_flashcard)
    return db_flashcard


@router.delete("/{flashcard_id}")
def delete_flashcard(
    flashcard_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar flashcard"""
    result = db.query(Flashcard, Deck).join(Deck).filter(Flashcard.id == flashcard_id).first()

    if not result:
        raise HTTPException(status_code=404, detail="Flashcard no encontrada")

    flashcard, deck = result

    if deck.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No puedes eliminar esta tarjeta")

    db.delete(flashcard)
    db.commit()
    return {"message": "Flashcard eliminada"}


class TextGenerationRequest(BaseModel):
    """Schema para generar flashcards desde texto"""
    text: str = Field(..., min_length=10, max_length=15000)
    deck_context: str = Field(default="", max_length=200)
    max_cards: int = Field(default=10, ge=1, le=20)


class GeneratedFlashcard(BaseModel):
    """Schema para flashcard generada (preview)"""
    front: str
    back: str
    tags: str | None = None
    article_number: str | None = None
    law_name: str | None = None


@router.post("/generate-from-text", response_model=List[GeneratedFlashcard])
async def generate_flashcards_from_text(
    data: TextGenerationRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generar flashcards desde texto usando IA.
    Retorna preview de las flashcards generadas (NO las guarda en DB).
    """
    try:
        # Generar flashcards con IA
        generated_cards = await generate_cards_from_text(
            text=data.text,
            context=data.deck_context,
            max_cards=data.max_cards
        )

        return generated_cards

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar flashcards: {str(e)}"
        )