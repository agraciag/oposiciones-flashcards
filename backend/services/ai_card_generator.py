"""
Servicio para generar flashcards usando IA a partir de texto
"""

import json
import anthropic
from config import settings


async def generate_cards_from_text(
    text: str,
    context: str = "",
    max_cards: int = 10
) -> list[dict]:
    """
    Genera flashcards a partir de texto usando Claude API

    Args:
        text: Texto fuente para generar flashcards
        context: Contexto adicional (ej: nombre del mazo, tema de estudio)
        max_cards: Número máximo de flashcards a generar

    Returns:
        list[dict]: Lista de flashcards con formato {front, back, tags, article_number, law_name}
    """
    try:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        # Limitar texto para evitar exceder tokens
        max_chars = 15000
        if len(text) > max_chars:
            text = text[:max_chars] + "\n\n[Texto truncado...]"

        # Construir contexto para el prompt
        context_str = f' para el tema "{context}"' if context else ""

        prompt = f"""Eres un asistente experto en crear flashcards (tarjetas de estudio) para oposiciones en España.

A partir del siguiente contenido, genera entre 5 y {max_cards} flashcards de alta calidad{context_str}.

CONTENIDO:
{text}

INSTRUCCIONES:
1. Crea flashcards que cubran los conceptos más importantes
2. Las preguntas deben ser claras y específicas
3. Las respuestas deben ser concisas pero completas
4. Si el contenido incluye legislación, menciona artículos y leyes específicos
5. Agrega tags relevantes separados por comas (ej: "constitución,derechos,artículo-15")
6. Si identificas un artículo específico, extrae el número (ej: "Art. 15") y la ley (ej: "Constitución Española")

FORMATO DE SALIDA (JSON):
[
  {{
    "front": "Pregunta clara y específica",
    "back": "Respuesta concisa y completa",
    "tags": "tag1,tag2,tag3",
    "article_number": "Art. 15",
    "law_name": "Constitución Española"
  }}
]

NOTAS:
- Los campos "article_number" y "law_name" son opcionales (usa null si no aplican)
- Devuelve SOLO el JSON, sin texto adicional antes ni después
- Asegúrate de que el JSON sea válido"""

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
            # Remover primera línea (```json o ```) y última línea (```)
            response_text = "\n".join(lines[1:-1]) if len(lines) > 2 else response_text

        # Parsear JSON
        flashcards = json.loads(response_text)

        # Validar estructura
        if not isinstance(flashcards, list):
            raise ValueError("La respuesta de IA no es una lista")

        # Validar y normalizar cada flashcard
        validated_cards = []
        for card in flashcards:
            if isinstance(card, dict) and "front" in card and "back" in card:
                validated_cards.append({
                    "front": str(card["front"]).strip(),
                    "back": str(card["back"]).strip(),
                    "tags": str(card.get("tags", "")).strip(),
                    "article_number": str(card.get("article_number", "")).strip() if card.get("article_number") else None,
                    "law_name": str(card.get("law_name", "")).strip() if card.get("law_name") else None
                })

        if not validated_cards:
            raise ValueError("No se generaron flashcards válidas")

        return validated_cards

    except json.JSONDecodeError as e:
        raise ValueError(f"Error al parsear respuesta JSON de Claude: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error al generar flashcards con IA: {str(e)}")
