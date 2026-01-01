# ✅ SETUP COMPLETADO - OpositApp

**Fecha:** 1 enero 2026
**Estado:** Backend y Base de Datos listos para usar

---

## 🎉 LO QUE ESTÁ FUNCIONANDO

### ✅ Docker Compose (Servicios levantados)

```bash
# Servicios corriendo:
✅ PostgreSQL - localhost:5435
✅ Redis - localhost:6380
✅ pgAdmin - http://localhost:5050

# Ver estado:
docker compose ps

# Ver logs:
docker compose logs -f
```

### ✅ Credenciales

**PostgreSQL:**
```
Host: localhost
Port: 5435
Usuario: oposiciones
Password: oposiciones2026
Database: oposiciones_flashcards
```

**Redis:**
```
Host: localhost
Port: 6380
Password: oposiciones2026
```

**pgAdmin:**
```
URL: http://localhost:5050
Email: admin@oposiciones.local
Password: admin2026
```

---

## 🚀 PRÓXIMO PASO (Mañana - 2 Enero)

### 1. Finalizar instalación dependencias Python

```bash
cd backend
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Verificar que se instalaron todas (debería salir sin errores)
pip list | grep fastapi
```

### 2. Crear tablas en base de datos

```bash
# Estando en backend/ con venv activo:
python3 create_tables.py

# Deberías ver:
# ✅ Tablas creadas exitosamente!
# - users
# - decks
# - flashcards
# - study_sessions
# - study_logs
# - legislation_updates
```

### 3. Iniciar backend

```bash
# Opción A - Con Make (desde raíz proyecto)
cd ..
make backend

# Opción B - Directamente
cd backend
python3 main.py

# Debería iniciar en:
# http://localhost:8000
```

### 4. Probar API

Abrir navegador:
- **API Docs:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/

Crear primer deck y flashcard usando Swagger UI.

---

## 📋 COMANDOS ÚTILES

### Gestión servicios Docker

```bash
make up          # Iniciar servicios
make down        # Detener servicios
make restart     # Reiniciar
make logs        # Ver logs
make status      # Ver estado
```

### Base de datos

```bash
make db-shell      # Shell PostgreSQL interactivo
make init-db       # Crear tablas (ejecuta create_tables.py)
```

### Backend

```bash
make backend       # Iniciar FastAPI
```

---

## 🧪 TEST RÁPIDO (Cuando esté todo listo)

### Via cURL:

```bash
# 1. Health check
curl http://localhost:8000/

# 2. Crear un deck
curl -X POST http://localhost:8000/api/decks/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Tema 1 - Constitución", "description": "Test"}'

# 3. Crear flashcard
curl -X POST http://localhost:8000/api/flashcards/ \
  -H "Content-Type: application/json" \
  -d '{
    "deck_id": 1,
    "front": "Art. 1 CE - ¿Qué dice?",
    "back": "España se constituye en Estado social y democrático de Derecho",
    "article_number": "Art. 1",
    "law_name": "Constitución Española"
  }'

# 4. Obtener siguiente tarjeta para estudiar
curl http://localhost:8000/api/study/next

# 5. Estudiar (marcar como good)
curl -X POST http://localhost:8000/api/study/review \
  -H "Content-Type: application/json" \
  -d '{
    "flashcard_id": 1,
    "quality": "good",
    "time_spent_seconds": 20
  }'
```

### Via Swagger UI:

1. Abrir http://localhost:8000/docs
2. Probar endpoint `POST /api/decks/` → Crear mazo
3. Probar endpoint `POST /api/flashcards/` → Crear tarjeta
4. Probar endpoint `GET /api/study/next` → Ver siguiente tarjeta
5. Probar endpoint `POST /api/study/review` → Estudiar tarjeta

---

## 🗄️ Verificar PostgreSQL

### Con pgAdmin:

1. Abrir http://localhost:5050
2. Login: `admin@oposiciones.local` / `admin2026`
3. Add New Server:
   - Name: `OpositApp`
   - Host name/address: `postgres` (nombre contenedor Docker)
   - Port: `5432` (puerto INTERNO)
   - Username: `oposiciones`
   - Password: `oposiciones2026`
4. Conectar y explorar base de datos

### Con shell directo:

```bash
make db-shell

# Dentro del shell PostgreSQL:
\dt                              # Listar tablas
\d flashcards                    # Ver estructura tabla flashcards
SELECT * FROM flashcards;        # Ver datos
\q                               # Salir
```

---

## 🐛 Troubleshooting

### "docker compose comando no encontrado"

```bash
# Verificar Docker instalado:
docker --version

# Si tienes docker-compose (guión):
docker-compose up -d
```

### "Puerto 5435 ocupado"

Edita `docker-compose.yml`:
```yaml
ports:
  - "5436:5432"  # Cambia 5435 por 5436
```

Y edita `backend/.env`:
```
DATABASE_URL=postgresql://oposiciones:oposiciones2026@localhost:5436/oposiciones_flashcards
```

### "ModuleNotFoundError"

```bash
# Asegúrate de activar venv:
cd backend
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Reinstalar dependencias:
pip install -r requirements.txt
```

### "Connection refused PostgreSQL"

```bash
# Verificar que Postgres está corriendo:
docker compose ps

# Si no está "Up (healthy)":
docker compose restart postgres

# Esperar 10 segundos y probar de nuevo
```

---

## 📁 ESTRUCTURA FINAL

```
oposiciones-flashcards/
├── backend/
│   ├── venv/                    # Entorno virtual Python
│   ├── main.py                  # API FastAPI
│   ├── models.py                # Modelos BD
│   ├── database.py              # Conexión BD
│   ├── config.py                # Configuración
│   ├── sm2.py                   # Algoritmo repetición espaciada
│   ├── create_tables.py         # Script crear tablas
│   ├── .env                     # Variables entorno
│   ├── requirements.txt         # Dependencias Python
│   └── routers/                 # Endpoints API
│       ├── flashcards.py
│       ├── decks.py
│       ├── study.py
│       ├── auth.py (stub)
│       └── legislation.py (stub)
├── docker-compose.yml           # Servicios Docker
├── Makefile                     # Comandos útiles
├── README.md                    # Documentación
├── PLAN-DESARROLLO.md           # Roadmap
└── SETUP-COMPLETO.md            # Este archivo
```

---

## ✅ CHECKLIST SETUP

- [x] Docker Compose creado
- [x] PostgreSQL corriendo (puerto 5435)
- [x] Redis corriendo (puerto 6380)
- [x] pgAdmin corriendo (puerto 5050)
- [x] Backend estructura completa
- [x] Modelos SQLAlchemy definidos
- [x] Algoritmo SM-2 implementado
- [x] API REST endpoints creados
- [x] Entorno virtual Python creado
- [ ] Dependencias Python instaladas ← **PENDIENTE (casi listo)**
- [ ] Tablas BD creadas ← **SIGUIENTE PASO**
- [ ] Backend corriendo ← **SIGUIENTE PASO**
- [ ] Primera flashcard creada ← **SIGUIENTE PASO**

---

## 📅 SIGUIENTE SESIÓN (2 Enero - 17:00)

### Agenda:

**17:00 - 17:30 (30 min)**
- Finalizar setup Python (si quedó algo)
- Crear tablas BD
- Arrancar backend
- Test básico API

**17:30 - 19:00 (90 min)**
- Crear seed data (datos de ejemplo)
- Poblar BD con flashcards de prueba
- Testing exhaustivo API
- Documentar bugs si hay

**19:00 - 19:30**
- Descanso, cena

**19:30 - 21:30 (120 min)**
- ESTUDIO: Tema 1 Día 2 (art. 56-107)
- Crear esquema Constitución

---

## 💾 BACKUP Y GIT

```bash
# Hacer commit de avances:
cd /mnt/d/dev_projects/oposiciones-flashcards
git add .
git commit -m "Setup: Dependencias instaladas y tablas creadas"

# Ver estado:
git status
git log --oneline
```

---

## 🎯 ESTADO ACTUAL

**FASE 1 (Backend Core): 90% COMPLETADO**

✅ Estructura proyecto
✅ Modelos de base de datos
✅ Algoritmo SM-2
✅ API CRUD básica
✅ Docker Compose setup
⏳ Tablas BD creadas (pendiente mañana)
⏳ Tests básicos (pendiente mañana)

**Siguiente:** Terminar Fase 1 mañana, empezar Fase 2 (Telegram Bot)

---

**¡Todo listo para arrancar mañana! 🚀**

**Servicios corriendo 24/7 (mientras Docker Desktop esté activo):**
- PostgreSQL esperando conexiones
- Redis listo para cachear
- pgAdmin para gestión visual

**Backend solo necesita:**
1. `python3 create_tables.py` (1 min)
2. `python3 main.py` (arranque inmediato)

**¡Nos vemos mañana a las 17:00! 💪**
