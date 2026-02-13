@echo off
REM Script para ejecutar el agente orchestrator
REM Verifica entorno virtual, conexion a Ollama y ejecuta el agente

setlocal enabledelayedexpansion

echo === Iniciando Agente Orchestrator ===

REM Activar entorno virtual si existe
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activando entorno virtual...
    call .venv\Scripts\activate.bat
) else (
    echo [WARNING] No se encontro entorno virtual ^(.venv^)
)

REM Instalar requerimientos si existe requirements.txt
if exist "requirements.txt" (
    echo [INFO] Instalando dependencias desde requirements.txt...
    pip install -q -r requirements.txt
)

REM Verificar que Ollama esta activo
echo [INFO] Verificando conexion con Ollama...
curl -s --max-time 5 http://localhost:11434/api/tags >nul 2>&1
if !ERRORLEVEL! EQU 0 (
    echo [OK] Ollama esta activo
) else (
    echo [ERROR] No se pudo conectar a Ollama en localhost:11434
    echo [ERROR] Asegurate de que Ollama este ejecutandose
    exit /b 1
)

REM Verificar que existe el archivo del agente
if not exist "orchestrator\agent.py" (
    echo [ERROR] No se encontro orchestrator\agent.py
    exit /b 1
)

REM Ejecutar el agente
echo [INFO] Ejecutando agente...
echo ----------------------------------------
set PYTHONPATH=.
python orchestrator\agent.py

REM Capturar codigo de salida
set EXIT_CODE=!ERRORLEVEL!

if !EXIT_CODE! EQU 0 (
    echo ----------------------------------------
    echo [OK] Agente ejecutado exitosamente
) else (
    echo ----------------------------------------
    echo [ERROR] El agente finalizo con codigo de error: !EXIT_CODE!
)

echo.
pause

if !EXIT_CODE! NEQ 0 (
    exit /b !EXIT_CODE!
)
