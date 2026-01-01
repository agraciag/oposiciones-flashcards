# 🧠 OpositApp - Sistema Inteligente de Flashcards

**Aplicación personalizada de repetición espaciada para oposiciones**

Sistema completo de estudio con:
- ✅ Repetición espaciada (algoritmo SM-2)
- ✅ Bot Telegram integrado
- ✅ Verificación automática legislación BOE/BOA
- ✅ PWA offline-first
- ✅ Sincronización multi-dispositivo

---

## 🎯 ¿Cómo Usar OpositApp?

Tienes **3 formas** de estudiar tus flashcards:

### 📱 1. Telegram Bot (Recomendado para móvil)
```bash
# Configurar token en telegram-bot/.env
# Iniciar bot
cd telegram-bot
source venv/bin/activate
python3 bot.py

# En Telegram:
# 1. Busca tu bot
# 2. Envía /start
# 3. Usa /study para estudiar
```

### 💻 2. Interfaz Web (Recomendado para PC)
```bash
# Frontend ya corriendo en:
http://localhost:2998

# Accede a:
# - Dashboard: http://localhost:2998
# - Estudiar: http://localhost:2998/study
# - Crear tarjeta: http://localhost:2998/cards/new
```

### 🔧 3. API REST (Para desarrolladores)
```bash
# Ver docs interactivas:
http://localhost:7999/docs

# Endpoints:
GET  /api/study/next        # Obtener siguiente flashcard
POST /api/study/review      # Evaluar respuesta
GET  /api/study/stats       # Ver estadísticas
POST /api/flashcards/       # Crear flashcard
```

---

## 🚀 Quick Start

### 1. Iniciar servicios (PostgreSQL + Redis)

```bash
# Usando Make (recomendado)
make up

# O usando Docker Compose directamente
docker compose up -d
```

Esto inicia:
- **PostgreSQL** en puerto `5399`
- **Redis** en puerto `6379`
- **pgAdmin** en `http://localhost:5049` (opcional, para gestión visual)

### 2. Instalar dependencias backend

```bash
# Crear entorno virtual
cd backend
python -m venv venv

# Activar
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar paquetes
pip install -r requirements.txt
```

### 3. Inicializar base de datos

```bash
# Crear tablas
make init-db

# O manualmente:
cd backend
python -c "from database import engine, Base; from models import *; Base.metadata.create_all(bind=engine)"
```

### 4. Iniciar backend

```bash
# Desde raíz del proyecto
make backend

# O desde backend/
cd backend
python main.py
```

Backend disponible en:
- API: http://localhost:7999
- Docs: http://localhost:7999/docs
- Redoc: http://localhost:7999/redoc

---

## 📋 Comandos Make Disponibles

```bash
make help          # Ver todos los comandos
make up            # Iniciar servicios
make down          # Detener servicios
make restart       # Reiniciar servicios
make logs          # Ver logs
make db-shell      # Shell PostgreSQL
make redis-shell   # Shell Redis
make backend       # Iniciar backend
make init-db       # Crear tablas
make status        # Ver estado servicios
```

---

## 🔧 Configuración

### Puertos de la Aplicación

```
Frontend (Next.js):  http://localhost:2998
Backend API (FastAPI): http://localhost:7999
PostgreSQL:          localhost:5399
Redis:               localhost:6379
pgAdmin:             http://localhost:5049
```

### Credenciales PostgreSQL

```
Host: localhost
Port: 5399
Usuario: oposiciones
Password: oposiciones2026
Database: oposiciones_flashcards
```

### Credenciales Redis

```
Host: localhost
Port: 6379
Password: oposiciones2026
```

### Credenciales pgAdmin

```
URL: http://localhost:5049
Email: admin@oposiciones.local
Password: admin2026
```

---

## 🏗️ Arquitectura

```
oposiciones-flashcards/
├── backend/              # FastAPI + Python
│   ├── main.py          # Aplicación principal
│   ├── models.py        # Modelos SQLAlchemy
│   ├── database.py      # Configuración BD
│   ├── sm2.py           # Algoritmo repetición espaciada
│   └── routers/         # Endpoints API
├── frontend/            # Next.js + React (TODO)
├── telegram-bot/        # Bot Telegram (TODO)
├── docker-compose.yml   # Servicios Docker
├── Makefile            # Comandos útiles
└── README.md           # Este archivo
```

---

## 📊 Stack Tecnológico

**Backend:**
- Python 3.11+
- FastAPI
- PostgreSQL 15
- SQLAlchemy (ORM)
- Redis 7

**Frontend (TODO):**
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS

**Bot (TODO):**
- python-telegram-bot

**Infraestructura:**
- Docker Compose
- PostgreSQL (puerto 5435)
- Redis (puerto 6380)

---

## 🧪 Testing API

### Con cURL

```bash
# Health check
curl http://localhost:8000/

# Crear deck
curl -X POST http://localhost:8000/api/decks/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Tema 1 - Constitución", "description": "Materias comunes"}'

# Crear flashcard
curl -X POST http://localhost:8000/api/flashcards/ \
  -H "Content-Type: application/json" \
  -d '{
    "deck_id": 1,
    "front": "Art. 15 CE - ¿Qué derechos reconoce?",
    "back": "Derecho a la vida y a la integridad física y moral",
    "article_number": "Art. 15",
    "law_name": "Constitución Española"
  }'

# Obtener siguiente tarjeta para estudiar
curl http://localhost:8000/api/study/next

# Estudiar tarjeta (marcar como "good")
curl -X POST http://localhost:8000/api/study/review \
  -H "Content-Type: application/json" \
  -d '{
    "flashcard_id": 1,
    "quality": "good",
    "time_spent_seconds": 15
  }'
```

### Con Swagger UI

Abre http://localhost:8000/docs y prueba los endpoints interactivamente.

---

## 🗄️ Gestión Base de Datos

### Conectar con pgAdmin

1. Abre http://localhost:5050
2. Login: `admin@oposiciones.local` / `admin2026`
3. Add Server:
   - Name: OpositApp
   - Host: `postgres` (nombre del contenedor)
   - Port: `5432` (puerto interno)
   - Username: `oposiciones`
   - Password: `oposiciones2026`

### Shell directo PostgreSQL

```bash
make db-shell

# O manualmente:
docker compose exec postgres psql -U oposiciones -d oposiciones_flashcards
```

Comandos útiles:
```sql
\dt              -- Listar tablas
\d flashcards    -- Describir tabla
SELECT * FROM flashcards LIMIT 10;
```

---

## 🌐 Exponer con Cloudflare Tunnel

OpositApp está configurado para ser accesible públicamente vía Cloudflare Tunnel. Ambos servicios ya escuchan en `0.0.0.0` para permitir acceso externo.

### Configuración Actual

✅ **Frontend Next.js**: Configurado en `0.0.0.0:2998`
✅ **Backend FastAPI**: Configurado en `0.0.0.0:7999`

### Pasos para Exponer con Cloudflare

1. **Configura tu túnel de Cloudflare** con `extra_hosts`:
   ```yaml
   services:
     tunnel:
       image: cloudflare/cloudflared
       extra_hosts:
         - "host.docker.internal:host-gateway"
   ```

2. **En Cloudflare Zero Trust**, añade Public Hostnames:

   **Frontend:**
   - Service Type: `HTTP`
   - URL: `http://host.docker.internal:2998`
   - Public Hostname: `oposit.tudominio.com`

   **Backend API:**
   - Service Type: `HTTP`
   - URL: `http://host.docker.internal:7999`
   - Public Hostname: `api-oposit.tudominio.com`

3. **Actualiza CORS en `backend/.env`**:
   ```env
   ALLOWED_ORIGINS=http://localhost:2998,http://localhost:7999,https://oposit.tudominio.com,https://api-oposit.tudominio.com
   ```

4. **Reinicia el backend** para aplicar cambios de CORS:
   ```bash
   cd backend
   python main.py
   ```

### Documentación Completa

Ver [CLOUDFLARE_WSL_SETUP.md](./CLOUDFLARE_WSL_SETUP.md) para:
- Configuración detallada de túneles
- Ejemplos para otros frameworks
- Checklist de configuración
- Troubleshooting específico de Cloudflare

---

## 🐛 Troubleshooting

### Puerto ocupado

Si `5399`, `6379` o `5049` están ocupados, edita `docker-compose.yml`:
```yaml
ports:
  - "PUERTO_NUEVO:5432"  # Para PostgreSQL
  - "PUERTO_NUEVO:6379"  # Para Redis
  - "PUERTO_NUEVO:80"    # Para pgAdmin
```

Y actualiza `backend/.env`:
```
DATABASE_URL=postgresql://oposiciones:oposiciones2026@localhost:PUERTO_NUEVO/oposiciones_flashcards
REDIS_URL=redis://:oposiciones2026@localhost:PUERTO_NUEVO
```

### Recrear base de datos

```bash
make clean    # ⚠️ BORRA TODOS LOS DATOS
make up       # Reinicia servicios
make init-db  # Recrea tablas
```

### Ver logs

```bash
make logs              # Todos los servicios
make logs-postgres     # Solo PostgreSQL
make logs-redis        # Solo Redis
```

---

## 📅 Roadmap

### ✅ FASE 1: Backend Core - COMPLETADA (1 enero 2026)
- [x] Estructura proyecto
- [x] Modelos de base de datos
- [x] Algoritmo SM-2 implementado y probado
- [x] API CRUD completa funcionando
- [x] Docker Compose setup (PostgreSQL + Redis + pgAdmin)
- [x] Tablas BD creadas
- [x] Primera flashcard creada y revisada con SM-2
- [x] Sistema de tracking con study logs
- [x] Repositorio en GitHub: https://github.com/agraciag/oposiciones-flashcards
- [ ] Tests unitarios (próximamente)

### ✅ FASE 2: Frontend Web - COMPLETADA (1 enero 2026)
- [x] Setup Next.js 16 con TypeScript y Tailwind CSS
- [x] Dashboard con estadísticas en tiempo real
- [x] Interfaz de estudio interactiva
- [x] Formularios crear mazos y flashcards
- [x] Integración completa con API backend
- [x] Diseño responsive y moderno
- [x] Rutas: /, /study, /decks/new, /cards/new
- [x] Frontend corriendo en http://localhost:3000

### ✅ FASE 3: Telegram Bot - COMPLETADA (1 enero 2026)
- [x] Setup bot con python-telegram-bot 20.7
- [x] Comandos básicos: /start, /help, /study, /stats
- [x] Sistema de preguntas interactivo con botones inline
- [x] Evaluación SM-2 (Again, Hard, Good, Easy)
- [x] Integración con API backend
- [x] Sesiones de estudio por usuario
- [x] Manejo de errores y reconexión
- [x] README y documentación completa

### ✅ FASE 4: Contenido - COMPLETADA (1 enero 2026)
- [x] Script seed para Tema 1 Constitución
- [x] 16 flashcards Art. 14-29 (Derechos Fundamentales)
- [x] Metadatos completos: artículo, ley, tags
- [x] Listas para estudiar inmediatamente

### 🤖 FASE 4: Agente (Semana 4)
- [ ] Scraper BOE/BOA
- [ ] Detector cambios
- [ ] Claude API análisis
- [ ] Notificaciones

---

## 📝 Notas Desarrollo

**Creado:** 1 enero 2026
**Desarrollador:** Alejandro
**Coach:** Claude Code
**Objetivo:** App funcional en 3-4 semanas

**Horario desarrollo:**
- 17:00-19:00: Coding (2h/día)
- 19:30-21:30: Estudio temario (2h/día)

---

## 📄 Licencia

Proyecto personal - Uso educativo
