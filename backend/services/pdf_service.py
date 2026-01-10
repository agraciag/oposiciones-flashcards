"""
Servicio para procesar PDFs y generar flashcards con IA
"""

import io
import json
from pypdf import PdfReader
import anthropic
from config import settings


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extrae texto de un archivo PDF

    Args:
        file_bytes: Bytes del archivo PDF

    Returns:
        str: Texto extraído del PDF
    """
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n\n"
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error al extraer texto del PDF: {str(e)}")


async def generate_flashcards_from_text(text: str, deck_name: str, max_cards: int = 20) -> list[dict]:
    """
    Genera flashcards a partir de texto usando Claude API

    Args:
        text: Texto fuente para generar flashcards
        deck_name: Nombre del mazo (para contexto)
        max_cards: Número máximo de flashcards a generar

    Returns:
        list[dict]: Lista de flashcards con formato {front, back, tags}
    """
    try:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        # Limitar texto para evitar exceder tokens
        max_chars = 15000
        if len(text) > max_chars:
            text = text[:max_chars] + "\n\n[Texto truncado...]"

        prompt = f"""Eres un asistente experto en crear flashcards (tarjetas de estudio) para oposiciones en España.

A partir del siguiente contenido, genera entre 10 y {max_cards} flashcards de alta calidad para el mazo titulado "{deck_name}".

CONTENIDO:
{text}

INSTRUCCIONES:
1. Crea flashcards que cubran los conceptos más importantes
2. Las preguntas deben ser claras y específicas
3. Las respuestas deben ser concisas pero completas
4. Si el contenido incluye legislación, menciona artículos y leyes
5. Agrega tags relevantes (ej: "constitución", "derechos", "artículo-15")

FORMATO DE SALIDA (JSON):
[
  {{
    "front": "Pregunta clara y específica",
    "back": "Respuesta concisa y completa",
    "tags": "tag1,tag2,tag3"
  }}
]

IMPORTANTE: Devuelve SOLO el JSON, sin texto adicional antes ni después."""

        message = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4000,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        # Extraer respuesta
        response_text = message.content[0].text.strip()

        # Limpiar markdown code blocks si existen
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1]) if len(lines) > 2 else response_text

        # Parsear JSON
        flashcards = json.loads(response_text)

        # Validar estructura
        if not isinstance(flashcards, list):
            raise ValueError("La respuesta de IA no es una lista")

        # Validar cada flashcard
        validated_cards = []
        for card in flashcards:
            if isinstance(card, dict) and "front" in card and "back" in card:
                validated_cards.append({
                    "front": str(card["front"]).strip(),
                    "back": str(card["back"]).strip(),
                    "tags": str(card.get("tags", "")).strip()
                })

        if not validated_cards:
            raise ValueError("No se generaron flashcards válidas")

        return validated_cards

    except json.JSONDecodeError as e:
        raise ValueError(f"Error al parsear respuesta JSON de Claude: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error al generar flashcards con IA: {str(e)}")
