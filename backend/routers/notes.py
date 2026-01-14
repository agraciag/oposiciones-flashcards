"""
Router para gestión de notas y apuntes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from models import Note, NoteCollection, NoteHierarchy, User, NoteType, CollectionType
from auth_utils import get_current_user

router = APIRouter()


# ============================================================================
# SCHEMAS
# ============================================================================

class NoteCreate(BaseModel):
    """Schema para crear nota"""
    title: str
    content: Optional[str] = None
    note_type: NoteType = NoteType.CONTENT
    tags: Optional[str] = None
    legal_reference: Optional[str] = None
    article_number: Optional[str] = None


class NoteUpdate(BaseModel):
    """Schema para actualizar nota"""
    title: Optional[str] = None
    content: Optional[str] = None
    note_type: Optional[NoteType] = None
    tags: Optional[str] = None
    legal_reference: Optional[str] = None
    article_number: Optional[str] = None


class NoteResponse(BaseModel):
    """Schema respuesta nota"""
    id: int
    user_id: int
    title: str
    content: Optional[str]
    note_type: NoteType
    tags: Optional[str]
    legal_reference: Optional[str]
    article_number: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class NoteCollectionCreate(BaseModel):
    """Schema para crear colección"""
    name: str
    description: Optional[str] = None
    collection_type: CollectionType = CollectionType.CUSTOM
    is_public: bool = False


class NoteCollectionUpdate(BaseModel):
    """Schema para actualizar colección"""
    name: Optional[str] = None
    description: Optional[str] = None
    collection_type: Optional[CollectionType] = None
    is_public: Optional[bool] = None


class NoteCollectionResponse(BaseModel):
    """Schema respuesta colección"""
    id: int
    user_id: int
    name: str
    description: Optional[str]
    collection_type: CollectionType
    is_public: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class NoteHierarchyCreate(BaseModel):
    """Schema para crear jerarquía"""
    collection_id: int
    note_id: int
    parent_id: Optional[int] = None
    order_index: int = 0
    is_featured: bool = False


class NoteHierarchyUpdate(BaseModel):
    """Schema para actualizar jerarquía"""
    parent_id: Optional[int] = None
    order_index: Optional[int] = None
    is_featured: Optional[bool] = None


class NoteHierarchyResponse(BaseModel):
    """Schema respuesta jerarquía"""
    id: int
    collection_id: int
    note_id: int
    parent_id: Optional[int]
    order_index: int
    is_featured: bool
    created_at: datetime

    class Config:
        from_attributes = True


class NoteTreeNode(BaseModel):
    """Nodo del árbol de notas"""
    hierarchy_id: int
    note_id: int
    title: str
    note_type: NoteType
    is_featured: bool
    order_index: int
    children: List['NoteTreeNode'] = []

    class Config:
        from_attributes = True


# ============================================================================
# ENDPOINTS - NOTES
# ============================================================================

@router.post("/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(
    note: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear nueva nota"""
    db_note = Note(
        user_id=current_user.id,
        title=note.title,
        content=note.content,
        note_type=note.note_type,
        tags=note.tags,
        legal_reference=note.legal_reference,
        article_number=note.article_number
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


@router.get("/notes", response_model=List[NoteResponse])
def get_my_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    tags: Optional[str] = None,
    search: Optional[str] = None
):
    """Obtener mis notas con filtros opcionales"""
    query = db.query(Note).filter(Note.user_id == current_user.id)

    if tags:
        # Filtrar por tags (búsqueda simple)
        query = query.filter(Note.tags.contains(tags))

    if search:
        # Búsqueda en título y contenido
        search_pattern = f"%{search}%"
        query = query.filter(
            (Note.title.ilike(search_pattern)) |
            (Note.content.ilike(search_pattern)) |
            (Note.article_number.ilike(search_pattern))
        )

    notes = query.offset(skip).limit(limit).all()
    return notes


@router.get("/notes/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener nota por ID"""
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Nota no encontrada")

    if note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta nota")

    return note


@router.put("/notes/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: int,
    note_update: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar nota"""
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Nota no encontrada")

    if db_note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta nota")

    # Actualizar campos proporcionados
    update_data = note_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_note, field, value)

    db.commit()
    db.refresh(db_note)
    return db_note


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar nota"""
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Nota no encontrada")

    if db_note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta nota")

    db.delete(db_note)
    db.commit()
    return None


# ============================================================================
# ENDPOINTS - COLLECTIONS
# ============================================================================

@router.post("/collections", response_model=NoteCollectionResponse, status_code=status.HTTP_201_CREATED)
def create_collection(
    collection: NoteCollectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear nueva colección"""
    db_collection = NoteCollection(
        user_id=current_user.id,
        name=collection.name,
        description=collection.description,
        collection_type=collection.collection_type,
        is_public=collection.is_public
    )
    db.add(db_collection)
    db.commit()
    db.refresh(db_collection)
    return db_collection


@router.get("/collections", response_model=List[NoteCollectionResponse])
def get_my_collections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    collection_type: Optional[CollectionType] = None
):
    """Obtener mis colecciones con filtros opcionales"""
    query = db.query(NoteCollection).filter(NoteCollection.user_id == current_user.id)

    if collection_type:
        query = query.filter(NoteCollection.collection_type == collection_type)

    collections = query.all()
    return collections


@router.get("/collections/public", response_model=List[NoteCollectionResponse])
def get_public_collections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100
):
    """Obtener colecciones públicas (excluyendo las mías)"""
    collections = db.query(NoteCollection).filter(
        NoteCollection.is_public == True,
        NoteCollection.user_id != current_user.id
    ).offset(skip).limit(limit).all()
    return collections


@router.get("/collections/{collection_id}", response_model=NoteCollectionResponse)
def get_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener colección por ID"""
    collection = db.query(NoteCollection).filter(NoteCollection.id == collection_id).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Colección no encontrada")

    if collection.user_id != current_user.id and not collection.is_public:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta colección")

    return collection


@router.put("/collections/{collection_id}", response_model=NoteCollectionResponse)
def update_collection(
    collection_id: int,
    collection_update: NoteCollectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar colección"""
    db_collection = db.query(NoteCollection).filter(NoteCollection.id == collection_id).first()
    if not db_collection:
        raise HTTPException(status_code=404, detail="Colección no encontrada")

    if db_collection.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta colección")

    # Actualizar campos proporcionados
    update_data = collection_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_collection, field, value)

    db.commit()
    db.refresh(db_collection)
    return db_collection


@router.delete("/collections/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar colección"""
    db_collection = db.query(NoteCollection).filter(NoteCollection.id == collection_id).first()
    if not db_collection:
        raise HTTPException(status_code=404, detail="Colección no encontrada")

    if db_collection.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta colección")

    db.delete(db_collection)
    db.commit()
    return None


@router.post("/collections/{collection_id}/clone", response_model=NoteCollectionResponse, status_code=status.HTTP_201_CREATED)
def clone_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Clonar una colección pública"""
    # Verificar que la colección existe y es pública
    source_collection = db.query(NoteCollection).filter(NoteCollection.id == collection_id).first()
    if not source_collection:
        raise HTTPException(status_code=404, detail="Colección no encontrada")

    if not source_collection.is_public and source_collection.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No puedes clonar una colección privada")

    # Crear nueva colección
    new_collection = NoteCollection(
        user_id=current_user.id,
        name=f"{source_collection.name} (copia)",
        description=source_collection.description,
        collection_type=source_collection.collection_type,
        is_public=False  # Las copias son privadas por defecto
    )
    db.add(new_collection)
    db.commit()
    db.refresh(new_collection)

    # Obtener todas las notas de la colección original
    hierarchies = db.query(NoteHierarchy).filter(
        NoteHierarchy.collection_id == collection_id
    ).all()

    # Mapeo de IDs antiguos a nuevos para mantener las relaciones padre-hijo
    hierarchy_id_map = {}

    # Clonar notas y crear nuevas jerarquías
    for hierarchy in hierarchies:
        # Obtener la nota original
        original_note = db.query(Note).filter(Note.id == hierarchy.note_id).first()

        # Crear copia de la nota
        new_note = Note(
            user_id=current_user.id,
            title=original_note.title,
            content=original_note.content,
            note_type=original_note.note_type,
            tags=original_note.tags,
            legal_reference=original_note.legal_reference,
            article_number=original_note.article_number
        )
        db.add(new_note)
        db.commit()
        db.refresh(new_note)

        # Determinar el parent_id correcto usando el mapeo
        new_parent_id = None
        if hierarchy.parent_id:
            new_parent_id = hierarchy_id_map.get(hierarchy.parent_id)

        # Crear nueva jerarquía
        new_hierarchy = NoteHierarchy(
            collection_id=new_collection.id,
            note_id=new_note.id,
            parent_id=new_parent_id,
            order_index=hierarchy.order_index,
            is_featured=hierarchy.is_featured
        )
        db.add(new_hierarchy)
        db.commit()
        db.refresh(new_hierarchy)

        # Guardar el mapeo de IDs
        hierarchy_id_map[hierarchy.id] = new_hierarchy.id

    return new_collection


# ============================================================================
# ENDPOINTS - HIERARCHIES
# ============================================================================

@router.post("/hierarchies", response_model=NoteHierarchyResponse, status_code=status.HTTP_201_CREATED)
def create_hierarchy(
    hierarchy: NoteHierarchyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Añadir nota a colección (crear jerarquía)"""
    # Verificar que la colección existe y es del usuario
    collection = db.query(NoteCollection).filter(NoteCollection.id == hierarchy.collection_id).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Colección no encontrada")
    if collection.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta colección")

    # Verificar que la nota existe y es del usuario
    note = db.query(Note).filter(Note.id == hierarchy.note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Nota no encontrada")
    if note.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta nota")

    # Verificar parent_id si se proporciona
    if hierarchy.parent_id:
        parent = db.query(NoteHierarchy).filter(NoteHierarchy.id == hierarchy.parent_id).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Jerarquía padre no encontrada")
        if parent.collection_id != hierarchy.collection_id:
            raise HTTPException(status_code=400, detail="El padre debe estar en la misma colección")

    db_hierarchy = NoteHierarchy(
        collection_id=hierarchy.collection_id,
        note_id=hierarchy.note_id,
        parent_id=hierarchy.parent_id,
        order_index=hierarchy.order_index,
        is_featured=hierarchy.is_featured
    )
    db.add(db_hierarchy)
    db.commit()
    db.refresh(db_hierarchy)
    return db_hierarchy


@router.get("/hierarchies/{hierarchy_id}", response_model=NoteHierarchyResponse)
def get_hierarchy(
    hierarchy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener jerarquía por ID"""
    hierarchy = db.query(NoteHierarchy).filter(NoteHierarchy.id == hierarchy_id).first()
    if not hierarchy:
        raise HTTPException(status_code=404, detail="Jerarquía no encontrada")

    # Verificar acceso a través de la colección
    collection = db.query(NoteCollection).filter(NoteCollection.id == hierarchy.collection_id).first()
    if collection.user_id != current_user.id and not collection.is_public:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta jerarquía")

    return hierarchy


@router.put("/hierarchies/{hierarchy_id}", response_model=NoteHierarchyResponse)
def update_hierarchy(
    hierarchy_id: int,
    hierarchy_update: NoteHierarchyUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar jerarquía (mover nodo, cambiar orden, etc.)"""
    db_hierarchy = db.query(NoteHierarchy).filter(NoteHierarchy.id == hierarchy_id).first()
    if not db_hierarchy:
        raise HTTPException(status_code=404, detail="Jerarquía no encontrada")

    # Verificar acceso
    collection = db.query(NoteCollection).filter(NoteCollection.id == db_hierarchy.collection_id).first()
    if collection.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta jerarquía")

    # Actualizar campos proporcionados
    update_data = hierarchy_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_hierarchy, field, value)

    db.commit()
    db.refresh(db_hierarchy)
    return db_hierarchy


@router.delete("/hierarchies/{hierarchy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hierarchy(
    hierarchy_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar jerarquía (quitar nota de colección)"""
    db_hierarchy = db.query(NoteHierarchy).filter(NoteHierarchy.id == hierarchy_id).first()
    if not db_hierarchy:
        raise HTTPException(status_code=404, detail="Jerarquía no encontrada")

    # Verificar acceso
    collection = db.query(NoteCollection).filter(NoteCollection.id == db_hierarchy.collection_id).first()
    if collection.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta jerarquía")

    db.delete(db_hierarchy)
    db.commit()
    return None


# ============================================================================
# ENDPOINTS - TREE VIEW
# ============================================================================

def build_tree_recursive(hierarchies_dict, parent_id=None):
    """Construir árbol de notas recursivamente"""
    nodes = []
    children = hierarchies_dict.get(parent_id, [])

    for hierarchy in sorted(children, key=lambda x: x['order_index']):
        node = NoteTreeNode(
            hierarchy_id=hierarchy['hierarchy_id'],
            note_id=hierarchy['note_id'],
            title=hierarchy['title'],
            note_type=hierarchy['note_type'],
            is_featured=hierarchy['is_featured'],
            order_index=hierarchy['order_index'],
            children=build_tree_recursive(hierarchies_dict, hierarchy['hierarchy_id'])
        )
        nodes.append(node)

    return nodes


@router.get("/collections/{collection_id}/tree", response_model=List[NoteTreeNode])
def get_collection_tree(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener árbol completo de notas de una colección"""
    # Verificar acceso a la colección
    collection = db.query(NoteCollection).filter(NoteCollection.id == collection_id).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Colección no encontrada")

    if collection.user_id != current_user.id and not collection.is_public:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta colección")

    # Obtener todas las jerarquías con sus notas
    hierarchies = db.query(NoteHierarchy, Note).join(
        Note, NoteHierarchy.note_id == Note.id
    ).filter(
        NoteHierarchy.collection_id == collection_id
    ).all()

    # Organizar por parent_id
    hierarchies_dict = {}
    for hierarchy, note in hierarchies:
        parent_id = hierarchy.parent_id
        if parent_id not in hierarchies_dict:
            hierarchies_dict[parent_id] = []

        hierarchies_dict[parent_id].append({
            'hierarchy_id': hierarchy.id,
            'note_id': note.id,
            'title': note.title,
            'note_type': note.note_type,
            'is_featured': hierarchy.is_featured,
            'order_index': hierarchy.order_index
        })

    # Construir árbol desde la raíz (parent_id = None)
    tree = build_tree_recursive(hierarchies_dict, parent_id=None)
    return tree


@router.get("/collections/{collection_id}/export")
def export_collection_markdown(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Exportar colección a formato Markdown"""
    from fastapi.responses import PlainTextResponse

    # Verificar acceso a la colección
    collection = db.query(NoteCollection).filter(NoteCollection.id == collection_id).first()
    if not collection:
        raise HTTPException(status_code=404, detail="Colección no encontrada")

    if collection.user_id != current_user.id and not collection.is_public:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta colección")

    # Obtener todas las jerarquías con sus notas
    hierarchies = db.query(NoteHierarchy, Note).join(
        Note, NoteHierarchy.note_id == Note.id
    ).filter(
        NoteHierarchy.collection_id == collection_id
    ).order_by(NoteHierarchy.order_index).all()

    # Construir markdown
    markdown_lines = [
        f"# {collection.name}",
        "",
    ]

    if collection.description:
        markdown_lines.extend([
            collection.description,
            "",
        ])

    markdown_lines.extend([
        "---",
        "",
    ])

    # Función para construir el markdown recursivamente
    def build_markdown(parent_id=None, level=0):
        for hierarchy, note in hierarchies:
            if hierarchy.parent_id == parent_id:
                prefix = "#" * min(level + 2, 6)

                # Añadir título con nivel apropiado
                markdown_lines.append(f"{prefix} {note.title}")

                # Añadir metadatos si existen
                if note.article_number or note.legal_reference:
                    markdown_lines.append("")
                    if note.article_number:
                        markdown_lines.append(f"**Artículo**: {note.article_number}")
                    if note.legal_reference:
                        markdown_lines.append(f"**Referencia**: {note.legal_reference}")

                # Añadir contenido si existe
                if note.content:
                    markdown_lines.extend(["", note.content])

                # Destacar si es featured
                if hierarchy.is_featured:
                    markdown_lines.append("")
                    markdown_lines.append("> ⭐ **Importante para examen**")

                markdown_lines.extend(["", "---", ""])

                # Recursión para hijos
                build_markdown(hierarchy.id, level + 1)

    build_markdown()

    # Unir todas las líneas
    markdown_content = "\n".join(markdown_lines)

    return PlainTextResponse(
        content=markdown_content,
        media_type="text/markdown",
        headers={
            "Content-Disposition": f'attachment; filename="{collection.name}.md"'
        }
    )
