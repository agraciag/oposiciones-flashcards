"""
Servicio de indexación de PDFs para fuentes normativas
"""

import os
import re
from datetime import datetime
from typing import List, Optional, Tuple
from pathlib import Path

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

from sqlalchemy.orm import Session
from models import NormativeSource, NormativeSourceType


class PDFIndexerService:
    """Servicio para extraer e indexar texto de PDFs"""

    def __init__(self, db: Session):
        self.db = db

    def extract_text_from_pdf(self, file_path: str) -> Tuple[str, int]:
        """
        Extrae texto de un PDF.
        Returns: (texto_completo, número_de_páginas)
        """
        if not PYMUPDF_AVAILABLE:
            raise ImportError("PyMuPDF no está instalado. Ejecuta: pip install pymupdf")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

        doc = fitz.open(file_path)
        text_parts = []

        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text()
            if text.strip():
                text_parts.append(f"--- Página {page_num + 1} ---\n{text}")

        full_text = "\n\n".join(text_parts)
        num_pages = len(doc)
        doc.close()
        return full_text, num_pages

    def detect_source_type(self, file_path: str, name: str) -> NormativeSourceType:
        """Detecta el tipo de fuente basándose en el nombre/ruta"""
        path_lower = file_path.lower()
        name_lower = name.lower()

        if "boe" in path_lower or "boe" in name_lower:
            return NormativeSourceType.BOE
        elif "boa" in path_lower or "boa" in name_lower:
            return NormativeSourceType.BOA
        elif "cte" in path_lower or "db-" in path_lower or "db" in name_lower:
            return NormativeSourceType.CTE
        else:
            return NormativeSourceType.CUSTOM

    def extract_boe_code(self, file_path: str) -> Optional[str]:
        """Extrae código BOE del nombre del archivo si existe"""
        filename = os.path.basename(file_path)
        # Patrón: BOE-A-YYYY-NNNNN
        match = re.search(r'BOE-[A-Z]-\d{4}-\d+', filename, re.IGNORECASE)
        if match:
            return match.group(0).upper()
        return None

    def index_pdf(self, file_path: str, name: Optional[str] = None) -> NormativeSource:
        """
        Indexa un PDF: extrae texto y lo guarda en la BD.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

        # Usar nombre del archivo si no se proporciona
        if not name:
            name = Path(file_path).stem

        # Verificar si ya existe
        existing = self.db.query(NormativeSource).filter(
            NormativeSource.file_path == file_path
        ).first()

        if existing:
            # Actualizar
            source = existing
        else:
            # Crear nuevo
            source = NormativeSource(
                name=name,
                file_path=file_path
            )
            self.db.add(source)

        # Detectar tipo y código
        source.source_type = self.detect_source_type(file_path, name)
        source.code = self.extract_boe_code(file_path) or source.code

        # Extraer texto
        try:
            full_text, page_count = self.extract_text_from_pdf(file_path)
            source.full_text = full_text
            source.page_count = page_count
            source.file_size = os.path.getsize(file_path)
            source.is_indexed = True
            source.indexed_at = datetime.utcnow()
        except Exception as e:
            source.is_indexed = False
            source.full_text = f"Error al extraer texto: {str(e)}"

        self.db.commit()
        self.db.refresh(source)
        return source

    def index_directory(
        self,
        directory: str,
        recursive: bool = True
    ) -> List[NormativeSource]:
        """
        Indexa todos los PDFs de un directorio.
        """
        indexed = []
        path = Path(directory)

        if not path.exists():
            raise FileNotFoundError(f"Directorio no encontrado: {directory}")

        pattern = "**/*.pdf" if recursive else "*.pdf"

        for pdf_path in path.glob(pattern):
            try:
                source = self.index_pdf(str(pdf_path))
                indexed.append(source)
                print(f"✓ Indexado: {pdf_path.name}")
            except Exception as e:
                print(f"✗ Error indexando {pdf_path.name}: {e}")

        return indexed

    def search_in_sources(
        self,
        query: str,
        source_type: Optional[NormativeSourceType] = None,
        limit: int = 10
    ) -> List[dict]:
        """
        Busca texto en las fuentes indexadas.
        Retorna fragmentos relevantes.
        """
        # Obtener fuentes indexadas
        sources_query = self.db.query(NormativeSource).filter(
            NormativeSource.is_indexed == True,
            NormativeSource.full_text.isnot(None)
        )

        if source_type:
            sources_query = sources_query.filter(NormativeSource.source_type == source_type)

        sources = sources_query.all()
        results = []

        # Preparar términos de búsqueda (case insensitive)
        query_terms = query.lower().split()

        for source in sources:
            if not source.full_text:
                continue

            text_lower = source.full_text.lower()

            # Verificar si contiene todos los términos
            if not all(term in text_lower for term in query_terms):
                continue

            # Encontrar contexto alrededor de la primera coincidencia
            excerpt = self._extract_context(source.full_text, query, context_chars=500)

            if excerpt:
                results.append({
                    "source_id": source.id,
                    "source_name": source.name,
                    "source_code": source.code,
                    "source_type": source.source_type.value,
                    "file_path": source.file_path,
                    "excerpt": excerpt,
                    "relevance_score": self._calculate_relevance(source.full_text, query_terms)
                })

        # Ordenar por relevancia
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:limit]

    def _extract_context(self, text: str, query: str, context_chars: int = 500) -> Optional[str]:
        """Extrae contexto alrededor de la primera coincidencia"""
        query_lower = query.lower()
        text_lower = text.lower()

        # Buscar primera coincidencia
        pos = text_lower.find(query_lower)
        if pos == -1:
            # Buscar primera palabra del query
            first_word = query_lower.split()[0]
            pos = text_lower.find(first_word)

        if pos == -1:
            return None

        # Extraer contexto
        start = max(0, pos - context_chars // 2)
        end = min(len(text), pos + len(query) + context_chars // 2)

        excerpt = text[start:end]

        # Limpiar inicio y fin (no cortar palabras)
        if start > 0:
            first_space = excerpt.find(' ')
            if first_space > 0:
                excerpt = "..." + excerpt[first_space + 1:]

        if end < len(text):
            last_space = excerpt.rfind(' ')
            if last_space > 0:
                excerpt = excerpt[:last_space] + "..."

        return excerpt.strip()

    def _calculate_relevance(self, text: str, query_terms: List[str]) -> float:
        """Calcula un score de relevancia básico"""
        text_lower = text.lower()
        score = 0.0

        for term in query_terms:
            # Contar ocurrencias
            count = text_lower.count(term)
            # Más ocurrencias = más relevante, pero con diminishing returns
            score += min(count, 10) * 0.1

        return score

    def get_indexing_stats(self) -> dict:
        """Obtiene estadísticas de indexación"""
        total = self.db.query(NormativeSource).count()
        indexed = self.db.query(NormativeSource).filter(
            NormativeSource.is_indexed == True
        ).count()

        by_type = {}
        for source_type in NormativeSourceType:
            count = self.db.query(NormativeSource).filter(
                NormativeSource.source_type == source_type
            ).count()
            by_type[source_type.value] = count

        return {
            "total_sources": total,
            "indexed_sources": indexed,
            "pending_sources": total - indexed,
            "by_type": by_type
        }


# ============================================================================
# Funciones de utilidad para uso directo
# ============================================================================

def index_normativa_folder(db: Session, base_path: str = None) -> List[NormativeSource]:
    """
    Indexa la carpeta de normativa del proyecto.
    """
    if base_path is None:
        # Ruta por defecto relativa al proyecto
        project_root = Path(__file__).parent.parent.parent
        base_path = project_root / "Material de Estudio" / "normativa"

    indexer = PDFIndexerService(db)
    return indexer.index_directory(str(base_path), recursive=True)


def search_normativa(db: Session, query: str, limit: int = 5) -> List[dict]:
    """
    Busca en la normativa indexada.
    """
    indexer = PDFIndexerService(db)
    return indexer.search_in_sources(query, limit=limit)
