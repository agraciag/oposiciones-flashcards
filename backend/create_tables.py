"""
Script para crear tablas en la base de datos
"""

from database import engine, Base
from models import User, Deck, Flashcard, StudySession, StudyLog, LegislationUpdate

print("🗄️  Creando tablas en la base de datos...")

# Crear todas las tablas
Base.metadata.create_all(bind=engine)

print("✅ Tablas creadas exitosamente!")
print("\nTablas disponibles:")
print("  - users")
print("  - decks")
print("  - flashcards")
print("  - study_sessions")
print("  - study_logs")
print("  - legislation_updates")
