@echo off
REM Script para iniciar OpositApp en WSL desde Windows
REM Colocar este archivo en: shell:startup para inicio automático

echo Iniciando OpositApp en WSL...

REM Iniciar Docker Desktop primero (si no está corriendo)
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"

REM Esperar 10 segundos a que Docker inicie
timeout /t 10 /nobreak

REM Ejecutar start-all.sh en WSL
wsl -d Ubuntu -e bash -c "cd /mnt/d/dev_projects/oposiciones-flashcards && ./start-all.sh"

echo OpositApp iniciado correctamente
timeout /t 5
