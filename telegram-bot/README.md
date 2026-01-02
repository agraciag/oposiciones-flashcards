# 🤖 OpositApp Telegram Bot

Bot de Telegram para estudiar flashcards con repetición espaciada (SM-2).

## 📋 Requisitos

- Python 3.11+
- Backend FastAPI corriendo en `http://localhost:7999`
- Token de Telegram Bot (de @BotFather)
- Cuenta de usuario en OpositApp (regístrate en http://localhost:2998/register)

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
API_URL=http://localhost:7999/api
```

## ▶️ Iniciar Bot

**Con PM2 (recomendado):**
```bash
# Desde la raíz del proyecto
pm2 start ecosystem.config.js --only oposit-telegram

# Ver logs
pm2 logs oposit-telegram
```

**Manualmente:**
```bash
# Con venv activado
python3 bot.py
```

Deberías ver:
```
🤖 Iniciando OpositApp Bot con autenticación JWT...
✅ Bot iniciado correctamente
📡 Conectado a API: http://localhost:7999/api
🔐 Sistema de autenticación JWT activo
⏳ Esperando mensajes...
```

## 📱 Comandos Disponibles

### 🔐 Autenticación (Requerida)

**`/login username password`**
- Autenticarte con tu cuenta de OpositApp
- Ejemplo: `/login alejandro oposit2026`
- ⚠️ El bot borra tu mensaje automáticamente por seguridad
- Debes registrarte primero en http://localhost:2998/register

**`/logout`**
- Cerrar sesión actual
- Útil para cambiar de cuenta

### 📚 Comandos de Estudio

- `/start` - Iniciar bot y ver bienvenida
- `/help` - Ver ayuda completa
- `/study` - Comenzar sesión de estudio
- `/stats` - Ver estadísticas de progreso

### Flujo de Estudio

1. **Autentícate primero:** `/login username password`
2. Envía `/study` al bot
3. Te mostrará una pregunta de flashcard
4. Presiona **"Ver Respuesta"**
5. Evalúa qué tan bien la recordaste:
   - **❌ Otra vez** - No la recordaste (vuelve a 0, verás pronto)
   - **😰 Difícil** - Te costó recordarla (interval x 1.2)
   - **✅ Bien** - La recordaste bien (interval según SM-2 estándar)
   - **😊 Fácil** - Perfecto (interval x 1.3, EF +0.1)

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
2. Verifica que el backend esté corriendo (`http://localhost:7999`)
3. Prueba enviar `/start` de nuevo
4. Si persiste, reinicia el bot con `pm2 restart oposit-telegram`

### Error: "🔐 Necesitas autenticarte"

**Causa:** No has iniciado sesión o tu sesión expiró.

**Solución:**
```bash
# En Telegram:
/login username password
```

### El bot borra mi mensaje pero no responde

**Causa:** Esto es normal - el bot borra credenciales por seguridad.

**Solución:**
- Espera 1-2 segundos, el bot te responderá con confirmación
- Si no responde, verifica que el backend esté corriendo
- Revisa logs: `pm2 logs oposit-telegram`

## 📊 Arquitectura

```
┌─────────────┐
│  Telegram   │
│   Usuario   │
└──────┬──────┘
       │ /login, /study, /stats
       ▼
┌─────────────┐
│ Telegram Bot│◄─── bot.py (PM2: oposit-telegram)
│  (este bot) │     Almacena tokens JWT en memoria
└──────┬──────┘
       │ HTTP Requests + JWT Bearer Token
       ▼
┌─────────────┐
│  Backend    │◄─── FastAPI (localhost:7999)
│     API     │     Valida JWT, bcrypt passwords
└──────┬──────┘
       │ SQL Queries
       ▼
┌─────────────┐
│ PostgreSQL  │◄─── Docker (port 5399)
│   Database  │     Multi-tenant: users, decks, flashcards
└─────────────┘
```

### Flujo de Autenticación JWT:

1. Usuario envía `/login username password` al bot
2. Bot elimina el mensaje inmediatamente
3. Bot hace POST a `/api/auth/token` con credenciales
4. Backend valida contraseña con bcrypt
5. Si es válida, backend genera JWT con expiración de 30 días
6. Bot almacena el token asociado al `telegram_user_id`
7. Todas las peticiones subsecuentes incluyen `Authorization: Bearer {token}`
8. Backend valida el token en cada request y devuelve datos del usuario autenticado

## 🔐 Seguridad

### Medidas implementadas:

✅ **Contraseñas seguras:**
- Hasheadas con bcrypt en el backend
- Nunca se almacenan en texto plano
- bcrypt usa salt automático

✅ **Autenticación JWT:**
- Tokens con expiración de 30 días
- Firmados con SECRET_KEY del backend
- Validados en cada petición

✅ **Seguridad en mensajes:**
- Bot borra mensajes con credenciales automáticamente
- Tokens almacenados solo en memoria del bot
- Tokens se pierden al reiniciar (por diseño)

✅ **Variables de entorno:**
- `.env` NO está en el repositorio (`.gitignore`)
- NUNCA compartas tu `TELEGRAM_BOT_TOKEN`
- Para producción, usa variables de entorno del sistema

### ⚠️ Consideraciones:

- Los tokens JWT en memoria se pierden al reiniciar el bot (deberás hacer `/login` de nuevo)
- Para persistencia, considera implementar almacenamiento en Redis o base de datos
- En producción, usa HTTPS para el backend
- Considera implementar rate limiting para prevenir ataques de fuerza bruta

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
