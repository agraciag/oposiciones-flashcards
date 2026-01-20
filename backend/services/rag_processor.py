"""
Procesador RAG (Retrieval-Augmented Generation)
Pipeline completo para procesar temas del temario usando normativa indexada y Ollama
"""

import re
import json
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session

from models import (
    StructuredTopic, NormativeSource, ProcessingLog,
    SourceType, ContentStatus, NormativeSourceType
)
from services.ollama_client import OllamaClient, OllamaError
from services.pdf_indexer import PDFIndexerService


class RAGProcessor:
    """Procesador RAG para generar contenido de temas"""

    # Prompt template para generación de contenido
    PROMPT_TEMPLATE = """Eres un experto en oposiciones de la Administración Pública española.
Tu tarea es desarrollar contenido educativo preciso y verificable para opositores.

TEMA A DESARROLLAR:
{topic_title}

FUENTES NORMATIVAS DISPONIBLES (usa SOLO estas fuentes para tu respuesta):
---
{context}
---

{extra_context}

INSTRUCCIONES:
1. Desarrolla el tema de forma clara, estructurada y pedagógica
2. Usa formato Markdown con títulos (##), listas y **negritas** para conceptos clave
3. **IMPORTANTE**: Cita las fuentes entre corchetes cuando uses información: [Nombre fuente, Art. X]
4. Si no encuentras información suficiente en el contexto, indica claramente qué aspectos no pudiste cubrir
5. No inventes información que no esté en las fuentes proporcionadas
6. Extensión recomendada: 500-1500 palabras según la complejidad del tema

DESARROLLA EL TEMA:"""

    SYSTEM_PROMPT = """Eres un asistente experto en preparación de oposiciones españolas.
Tu objetivo es generar contenido educativo de alta calidad basándote EXCLUSIVAMENTE en las fuentes normativas proporcionadas.
Siempre citas tus fuentes y nunca inventas información."""

    def __init__(self, db: Session, ollama: Optional[OllamaClient] = None):
        self.db = db
        self.ollama = ollama or OllamaClient()
        self.indexer = PDFIndexerService(db)

    async def process_topic(
        self,
        topic_id: int,
        extra_context: Optional[str] = None,
        use_embeddings: bool = False,
        temperature: float = 0.7,
        source_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Procesa un tema completo:
        1. Obtiene el tema
        2. Busca en normativa indexada (o usa fuentes específicas)
        3. Construye prompt con contexto
        4. Genera con Ollama
        5. Guarda resultado y log

        Args:
            topic_id: ID del tema a procesar
            extra_context: Contexto adicional del usuario
            use_embeddings: Si usar búsqueda semántica (futuro)
            temperature: Creatividad del modelo
            source_ids: IDs de fuentes específicas a usar (si None, busca automáticamente)

        Returns:
            Diccionario con resultado del procesamiento
        """
        # 1. Obtener tema
        topic = self.db.query(StructuredTopic).filter(StructuredTopic.id == topic_id).first()
        if not topic:
            return self._error_result(topic_id, "Tema no encontrado")

        # Log de inicio
        log = self._create_log(topic_id, "process", "started", {
            "extra_context": extra_context,
            "source_ids": source_ids
        })

        try:
            # 2. Buscar en normativa o usar fuentes específicas
            if source_ids:
                # Usar fuentes específicas seleccionadas por el usuario
                search_results = self._get_sources_by_ids(source_ids, topic.title)
            else:
                # Búsqueda automática
                search_results = self.search_relevant_sources(
                    topic.title,
                    use_embeddings=use_embeddings
                )

                if not search_results:
                    # Intentar con búsqueda más amplia
                    keywords = self._extract_keywords(topic.title)
                    for keyword in keywords:
                        search_results.extend(
                            self.search_relevant_sources(keyword, limit=3)
                        )

            # Actualizar log con fuentes encontradas
            self._update_log(log, sources_checked=len(search_results))

            # 3. Extraer chunks relevantes
            context, sources_used = self.extract_relevant_chunks(
                search_results,
                topic.title,
                max_tokens=4000
            )

            if not context.strip():
                # No se encontró contenido relevante - sugerir qué fuentes se necesitan
                suggested_sources = await self._suggest_required_sources(topic.title)
                self._update_log(log, "pending_sources", {
                    "warning": "No se encontró contenido relevante en la normativa",
                    "suggested_sources": suggested_sources
                })
                return {
                    "success": False,
                    "topic_id": topic_id,
                    "needs_sources": True,
                    "error": "No se encontraron fuentes normativas relevantes para este tema",
                    "suggested_sources": suggested_sources,
                    "message": "Para procesar este tema, necesitas subir los siguientes documentos:"
                }

            # 4. Construir prompt
            prompt = self.build_prompt(topic.title, context, extra_context)

            # 5. Generar con Ollama
            generated_content = await self.ollama.generate(
                prompt=prompt,
                system=self.SYSTEM_PROMPT,
                temperature=temperature
            )

            # 6. Guardar resultado
            topic.content = generated_content
            topic.source_type = SourceType.AI_GENERATED
            topic.source_reference = self._format_source_references(sources_used)
            topic.source_excerpt = context[:2000]  # Guardar primeros 2000 chars del contexto
            topic.content_status = ContentStatus.COMPLETE
            topic.last_processed_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(topic)

            # Log de éxito
            self._update_log(log, "completed", {
                "content_length": len(generated_content),
                "sources_used": len(sources_used),
                "source_names": [s["source_name"] for s in sources_used]
            })

            return {
                "success": True,
                "topic_id": topic_id,
                "content": generated_content,
                "sources_used": sources_used,
                "source_reference": topic.source_reference
            }

        except OllamaError as e:
            self._update_log(log, "failed", error_message=str(e))
            return self._error_result(topic_id, f"Error de Ollama: {str(e)}")
        except Exception as e:
            self._update_log(log, "failed", error_message=str(e))
            return self._error_result(topic_id, f"Error inesperado: {str(e)}")

    def search_relevant_sources(
        self,
        query: str,
        source_type: Optional[NormativeSourceType] = None,
        limit: int = 5,
        use_embeddings: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Busca fuentes relevantes para el query.

        Args:
            query: Texto a buscar
            source_type: Filtrar por tipo de fuente
            limit: Número máximo de resultados
            use_embeddings: Si usar búsqueda semántica (futuro)

        Returns:
            Lista de resultados con excerpts
        """
        if use_embeddings:
            # TODO: Implementar búsqueda semántica con embeddings
            pass

        return self.indexer.search_in_sources(
            query=query,
            source_type=source_type,
            limit=limit
        )

    def _get_sources_by_ids(
        self,
        source_ids: List[int],
        query: str
    ) -> List[Dict[str, Any]]:
        """
        Obtiene contenido de fuentes específicas por sus IDs.

        Args:
            source_ids: Lista de IDs de fuentes normativas
            query: Query para buscar contenido relevante dentro de las fuentes

        Returns:
            Lista de resultados con excerpts de las fuentes seleccionadas
        """
        results = []
        sources = self.db.query(NormativeSource).filter(
            NormativeSource.id.in_(source_ids)
        ).all()

        for source in sources:
            if not source.full_text:
                continue

            # Buscar contenido relevante dentro de esta fuente específica
            excerpt = self._get_extended_context(source.id, query, max_chars=3000)

            if not excerpt:
                # Si no encontramos el query específico, tomar el inicio del documento
                excerpt = source.full_text[:3000]

            results.append({
                "source_id": source.id,
                "source_name": source.name,
                "source_code": source.code,
                "excerpt": excerpt,
                "relevance_score": 1.0  # Máxima relevancia porque el usuario las seleccionó
            })

        return results

    def extract_relevant_chunks(
        self,
        sources: List[Dict[str, Any]],
        query: str,
        max_tokens: int = 4000
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Extrae chunks relevantes de las fuentes encontradas.

        Args:
            sources: Lista de fuentes con excerpts
            query: Query original para contexto
            max_tokens: Límite aproximado de tokens (~4 chars/token)

        Returns:
            Tupla (contexto_combinado, fuentes_usadas)
        """
        max_chars = max_tokens * 4
        context_parts = []
        sources_used = []
        total_chars = 0

        for source in sources:
            if total_chars >= max_chars:
                break

            excerpt = source.get("excerpt", "")
            if not excerpt:
                continue

            # Obtener más contexto si es posible
            full_context = self._get_extended_context(
                source["source_id"],
                query,
                max_chars=1500
            )

            if full_context:
                excerpt = full_context

            # Formatear con nombre de fuente
            chunk = f"\n### {source['source_name']}\n{excerpt}\n"

            if total_chars + len(chunk) <= max_chars:
                context_parts.append(chunk)
                sources_used.append(source)
                total_chars += len(chunk)

        return "\n".join(context_parts), sources_used

    def _get_extended_context(
        self,
        source_id: int,
        query: str,
        max_chars: int = 1500
    ) -> Optional[str]:
        """Obtiene contexto extendido de una fuente específica"""
        source = self.db.query(NormativeSource).filter(
            NormativeSource.id == source_id
        ).first()

        if not source or not source.full_text:
            return None

        # Buscar posición del query en el texto completo
        query_lower = query.lower()
        text_lower = source.full_text.lower()

        pos = text_lower.find(query_lower)
        if pos == -1:
            # Buscar primera palabra significativa
            words = [w for w in query_lower.split() if len(w) > 3]
            for word in words:
                pos = text_lower.find(word)
                if pos != -1:
                    break

        if pos == -1:
            return None

        # Extraer contexto ampliado
        start = max(0, pos - max_chars // 2)
        end = min(len(source.full_text), pos + max_chars // 2)

        context = source.full_text[start:end]

        # Limpiar inicio/fin
        if start > 0:
            first_newline = context.find('\n')
            if first_newline > 0 and first_newline < 100:
                context = context[first_newline + 1:]

        if end < len(source.full_text):
            last_newline = context.rfind('\n')
            if last_newline > len(context) - 100:
                context = context[:last_newline]

        return context.strip()

    def build_prompt(
        self,
        topic_title: str,
        context: str,
        extra_context: Optional[str] = None
    ) -> str:
        """
        Construye el prompt completo para Ollama.

        Args:
            topic_title: Título del tema
            context: Contexto de fuentes normativas
            extra_context: Contexto adicional del usuario

        Returns:
            Prompt formateado
        """
        extra_section = ""
        if extra_context:
            extra_section = f"\nINSTRUCCIONES ADICIONALES DEL USUARIO:\n{extra_context}\n"

        return self.PROMPT_TEMPLATE.format(
            topic_title=topic_title,
            context=context,
            extra_context=extra_section
        )

    def _extract_keywords(self, title: str) -> List[str]:
        """Extrae palabras clave de un título"""
        # Palabras a ignorar
        stopwords = {
            'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
            'de', 'del', 'en', 'con', 'por', 'para', 'sobre', 'entre',
            'y', 'o', 'que', 'se', 'su', 'sus', 'al', 'lo', 'como',
            'más', 'pero', 'sus', 'le', 'ya', 'o', 'fue', 'sido', 'tiene'
        }

        # Limpiar y tokenizar
        words = re.findall(r'\b[a-záéíóúüñ]+\b', title.lower())
        keywords = [w for w in words if w not in stopwords and len(w) > 3]

        return keywords

    def _format_source_references(self, sources: List[Dict[str, Any]]) -> str:
        """Formatea las referencias de fuentes"""
        if not sources:
            return ""

        refs = []
        for source in sources:
            name = source.get("source_name", "Fuente desconocida")
            code = source.get("source_code", "")
            if code:
                refs.append(f"{name} ({code})")
            else:
                refs.append(name)

        return "; ".join(refs)

    def _create_log(
        self,
        topic_id: int,
        action: str,
        status: str,
        input_data: Optional[Dict] = None
    ) -> ProcessingLog:
        """Crea un log de procesamiento"""
        log = ProcessingLog(
            topic_id=topic_id,
            action=action,
            agent_name="rag_processor",
            status=status,
            input_data=json.dumps(input_data) if input_data else None
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def _update_log(
        self,
        log: ProcessingLog,
        status: Optional[str] = None,
        output_data: Optional[Dict] = None,
        error_message: Optional[str] = None,
        sources_checked: Optional[int] = None
    ):
        """Actualiza un log de procesamiento"""
        if status:
            log.status = status
        if output_data:
            log.output_data = json.dumps(output_data)
        if error_message:
            log.error_message = error_message
        if sources_checked is not None:
            log.sources_checked = json.dumps({"count": sources_checked})

        self.db.commit()

    async def _suggest_required_sources(self, topic_title: str) -> List[Dict[str, str]]:
        """
        Usa Ollama para sugerir qué fuentes normativas se necesitan para un tema.

        Args:
            topic_title: Título del tema

        Returns:
            Lista de fuentes sugeridas con nombre y descripción
        """
        prompt = f"""Eres un experto en oposiciones españolas. Dado el siguiente tema de oposición, indica qué documentos legales/normativos serían necesarios para desarrollarlo correctamente.

TEMA: {topic_title}

Responde SOLO con un JSON array con el siguiente formato (sin explicaciones adicionales):
[
    {{"nombre": "Nombre del documento", "tipo": "LEY|REAL_DECRETO|CONSTITUCION|ESTATUTO|REGLAMENTO|ORDEN|DIRECTIVA", "descripcion": "Breve descripción de qué aporta al tema"}}
]

Incluye solo los documentos más relevantes (máximo 5). Sé específico con los nombres oficiales de las leyes."""

        try:
            response = await self.ollama.generate(
                prompt=prompt,
                system="Eres un asistente que responde únicamente con JSON válido, sin texto adicional.",
                temperature=0.3
            )

            # Limpiar respuesta y extraer JSON
            response = response.strip()
            # Buscar el array JSON en la respuesta
            start = response.find('[')
            end = response.rfind(']') + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                sources = json.loads(json_str)
                return sources

            return [{"nombre": "No se pudieron determinar las fuentes necesarias", "tipo": "DESCONOCIDO", "descripcion": "Revisa el tema manualmente"}]

        except Exception as e:
            return [{"nombre": f"Error al sugerir fuentes: {str(e)}", "tipo": "ERROR", "descripcion": "Intenta de nuevo más tarde"}]

    def _error_result(self, topic_id: int, error: str) -> Dict[str, Any]:
        """Genera un resultado de error"""
        return {
            "success": False,
            "topic_id": topic_id,
            "error": error
        }

    async def get_topic_sources(self, topic_id: int) -> Dict[str, Any]:
        """
        Obtiene las fuentes originales usadas para un tema.

        Args:
            topic_id: ID del tema

        Returns:
            Diccionario con las fuentes y excerpts
        """
        topic = self.db.query(StructuredTopic).filter(
            StructuredTopic.id == topic_id
        ).first()

        if not topic:
            return {"error": "Tema no encontrado"}

        # Obtener logs de procesamiento
        logs = self.db.query(ProcessingLog).filter(
            ProcessingLog.topic_id == topic_id,
            ProcessingLog.status == "completed"
        ).order_by(ProcessingLog.created_at.desc()).limit(5).all()

        return {
            "topic_id": topic_id,
            "topic_title": topic.title,
            "source_type": topic.source_type.value if topic.source_type else None,
            "source_reference": topic.source_reference,
            "source_excerpt": topic.source_excerpt,
            "last_processed_at": topic.last_processed_at.isoformat() if topic.last_processed_at else None,
            "processing_logs": [
                {
                    "action": log.action,
                    "status": log.status,
                    "created_at": log.created_at.isoformat(),
                    "output_data": json.loads(log.output_data) if log.output_data else None
                }
                for log in logs
            ]
        }


# Función de utilidad para procesamiento directo
async def process_single_topic(
    db: Session,
    topic_id: int,
    extra_context: Optional[str] = None
) -> Dict[str, Any]:
    """Procesa un tema individual"""
    processor = RAGProcessor(db)
    return await processor.process_topic(topic_id, extra_context)
