#!/bin/bash

# Script para ejecutar el agente orchestrator
# Verifica entorno virtual, conexión a Ollama y ejecuta el agente

set -e

echo "=== Iniciando Agente Orchestrator ==="

# Activar entorno virtual si existe
if [ -d ".venv" ]; then
    echo "[INFO] Activando entorno virtual..."
    source .venv/bin/activate
else
    echo "[WARNING] No se encontró entorno virtual (.venv)"
fi

# Instalar requerimientos si existe requirements.txt
if [ -f "requirements.txt" ]; then
    echo "[INFO] Instalando dependencias desde requirements.txt..."
    pip install -q -r requirements.txt
fi

# Verificar que Ollama está activo
echo "[INFO] Verificando conexión con Ollama..."
if curl -s --max-time 5 http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "[OK] Ollama está activo"
else
    echo "[ERROR] No se pudo conectar a Ollama en localhost:11434"
    echo "[ERROR] Asegúrate de que Ollama esté ejecutándose"
    exit 1
fi

# Verificar que existe el archivo del agente
if [ ! -f "orchestrator/agent.py" ]; then
    echo "[ERROR] No se encontró orchestrator/agent.py"
    exit 1
fi

# Ejecutar el agente
echo "[INFO] Ejecutando agente..."
echo "----------------------------------------"
PYTHONPATH=. python orchestrator/agent.py

# Capturar código de salida
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "----------------------------------------"
    echo "[OK] Agente ejecutado exitosamente"
else
    echo "----------------------------------------"
    echo "[ERROR] El agente finalizó con código de error: $EXIT_CODE"
fi

echo ""
read -p "Presiona Enter para salir..."

if [ $EXIT_CODE -ne 0 ]; then
    exit $EXIT_CODE
fi
