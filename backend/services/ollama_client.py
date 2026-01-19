"""
Cliente HTTP para Ollama API
Proporciona generación de texto usando modelos locales (qwen3:14b)
"""

import httpx
import asyncio
from typing import Optional, Dict, Any
from config import settings


class OllamaClient:
    """Cliente asíncrono para interactuar con Ollama API"""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None
    ):
        self.base_url = base_url or settings.OLLAMA_URL
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = timeout or settings.OLLAMA_TIMEOUT

    async def is_available(self) -> bool:
        """Verifica si Ollama está corriendo y accesible"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                return response.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list:
        """Lista los modelos disponibles en Ollama"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    return [m["name"] for m in data.get("models", [])]
                return []
        except Exception:
            return []

    async def model_exists(self, model_name: Optional[str] = None) -> bool:
        """Verifica si un modelo específico está disponible"""
        model = model_name or self.model
        models = await self.list_models()
        # Ollama puede tener el modelo con o sin tag
        return any(model in m or m.startswith(model.split(":")[0]) for m in models)

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False
    ) -> str:
        """
        Genera texto con Ollama.

        Args:
            prompt: El prompt para generar
            model: Modelo a usar (default: configurado)
            system: Mensaje de sistema opcional
            temperature: Creatividad (0.0-1.0)
            max_tokens: Máximo de tokens a generar
            stream: Si usar streaming (no implementado)

        Returns:
            Texto generado por el modelo
        """
        model_name = model or self.model

        payload: Dict[str, Any] = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }

        if system:
            payload["system"] = system

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )

                if response.status_code != 200:
                    error_text = response.text
                    raise OllamaError(f"Error de Ollama ({response.status_code}): {error_text}")

                data = response.json()
                return data.get("response", "")

        except httpx.TimeoutException:
            raise OllamaError(f"Timeout al generar con Ollama (>{self.timeout}s)")
        except httpx.ConnectError:
            raise OllamaError(f"No se puede conectar a Ollama en {self.base_url}")
        except Exception as e:
            raise OllamaError(f"Error en Ollama: {str(e)}")

    async def generate_with_context(
        self,
        prompt: str,
        context: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """
        Genera texto con contexto adicional (RAG).

        Args:
            prompt: La pregunta o tema a desarrollar
            context: Texto de contexto (fuentes normativas)
            model: Modelo a usar
            system: Mensaje de sistema personalizado
            temperature: Creatividad

        Returns:
            Texto generado
        """
        full_prompt = f"""CONTEXTO DISPONIBLE:
---
{context}
---

{prompt}"""

        return await self.generate(
            prompt=full_prompt,
            model=model,
            system=system,
            temperature=temperature
        )

    async def generate_stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        temperature: float = 0.7
    ):
        """
        Genera texto con streaming (generator).
        Útil para respuestas en tiempo real.
        """
        model_name = model or self.model

        payload: Dict[str, Any] = {
            "model": model_name,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": temperature,
            }
        }

        if system:
            payload["system"] = system

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/generate",
                    json=payload
                ) as response:
                    async for line in response.aiter_lines():
                        if line:
                            import json
                            data = json.loads(line)
                            if "response" in data:
                                yield data["response"]
                            if data.get("done"):
                                break
        except Exception as e:
            raise OllamaError(f"Error en streaming: {str(e)}")


class OllamaError(Exception):
    """Excepción personalizada para errores de Ollama"""
    pass


# Instancia global para uso conveniente
ollama = OllamaClient()


# Funciones de utilidad
async def test_ollama_connection() -> dict:
    """Prueba la conexión con Ollama y retorna estado"""
    client = OllamaClient()

    result = {
        "available": False,
        "url": client.base_url,
        "model": client.model,
        "model_available": False,
        "models": [],
        "error": None
    }

    try:
        result["available"] = await client.is_available()

        if result["available"]:
            result["models"] = await client.list_models()
            result["model_available"] = await client.model_exists()

    except Exception as e:
        result["error"] = str(e)

    return result


async def quick_generate(prompt: str, temperature: float = 0.7) -> str:
    """Generación rápida usando configuración por defecto"""
    client = OllamaClient()
    return await client.generate(prompt, temperature=temperature)
