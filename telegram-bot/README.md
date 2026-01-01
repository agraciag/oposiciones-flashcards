# 🤖 OpositApp Telegram Bot

Bot de Telegram para estudiar flashcards con repetición espaciada (SM-2).

## 📋 Requisitos

- Python 3.11+
- Backend FastAPI corriendo en `http://localhost:8000`
- Token de Telegram Bot (de @BotFather)

## 🚀 Instalación

### 1. Crear entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar token

Edita el archivo `.env` con tu token de bot:

```env
TELEGRAM_BOT_TOKEN=tu_token_aqui
API_URL=http://localhost:8000/api
```

## ▶️ Iniciar Bot

```bash
# Con venv activado
python3 bot.py
```

Deberías ver:
```
🤖 Iniciando OpositApp Bot...
✅ Bot iniciado correctamente
📡 Conectado a API: http://localhost:8000/api
⏳ Esperando mensajes...
```

## 📱 Comandos Disponibles

### Comandos Básicos

- `/start` - Iniciar bot y ver bienvenida
- `/help` - Ver ayuda completa
- `/study` - Comenzar sesión de estudio
- `/stats` - Ver estadísticas de progreso

### Flujo de Estudio

1. Envía `/study` al bot
2. Te mostrará una pregunta de flashcard
3. Presiona **"Ver Respuesta"**
4. Evalúa qué tan bien la recordaste:
   - **❌ Otra vez** - No la recordaste (intervalo: 1 día)
   - **😰 Difícil** - Te costó (intervalo reducido)
   - **✅ Bien** - La recordaste bien (intervalo normal)
   - **😊 Fácil** - Perfecto (intervalo aumentado)

El algoritmo SM-2 ajustará automáticamente cuándo volver a mostrarte cada tarjeta.

## 🔧 Troubleshooting

### Error: "Conflict: terminated by other getUpdates request"

**Causa:** Ya hay otra instancia del bot corriendo.

**Solución:**
```bash
# Detener todas las instancias
pkill -f "python3 bot.py"

# Esperar 2-3 segundos
sleep 3

# Reiniciar
python3 bot.py
```

### Error: "No se pudo conectar con el servidor"

**Causa:** El backend no está corriendo.

**Solución:**
```bash
# Desde la raíz del proyecto
cd ../backend
source venv/bin/activate
python3 main.py
```

### El bot no responde

1. Verifica que el bot esté corriendo (no errores en consola)
2. Verifica que el backend esté corriendo (`http://localhost:8000`)
3. Prueba enviar `/start` de nuevo
4. Si persiste, reinicia el bot

## 📊 Arquitectura

```
┌─────────────┐
│  Telegram   │
│   Usuario   │
└──────┬──────┘
       │ /study, /stats, etc.
       ▼
┌─────────────┐
│ Telegram Bot│◄─── bot.py
│  (este bot) │
└──────┬──────┘
       │ HTTP Requests
       ▼
┌─────────────┐
│  Backend    │◄─── FastAPI (localhost:8000)
│     API     │
└──────┬──────┘
       │ SQL Queries
       ▼
┌─────────────┐
│ PostgreSQL  │◄─── Docker (port 5435)
│   Database  │
└─────────────┘
```

## 🔐 Seguridad

**IMPORTANTE:**
- El archivo `.env` NO está en el repositorio (está en `.gitignore`)
- NUNCA compartas tu `TELEGRAM_BOT_TOKEN`
- Para producción, usa variables de entorno del sistema

## 📝 Desarrollo

### Agregar nuevos comandos

```python
async def mi_nuevo_comando(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola!")

# Registrar en main()
application.add_handler(CommandHandler("micomando", mi_nuevo_comando))
```

### Ver logs en tiempo real

El bot usa logging estándar de Python. Los logs se muestran en consola.

## 🎯 Próximas Funcionalidades

- [ ] Envío automático de preguntas programadas
- [ ] Recordatorios personalizados
- [ ] Estadísticas detalladas por tema
- [ ] Exportar progreso
- [ ] Modo competitivo con amigos

## 📄 Licencia

Proyecto personal - Uso educativo
