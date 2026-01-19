"""
Configuración de la aplicación
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Configuración global"""

    # Database
    DATABASE_URL: str = "postgresql://oposiciones:oposiciones@localhost:5399/oposiciones_flashcards"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # Auth
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 días

    # Telegram
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_WEBHOOK_URL: str = ""

    # Claude API
    ANTHROPIC_API_KEY: str = ""

    # Ollama (Local LLM)
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen3:30b"
    OLLAMA_TIMEOUT: int = 300  # 5 minutos max por request
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"

    # App
    DEBUG: bool = True
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS string into list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
