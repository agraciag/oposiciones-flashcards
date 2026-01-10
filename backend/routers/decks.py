"""
Router para gestión de decks (mazos)
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from models import Deck, User, Flashcard
from auth_utils import get_current_user
from services.pdf_service import extract_text_from_pdf, generate_flashcards_from_text

router = APIRouter()


class DeckCreate(BaseModel):
    """Schema para crear deck"""
    name: str
    description: str | None = None
    is_public: bool = False


class DeckResponse(BaseModel):
    """Schema respuesta deck"""
    id: int
    user_id: int
    name: str
    description: str | None
    is_public: bool
    original_deck_id: int | None
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/", response_model=DeckResponse)
def create_deck(
    deck: DeckCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear nuevo deck"""
    db_deck = Deck(
        user_id=current_user.id,
        name=deck.name,
        description=deck.description,
        is_public=deck.is_public
    )
    db.add(db_deck)
    db.commit()
    db.refresh(db_deck)
    return db_deck


@router.get("/", response_model=List[DeckResponse])
def get_my_decks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener mis decks"""
    decks = db.query(Deck).filter(Deck.user_id == current_user.id).all()
    return decks


@router.get("/public", response_model=List[DeckResponse])
def get_public_decks(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener mercado de decks públicos (excluyendo los míos)"""
    decks = db.query(Deck).filter(
        Deck.is_public == True,
        Deck.user_id != current_user.id
    ).offset(skip).limit(limit).all()
    return decks


@router.get("/{deck_id}", response_model=DeckResponse)
def get_deck(
    deck_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener deck por ID (si es mío o es público)"""
    deck = db.query(Deck).filter(Deck.id == deck_id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck no encontrado")
    
    # Check access
    if deck.user_id != current_user.id and not deck.is_public:
         raise HTTPException(status_code=403, detail="No tienes acceso a este mazo")

    return deck


@router.put("/{deck_id}/toggle-public", response_model=DeckResponse)
def toggle_public(
    deck_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Hacer público/privado un mazo"""
    deck = db.query(Deck).filter(Deck.id == deck_id, Deck.user_id == current_user.id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck no encontrado o no eres el dueño")
    
    deck.is_public = not deck.is_public
    db.commit()
    db.refresh(deck)
    return deck


@router.post("/{deck_id}/clone", response_model=DeckResponse)
def clone_deck(
    deck_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Clonar un mazo público a mi librería"""
    original_deck = db.query(Deck).filter(Deck.id == deck_id).first()
    if not original_deck:
        raise HTTPException(status_code=404, detail="Deck original no encontrado")
        
    if not original_deck.is_public and original_deck.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Este mazo es privado")

    # 1. Create new Deck
    new_deck = Deck(
        user_id=current_user.id,
        name=f"{original_deck.name} (Copia)",
        description=original_deck.description,
        is_public=False, # Clones start as private
        original_deck_id=original_deck.id
    )
    db.add(new_deck)
    db.flush() # Get ID

    # 2. Clone Flashcards
    original_cards = db.query(Flashcard).filter(Flashcard.deck_id == original_deck.id).all()
    for card in original_cards:
        new_card = Flashcard(
            deck_id=new_deck.id,
            front=card.front,
            back=card.back,
            tags=card.tags,
            legal_reference=card.legal_reference,
            article_number=card.article_number,
            law_name=card.law_name,
            # Reset study progress
            repetitions=0,
            easiness_factor=2.5,
            interval_days=0,
            # next_review default is now()
        )
        db.add(new_card)

    db.commit()
    db.refresh(new_deck)
    return new_deck


@router.delete("/{deck_id}")
def delete_deck(
    deck_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar deck"""
    deck = db.query(Deck).filter(Deck.id == deck_id, Deck.user_id == current_user.id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck no encontrado o no eres el dueño")
    db.delete(deck)
    db.commit()
    return {"message": "Deck eliminado"}


@router.post("/import-pdf")
async def import_pdf_preview(
    file: UploadFile = File(...),
    deck_name: str = Form(...),
    description: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Importar PDF y generar preview de flashcards con IA
    NO guarda nada en la base de datos, solo retorna preview
    """
    # Validar tipo de archivo
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")

    # Validar tamaño (10MB máximo)
    file_bytes = await file.read()
    if len(file_bytes) > 10 * 1024 * 1024:  # 10MB
        raise HTTPException(status_code=400, detail="El archivo es demasiado grande (máximo 10MB)")

    # Extraer texto del PDF
    try:
        text = extract_text_from_pdf(file_bytes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not text.strip():
        raise HTTPException(status_code=400, detail="El PDF no contiene texto extraíble")

    # Generar flashcards con IA
    try:
        flashcards_data = await generate_flashcards_from_text(text, deck_name)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Error al generar flashcards: {str(e)}")

    # Retornar preview (NO guardar en DB todavía)
    return {
        "deck_name": deck_name,
        "description": description,
        "flashcards_preview": flashcards_data,
        "total_flashcards": len(flashcards_data),
        "extracted_text_length": len(text)
    }


class FlashcardImport(BaseModel):
    """Schema para flashcard en importación"""
    front: str
    back: str
    tags: str | None = None


class PDFImportConfirm(BaseModel):
    """Schema para confirmar importación de PDF"""
    deck_name: str
    description: str | None = None
    flashcards: List[FlashcardImport]


@router.post("/import-pdf/confirm", response_model=DeckResponse)
def confirm_pdf_import(
    data: PDFImportConfirm,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Guardar flashcards generadas por IA después de confirmación del usuario
    """
    if not data.flashcards:
        raise HTTPException(status_code=400, detail="No hay flashcards para guardar")

    # Crear deck
    deck = Deck(
        user_id=current_user.id,
        name=data.deck_name,
        description=data.description,
        is_public=False
    )
    db.add(deck)
    db.flush()  # Obtener ID del deck

    # Crear flashcards
    for card_data in data.flashcards:
        flashcard = Flashcard(
            deck_id=deck.id,
            front=card_data.front,
            back=card_data.back,
            tags=card_data.tags or ""
        )
        db.add(flashcard)

    db.commit()
    db.refresh(deck)
    return deck