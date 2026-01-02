# Script PowerShell para detener todos los servicios de OpositApp
# Ejecutar: .\stop-all.ps1

Write-Host "🛑 Deteniendo OpositApp..." -ForegroundColor Cyan
Write-Host ""

# 1. Detener servicios PM2
Write-Host "🔧 Deteniendo servicios PM2..." -ForegroundColor Yellow
pm2 stop all

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Servicios PM2 detenidos" -ForegroundColor Green
} else {
    Write-Host "⚠️  PM2 no tenía servicios corriendo" -ForegroundColor Yellow
}

Write-Host ""

# 2. Detener Docker Compose
Write-Host "📦 Deteniendo servicios Docker..." -ForegroundColor Yellow
docker compose down

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Docker detenido correctamente" -ForegroundColor Green
} else {
    Write-Host "⚠️  Docker no tenía servicios corriendo" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "✅ Todos los servicios detenidos" -ForegroundColor Green
Write-Host ""
Write-Host "💡 Para iniciar de nuevo:" -ForegroundColor Cyan
Write-Host "   .\start-all.ps1" -ForegroundColor White
Write-Host ""
