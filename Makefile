# Makefile para OpositApp
.PHONY: help up down restart logs db-shell redis-shell backend test clean

help: ## Mostrar ayuda
	@echo "🧠 OpositApp - Comandos disponibles:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

up: ## Iniciar todos los servicios (PostgreSQL + Redis + pgAdmin)
	docker compose up -d
	@echo "✅ Servicios iniciados"
	@echo "📊 PostgreSQL: localhost:5435"
	@echo "🔴 Redis: localhost:6380"
	@echo "🖥️  pgAdmin: http://localhost:5050"
	@echo ""
	@echo "Credenciales PostgreSQL:"
	@echo "  Usuario: oposiciones"
	@echo "  Password: oposiciones2026"
	@echo "  Database: oposiciones_flashcards"
	@echo ""
	@echo "Credenciales pgAdmin:"
	@echo "  Email: admin@oposiciones.local"
	@echo "  Password: admin2026"

down: ## Detener todos los servicios
	docker compose down
	@echo "⏹️  Servicios detenidos"

restart: ## Reiniciar servicios
	docker compose restart
	@echo "🔄 Servicios reiniciados"

logs: ## Ver logs de todos los servicios
	docker compose logs -f

logs-postgres: ## Ver logs de PostgreSQL
	docker compose logs -f postgres

logs-redis: ## Ver logs de Redis
	docker compose logs -f redis

db-shell: ## Conectar a shell de PostgreSQL
	docker compose exec postgres psql -U oposiciones -d oposiciones_flashcards

redis-shell: ## Conectar a shell de Redis
	docker compose exec redis redis-cli -a oposiciones2026

backend: ## Iniciar backend FastAPI
	cd backend && python main.py

backend-dev: ## Iniciar backend en modo desarrollo
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

install: ## Instalar dependencias backend
	cd backend && python -m venv venv
	@echo "Activar venv:"
	@echo "  Windows: backend\\venv\\Scripts\\activate"
	@echo "  Linux/Mac: source backend/venv/bin/activate"
	@echo "Luego: pip install -r requirements.txt"

test: ## Ejecutar tests
	cd backend && pytest

clean: ## Limpiar contenedores y volúmenes (⚠️ BORRA DATOS)
	docker compose down -v
	@echo "⚠️  Datos borrados. Ejecuta 'make up' para recrear"

status: ## Ver estado de servicios
	docker compose ps

init-db: ## Inicializar base de datos (crear tablas)
	@echo "Creando tablas..."
	cd backend && python -c "from database import engine, Base; from models import *; Base.metadata.create_all(bind=engine); print('✅ Tablas creadas')"

seed-db: ## Poblar BD con datos de ejemplo
	@echo "🌱 Poblando base de datos con datos de ejemplo..."
	cd backend && python scripts/seed_data.py
