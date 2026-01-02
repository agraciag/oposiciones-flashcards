#!/bin/bash
# Script para iniciar todos los servicios de OpositApp
# Uso: ./start-all.sh

echo "🚀 Iniciando OpositApp..."
echo ""

# 1. Iniciar Docker Compose (PostgreSQL + Redis)
echo "📦 Iniciando servicios Docker (PostgreSQL + Redis)..."
docker compose up -d

if [ $? -ne 0 ]; then
    echo "❌ Error al iniciar Docker. ¿Está Docker corriendo?"
    exit 1
fi

echo "✅ Docker iniciado correctamente"
echo ""

# Esperar a que PostgreSQL esté listo
echo "⏳ Esperando a que PostgreSQL esté listo..."
sleep 5

# 2. Iniciar servicios con PM2
echo "🔧 Iniciando servicios con PM2..."

# Verificar si PM2 está instalado
if ! command -v pm2 &> /dev/null; then
    echo "❌ PM2 no está instalado. Instálalo con: npm install -g pm2"
    exit 1
fi

# Iniciar aplicaciones con PM2
pm2 start ecosystem.config.js

if [ $? -ne 0 ]; then
    echo "❌ Error al iniciar servicios con PM2"
    exit 1
fi

echo ""
echo "✅ Todos los servicios iniciados correctamente"
echo ""

# Mostrar estado de PM2
pm2 status

echo ""
echo "📊 Servicios disponibles:"
echo "   🌐 Frontend: http://localhost:2998"
echo "   🌐 Frontend (Cloudflare): https://cards.alejandrogracia.com"
echo "   🔌 Backend API: http://localhost:7999"
echo "   📚 API Docs: http://localhost:7999/docs"
echo "   🗄️  PostgreSQL: localhost:5399"
echo "   🔴 Redis: localhost:6379"
echo "   🤖 Bot Telegram: Activo"
echo ""
echo "💡 Comandos útiles:"
echo "   pm2 logs           - Ver logs de todos los servicios"
echo "   pm2 monit          - Monitor en tiempo real"
echo "   pm2 restart all    - Reiniciar todos los servicios"
echo "   pm2 stop all       - Detener todos los servicios"
echo "   ./stop-all.sh      - Detener TODO (PM2 + Docker)"
echo ""
