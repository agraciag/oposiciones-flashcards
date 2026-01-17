"""
Router para documentos de estudio interactivos
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
import markdown
import re

from database import get_db
from models import StudyDocument, StudyAnnotation, User
from auth_utils import get_current_user

router = APIRouter()


# ============================================================================
# SCHEMAS
# ============================================================================

class AnnotationCreate(BaseModel):
    """Schema para crear anotación"""
    start_pos: int
    end_pos: int
    selected_text: str
    annotation_title: Optional[str] = None
    linked_content: str
    legal_reference: Optional[str] = None
    article_number: Optional[str] = None


class AnnotationUpdate(BaseModel):
    """Schema para actualizar anotación"""
    annotation_title: Optional[str] = None
    linked_content: Optional[str] = None
    legal_reference: Optional[str] = None
    article_number: Optional[str] = None


class AnnotationResponse(BaseModel):
    """Schema respuesta anotación"""
    id: int
    document_id: int
    start_pos: int
    end_pos: int
    selected_text: str
    annotation_title: Optional[str]
    linked_content: str
    legal_reference: Optional[str]
    article_number: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class DocumentCreate(BaseModel):
    """Schema para crear documento"""
    title: str
    content: str
    description: Optional[str] = None
    is_public: bool = False


class DocumentUpdate(BaseModel):
    """Schema para actualizar documento"""
    title: Optional[str] = None
    content: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None


class DocumentResponse(BaseModel):
    """Schema respuesta documento"""
    id: int
    user_id: int
    title: str
    content: str
    description: Optional[str]
    is_public: bool
    created_at: datetime
    updated_at: Optional[datetime]
    annotations: List[AnnotationResponse] = []

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Schema respuesta lista de documentos (sin contenido completo)"""
    id: int
    user_id: int
    title: str
    description: Optional[str]
    is_public: bool
    created_at: datetime
    updated_at: Optional[datetime]
    annotation_count: int = 0

    class Config:
        from_attributes = True


# ============================================================================
# ENDPOINTS - DOCUMENTS
# ============================================================================

@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear nuevo documento de estudio"""
    db_document = StudyDocument(
        user_id=current_user.id,
        title=document.title,
        content=document.content,
        description=document.description,
        is_public=document.is_public
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


@router.get("/documents", response_model=List[DocumentListResponse])
def get_my_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener mis documentos de estudio"""
    documents = db.query(StudyDocument).filter(
        StudyDocument.user_id == current_user.id
    ).all()

    result = []
    for doc in documents:
        result.append(DocumentListResponse(
            id=doc.id,
            user_id=doc.user_id,
            title=doc.title,
            description=doc.description,
            is_public=doc.is_public,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
            annotation_count=len(doc.annotations)
        ))
    return result


@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Obtener documento por ID"""
    document = db.query(StudyDocument).filter(StudyDocument.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    if document.user_id != current_user.id and not document.is_public:
        raise HTTPException(status_code=403, detail="No tienes acceso a este documento")

    return document


@router.put("/documents/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: int,
    document_update: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar documento"""
    db_document = db.query(StudyDocument).filter(StudyDocument.id == document_id).first()
    if not db_document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    if db_document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este documento")

    update_data = document_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_document, field, value)

    db.commit()
    db.refresh(db_document)
    return db_document


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar documento"""
    db_document = db.query(StudyDocument).filter(StudyDocument.id == document_id).first()
    if not db_document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    if db_document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este documento")

    db.delete(db_document)
    db.commit()
    return None


# ============================================================================
# ENDPOINTS - ANNOTATIONS
# ============================================================================

@router.post("/documents/{document_id}/annotations", response_model=AnnotationResponse, status_code=status.HTTP_201_CREATED)
def create_annotation(
    document_id: int,
    annotation: AnnotationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Crear nueva anotación en un documento"""
    # Verificar acceso al documento
    document = db.query(StudyDocument).filter(StudyDocument.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")
    if document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este documento")

    # Verificar que las posiciones son válidas
    if annotation.start_pos < 0 or annotation.end_pos > len(document.content):
        raise HTTPException(status_code=400, detail="Posiciones inválidas")
    if annotation.start_pos >= annotation.end_pos:
        raise HTTPException(status_code=400, detail="start_pos debe ser menor que end_pos")

    # Verificar que el texto seleccionado coincide
    actual_text = document.content[annotation.start_pos:annotation.end_pos]
    if actual_text != annotation.selected_text:
        raise HTTPException(
            status_code=400,
            detail=f"El texto seleccionado no coincide. Esperado: '{actual_text}'"
        )

    db_annotation = StudyAnnotation(
        document_id=document_id,
        start_pos=annotation.start_pos,
        end_pos=annotation.end_pos,
        selected_text=annotation.selected_text,
        annotation_title=annotation.annotation_title,
        linked_content=annotation.linked_content,
        legal_reference=annotation.legal_reference,
        article_number=annotation.article_number
    )
    db.add(db_annotation)
    db.commit()
    db.refresh(db_annotation)
    return db_annotation


@router.put("/annotations/{annotation_id}", response_model=AnnotationResponse)
def update_annotation(
    annotation_id: int,
    annotation_update: AnnotationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Actualizar anotación"""
    db_annotation = db.query(StudyAnnotation).filter(StudyAnnotation.id == annotation_id).first()
    if not db_annotation:
        raise HTTPException(status_code=404, detail="Anotación no encontrada")

    # Verificar acceso a través del documento
    document = db.query(StudyDocument).filter(StudyDocument.id == db_annotation.document_id).first()
    if document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta anotación")

    update_data = annotation_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_annotation, field, value)

    db.commit()
    db.refresh(db_annotation)
    return db_annotation


@router.delete("/annotations/{annotation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_annotation(
    annotation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Eliminar anotación"""
    db_annotation = db.query(StudyAnnotation).filter(StudyAnnotation.id == annotation_id).first()
    if not db_annotation:
        raise HTTPException(status_code=404, detail="Anotación no encontrada")

    # Verificar acceso
    document = db.query(StudyDocument).filter(StudyDocument.id == db_annotation.document_id).first()
    if document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a esta anotación")

    db.delete(db_annotation)
    db.commit()
    return None


# ============================================================================
# ENDPOINTS - EXPORT
# ============================================================================

def build_interactive_html(document: StudyDocument, annotations: list) -> str:
    """Construir HTML interactivo con details/summary"""
    # Ordenar anotaciones por posición (de mayor a menor para insertar sin desplazar)
    sorted_annotations = sorted(annotations, key=lambda a: a.start_pos, reverse=True)

    content = document.content

    # Insertar las anotaciones como details/summary
    for ann in sorted_annotations:
        # Convertir contenido markdown a HTML
        html_content = markdown.markdown(ann.linked_content, extensions=['tables', 'fenced_code'])

        # Crear el elemento details
        title = ann.annotation_title or ann.selected_text
        details_html = f'''<details class="annotation" id="ann-{ann.id}">
<summary class="annotation-trigger">{ann.selected_text}</summary>
<div class="annotation-content">
<h4>{title}</h4>
{f'<p class="legal-ref"><strong>Ref:</strong> {ann.article_number}</p>' if ann.article_number else ''}
{html_content}
</div>
</details>'''

        # Reemplazar el texto original con el details
        content = content[:ann.start_pos] + details_html + content[ann.end_pos:]

    # Construir tabla de contenidos
    toc_items = []
    for ann in sorted(annotations, key=lambda a: a.start_pos):
        title = ann.annotation_title or ann.selected_text
        toc_items.append(f'<li><a href="#ann-{ann.id}">{title}</a></li>')

    toc_html = f'''<nav class="toc">
<h2>Tabla de Contenidos</h2>
<ol>
{''.join(toc_items)}
</ol>
</nav>''' if toc_items else ''

    # HTML completo
    html = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{document.title}</title>
    <style>
        :root {{
            --primary-color: #2563eb;
            --bg-color: #ffffff;
            --text-color: #1f2937;
            --border-color: #e5e7eb;
            --highlight-bg: #dbeafe;
        }}

        @media (prefers-color-scheme: dark) {{
            :root {{
                --bg-color: #1f2937;
                --text-color: #f3f4f6;
                --border-color: #374151;
                --highlight-bg: #1e3a5f;
            }}
        }}

        * {{
            box-sizing: border-box;
        }}

        body {{
            font-family: Georgia, 'Times New Roman', serif;
            line-height: 1.8;
            max-width: 800px;
            margin: 0 auto;
            padding: 2rem;
            background: var(--bg-color);
            color: var(--text-color);
        }}

        h1 {{
            border-bottom: 2px solid var(--primary-color);
            padding-bottom: 0.5rem;
        }}

        .toc {{
            background: var(--highlight-bg);
            padding: 1.5rem;
            border-radius: 8px;
            margin-bottom: 2rem;
        }}

        .toc h2 {{
            margin-top: 0;
            font-size: 1.2rem;
        }}

        .toc ol {{
            margin-bottom: 0;
            padding-left: 1.5rem;
        }}

        .toc a {{
            color: var(--primary-color);
            text-decoration: none;
        }}

        .toc a:hover {{
            text-decoration: underline;
        }}

        .content {{
            white-space: pre-wrap;
        }}

        .annotation {{
            display: inline;
        }}

        .annotation-trigger {{
            display: inline;
            color: var(--primary-color);
            cursor: pointer;
            border-bottom: 2px dotted var(--primary-color);
            font-weight: 500;
        }}

        .annotation-trigger:hover {{
            background: var(--highlight-bg);
        }}

        .annotation-content {{
            display: block;
            background: var(--highlight-bg);
            border-left: 4px solid var(--primary-color);
            padding: 1rem 1.5rem;
            margin: 1rem 0;
            border-radius: 0 8px 8px 0;
        }}

        .annotation-content h4 {{
            margin-top: 0;
            color: var(--primary-color);
        }}

        .legal-ref {{
            font-size: 0.9rem;
            color: #6b7280;
            font-style: italic;
        }}

        details[open] > .annotation-trigger {{
            background: var(--highlight-bg);
        }}

        /* Estilos para tablas dentro del contenido */
        table {{
            border-collapse: collapse;
            width: 100%;
            margin: 1rem 0;
        }}

        th, td {{
            border: 1px solid var(--border-color);
            padding: 0.5rem;
            text-align: left;
        }}

        th {{
            background: var(--highlight-bg);
        }}

        code {{
            background: var(--border-color);
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-size: 0.9em;
        }}

        pre {{
            background: var(--border-color);
            padding: 1rem;
            border-radius: 8px;
            overflow-x: auto;
        }}

        pre code {{
            background: none;
            padding: 0;
        }}

        @media print {{
            .annotation-content {{
                display: block !important;
            }}
        }}
    </style>
</head>
<body>
    <h1>{document.title}</h1>
    {f'<p class="description"><em>{document.description}</em></p>' if document.description else ''}

    {toc_html}

    <div class="content">
{content}
    </div>

    <footer style="margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--border-color); font-size: 0.9rem; color: #6b7280;">
        <p>Generado desde Oposiciones Flashcards</p>
    </footer>
</body>
</html>'''

    return html


@router.get("/documents/{document_id}/export/html")
def export_document_html(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Exportar documento como HTML interactivo"""
    document = db.query(StudyDocument).filter(StudyDocument.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    if document.user_id != current_user.id and not document.is_public:
        raise HTTPException(status_code=403, detail="No tienes acceso a este documento")

    html_content = build_interactive_html(document, document.annotations)

    return Response(
        content=html_content,
        media_type="text/html",
        headers={
            "Content-Disposition": f'attachment; filename="{document.title}.html"'
        }
    )


@router.get("/documents/{document_id}/export/pdf")
def export_document_pdf(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Exportar documento como PDF con TOC"""
    document = db.query(StudyDocument).filter(StudyDocument.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Documento no encontrado")

    if document.user_id != current_user.id and not document.is_public:
        raise HTTPException(status_code=403, detail="No tienes acceso a este documento")

    try:
        from weasyprint import HTML, CSS

        html_content = build_interactive_html(document, document.annotations)

        # CSS adicional para PDF
        pdf_css = CSS(string='''
            @page {
                size: A4;
                margin: 2cm;
                @bottom-center {
                    content: counter(page) " / " counter(pages);
                }
            }

            details {
                display: block !important;
            }

            .annotation-content {
                display: block !important;
                page-break-inside: avoid;
            }

            h1, h2, h3, h4 {
                page-break-after: avoid;
            }
        ''')

        pdf_bytes = HTML(string=html_content).write_pdf(stylesheets=[pdf_css])

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{document.title}.pdf"'
            }
        )
    except ImportError:
        raise HTTPException(
            status_code=501,
            detail="Exportación PDF no disponible. Instalar: pip install weasyprint"
        )
