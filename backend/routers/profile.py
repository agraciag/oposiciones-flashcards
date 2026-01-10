"""
Router para gestión de perfil de usuario
Permite actualizar email y contraseña con re-autenticación
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from database import get_db
from models import User
from auth_utils import get_current_user, get_password_hash, verify_password

router = APIRouter()


class EmailUpdate(BaseModel):
    new_email: EmailStr
    current_password: str


class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str
    confirm_new_password: str


@router.put("/email")
def update_email(
    data: EmailUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualizar email del usuario
    Requiere contraseña actual para verificación
    """
    # Verificar contraseña actual
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Contraseña incorrecta")

    # Verificar que el nuevo email no esté en uso
    existing_user = db.query(User).filter(User.email == data.new_email).first()
    if existing_user and existing_user.id != current_user.id:
        raise HTTPException(status_code=400, detail="Este email ya está en uso")

    # Actualizar email
    current_user.email = data.new_email
    db.commit()
    db.refresh(current_user)

    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email
    }


@router.put("/password")
def update_password(
    data: PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Actualizar contraseña del usuario
    Requiere contraseña actual y confirmación de nueva contraseña
    """
    # Verificar contraseña actual
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")

    # Verificar que las contraseñas nuevas coincidan
    if data.new_password != data.confirm_new_password:
        raise HTTPException(status_code=400, detail="Las contraseñas nuevas no coinciden")

    # Verificar que la nueva contraseña sea diferente
    if verify_password(data.new_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="La nueva contraseña debe ser diferente a la actual")

    # Validar longitud mínima de contraseña
    if len(data.new_password) < 6:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 6 caracteres")

    # Actualizar contraseña
    current_user.hashed_password = get_password_hash(data.new_password)
    db.commit()

    return {"message": "Contraseña actualizada correctamente"}
