# Script PowerShell para iniciar todos los servicios de OpositApp
# Ejecutar: .\start-all.ps1

Write-Host "🚀 Iniciando OpositApp..." -ForegroundColor Cyan
Write-Host ""

# 1. Iniciar Docker Compose (PostgreSQL + Redis)
Write-Host "📦 Iniciando servicios Docker (PostgreSQL + Redis)..." -ForegroundColor Yellow
docker compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al iniciar Docker. ¿Está Docker Desktop corriendo?" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Docker iniciado correctamente" -ForegroundColor Green
Write-Host ""

# Esperar a que PostgreSQL esté listo
Write-Host "⏳ Esperando a que PostgreSQL esté listo..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

# 2. Iniciar servicios con PM2
Write-Host "🔧 Iniciando servicios con PM2..." -ForegroundColor Yellow

# Verificar si PM2 está instalado
$pm2Installed = Get-Command pm2 -ErrorAction SilentlyContinue
if (-not $pm2Installed) {
    Write-Host "❌ PM2 no está instalado. Instálalo con: npm install -g pm2" -ForegroundColor Red
    exit 1
}

# Iniciar aplicaciones con PM2
pm2 start ecosystem.config.js

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error al iniciar servicios con PM2" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ Todos los servicios iniciados correctamente" -ForegroundColor Green
Write-Host ""

# Mostrar estado de PM2
pm2 status

Write-Host ""
Write-Host "📊 Servicios disponibles:" -ForegroundColor Cyan
Write-Host "   🌐 Frontend: http://localhost:2998" -ForegroundColor White
Write-Host "   🌐 Frontend (Cloudflare): https://cards.alejandrogracia.com" -ForegroundColor White
Write-Host "   🔌 Backend API: http://localhost:7999" -ForegroundColor White
Write-Host "   📚 API Docs: http://localhost:7999/docs" -ForegroundColor White
Write-Host "   🗄️  PostgreSQL: localhost:5399" -ForegroundColor White
Write-Host "   🔴 Redis: localhost:6379" -ForegroundColor White
Write-Host "   🤖 Bot Telegram: Activo" -ForegroundColor White
Write-Host ""
Write-Host "💡 Comandos útiles:" -ForegroundColor Cyan
Write-Host "   pm2 logs           - Ver logs de todos los servicios" -ForegroundColor White
Write-Host "   pm2 monit          - Monitor en tiempo real" -ForegroundColor White
Write-Host "   pm2 restart all    - Reiniciar todos los servicios" -ForegroundColor White
Write-Host "   pm2 stop all       - Detener todos los servicios" -ForegroundColor White
Write-Host "   .\stop-all.ps1     - Detener TODO (PM2 + Docker)" -ForegroundColor White
Write-Host ""
