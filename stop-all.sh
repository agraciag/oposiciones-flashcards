#!/bin/bash
# Script para detener todos los servicios de OpositApp
# Uso: ./stop-all.sh

echo "🛑 Deteniendo OpositApp..."
echo ""

# 1. Detener servicios PM2
echo "🔧 Deteniendo servicios PM2..."
pm2 stop all

if [ $? -eq 0 ]; then
    echo "✅ Servicios PM2 detenidos"
else
    echo "⚠️  PM2 no tenía servicios corriendo"
fi

echo ""

# 2. Detener Docker Compose
echo "📦 Deteniendo servicios Docker..."
docker compose down

if [ $? -eq 0 ]; then
    echo "✅ Docker detenido correctamente"
else
    echo "⚠️  Docker no tenía servicios corriendo"
fi

echo ""
echo "✅ Todos los servicios detenidos"
echo ""
echo "💡 Para iniciar de nuevo:"
echo "   ./start-all.sh"
echo ""
