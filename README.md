# 🧠 OpositApp - Sistema Inteligente de Flashcards

**Aplicación personalizada de repetición espaciada para oposiciones**

Sistema completo de estudio con:
- ✅ Repetición espaciada (algoritmo SM-2)
- ✅ Bot Telegram integrado
- ✅ Verificación automática legislación BOE/BOA
- ✅ PWA offline-first
- ✅ Sincronización multi-dispositivo

---

## 🏗️ Arquitectura

```
oposiciones-flashcards/
├── backend/           # FastAPI + Python
├── frontend/          # Next.js + React
├── telegram-bot/      # Bot Telegram
└── shared/            # Tipos compartidos, utils
```

---

## 🚀 Stack Tecnológico

**Backend:**
- Python 3.11+
- FastAPI
- PostgreSQL
- SQLAlchemy (ORM)
- Alembic (migraciones)
- Redis (caché/sesiones)

**Frontend:**
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- PWA support

**Bot:**
- python-telegram-bot
- Webhooks

**Agente:**
- BeautifulSoup4 (scraping)
- Claude API (análisis)
- APScheduler (tareas programadas)

---

## ⚡ Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Telegram Bot

```bash
cd telegram-bot
pip install -r requirements.txt
python bot.py
```

---

## 📅 Roadmap Desarrollo

### FASE 1: MVP (Semana 1)
- [x] Estructura proyecto
- [ ] Backend API básica
- [ ] Base datos PostgreSQL
- [ ] Algoritmo SM-2
- [ ] CRUD flashcards
- [ ] Frontend básico

### FASE 2: Telegram (Semana 2)
- [ ] Bot Telegram
- [ ] Envío preguntas programadas
- [ ] Respuestas y evaluación
- [ ] Sincronización

### FASE 3: Agente (Semana 3)
- [ ] Scraper BOE/BOA
- [ ] Detector cambios
- [ ] Notificaciones
- [ ] Claude API integración

### FASE 4: Deploy (Semana 4)
- [ ] Testing
- [ ] Optimización
- [ ] Deploy producción
- [ ] Documentación

---

## 🎯 Prioridad

**Desarrollo en paralelo con estudio:**
- Desarrollo: 2h/día (17:00-19:00)
- Estudio: 2h/día (19:30-21:30)
- **Total: 4h/día productivas**

---

Creado: 1 enero 2026
Objetivo: App funcional en 3-4 semanas
