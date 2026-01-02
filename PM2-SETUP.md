# Configuración PM2 para OpositApp

Guía completa para gestionar todos los servicios de OpositApp con PM2 y configurar inicio automático con Windows.

## 📋 Requisitos Previos

- Node.js instalado
- Docker Desktop instalado
- Python 3.11+ instalado

## 🔧 Instalación de PM2

### 1. Instalar PM2 globalmente

**En WSL (Linux):**
```bash
npm install -g pm2
```

**En Windows PowerShell (nativo):**
```powershell
npm install -g pm2 pm2-windows-startup
```

Verifica la instalación:
```bash
pm2 --version
```

### 2. Configurar inicio automático

#### Opción A: WSL con inicio automático vía Windows

1. Instala PM2 en WSL:
   ```bash
   npm install -g pm2
   ```

2. Copia `start-wsl.bat` a la carpeta de inicio de Windows:
   ```powershell
   # Desde PowerShell de Windows
   copy D:\dev_projects\oposiciones-flashcards\start-wsl.bat "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\"
   ```

3. Reinicia Windows para probar.

#### Opción B: Windows PowerShell nativo

Para que PM2 inicie automáticamente con Windows:

```powershell
# Solo funciona en PowerShell de Windows, NO en WSL
npm install -g pm2-windows-startup
pm2-startup install
```

Esto instalará PM2 como servicio de Windows.

## 🚀 Uso Básico

### Iniciar todos los servicios

**En Windows (PowerShell):**
```powershell
.\start-all.ps1
```

**En Linux/WSL (Bash):**
```bash
chmod +x start-all.sh
./start-all.sh
```

Esto iniciará automáticamente:
1. ✅ Docker Compose (PostgreSQL + Redis)
2. ✅ Backend FastAPI (puerto 7999)
3. ✅ Frontend Next.js (puerto 2998)
4. ✅ Bot de Telegram

### Detener todos los servicios

**En Windows (PowerShell):**
```powershell
.\stop-all.ps1
```

**En Linux/WSL (Bash):**
```bash
./stop-all.sh
```

## 📊 Comandos Útiles de PM2

### Ver estado de todos los servicios
```bash
pm2 status
```

### Ver logs en tiempo real
```bash
# Todos los servicios
pm2 logs

# Servicio específico
pm2 logs oposit-backend
pm2 logs oposit-frontend
pm2 logs oposit-telegram
```

### Monitor en tiempo real
```bash
pm2 monit
```

### Reiniciar servicios
```bash
# Todos
pm2 restart all

# Específico
pm2 restart oposit-backend
pm2 restart oposit-frontend
pm2 restart oposit-telegram
```

### Detener servicios
```bash
# Todos
pm2 stop all

# Específico
pm2 stop oposit-backend
```

### Eliminar servicios de PM2
```bash
pm2 delete all
```

## 🔄 Configurar Inicio Automático con Windows

### Paso 1: Iniciar los servicios manualmente
```powershell
.\start-all.ps1
```

### Paso 2: Guardar la configuración actual
```bash
pm2 save
```

Esto guarda el estado actual de PM2 para que se restaure al reiniciar.

### Paso 3: Configurar pm2-windows-startup

Si ya instalaste `pm2-windows-startup` anteriormente:

```powershell
pm2-startup install
```

### Paso 4: Verificar configuración

Reinicia tu PC y verifica que los servicios de PM2 inicien automáticamente:

```bash
pm2 status
```

**⚠️ Nota importante:** Docker Desktop también debe estar configurado para iniciar con Windows. Ve a:
- Docker Desktop → Settings → General → "Start Docker Desktop when you log in"

## 📁 Estructura de Logs

Los logs de PM2 se guardan en:
```
oposiciones-flashcards/logs/
├── backend-error.log
├── backend-out.log
├── frontend-error.log
├── frontend-out.log
├── telegram-error.log
└── telegram-out.log
```

### Ver ubicación de logs
```bash
pm2 show oposit-backend
```

### Limpiar logs
```bash
pm2 flush
```

## 🛠️ Troubleshooting

### PM2 no reconocido en PowerShell

Si obtienes error "pm2 no se reconoce como comando":

1. Verifica que Node.js esté en el PATH
2. Reinicia PowerShell/Terminal
3. O usa la ruta completa:
   ```powershell
   & "$env:APPDATA\npm\pm2.cmd" status
   ```

### Servicios no inician automáticamente en Windows

1. Verifica que pm2-windows-startup esté instalado:
   ```powershell
   pm2-startup
   ```

2. Reinstala el servicio:
   ```powershell
   pm2-startup uninstall
   pm2-startup install
   ```

3. Verifica en Servicios de Windows:
   - Presiona `Win + R`
   - Escribe `services.msc`
   - Busca "PM2"
   - Estado debe ser "En ejecución" y Tipo de inicio "Automático"

### Backend falla al iniciar

Verifica que el entorno virtual de Python esté activado:
```bash
cd backend
source venv/bin/activate  # Linux/WSL
# o
.\venv\Scripts\activate   # Windows
```

Luego guarda de nuevo:
```bash
pm2 restart oposit-backend
pm2 save
```

### Frontend falla con error de memoria

Aumenta el límite de memoria en `ecosystem.config.js`:
```javascript
{
  name: 'oposit-frontend',
  max_memory_restart: '2G',  // Aumentar de 1G a 2G
  ...
}
```

Luego reinicia:
```bash
pm2 reload ecosystem.config.js
pm2 save
```

## 🔐 Seguridad

### Gestión de secretos

**NO** commites archivos `.env` con tokens sensibles. PM2 cargará automáticamente las variables de entorno desde los archivos `.env` en cada directorio.

Asegúrate de tener:
- `backend/.env` - Configuración del backend
- `telegram-bot/.env` - Token del bot de Telegram
- `frontend/.env.local` - URL de la API

## 📚 Comandos de Mantenimiento

### Actualizar PM2
```bash
npm install -g pm2@latest
pm2 update
```

### Backup de configuración
```bash
pm2 save
```

Esto guarda en: `~/.pm2/dump.pm2`

### Restaurar desde backup
```bash
pm2 resurrect
```

## 🎯 Flujo de Trabajo Recomendado

### Desarrollo diario:
```bash
# Iniciar todo
.\start-all.ps1  # o ./start-all.sh

# Trabajar...

# Ver logs si hay problemas
pm2 logs

# Reiniciar servicio específico si haces cambios
pm2 restart oposit-backend

# Al terminar (opcional, deja corriendo si quieres)
.\stop-all.ps1  # o ./stop-all.sh
```

### Primera vez / Después de clonar:
```bash
# Instalar dependencias
cd backend && pip install -r requirements.txt
cd ../frontend && npm install
cd ../telegram-bot && pip install -r requirements.txt

# Configurar .env en cada directorio
# (backend/.env, telegram-bot/.env, frontend/.env.local)

# Iniciar servicios
.\start-all.ps1

# Guardar configuración
pm2 save
```

## 📖 Recursos Adicionales

- [Documentación oficial de PM2](https://pm2.keymetrics.io/)
- [pm2-windows-startup en NPM](https://www.npmjs.com/package/pm2-windows-startup)
- [Guía de PM2 para Windows](https://pm2.keymetrics.io/docs/usage/startup/#windows)

---

**Última actualización:** 1 enero 2026
