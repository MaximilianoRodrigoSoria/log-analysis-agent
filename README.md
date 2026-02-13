# 🤖 LLM Lab - Analizador de Logs con IA

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)
![Status](https://img.shields.io/badge/status-Active-success.svg)
![Ollama](https://img.shields.io/badge/Ollama-Compatible-orange.svg)

Laboratorio de Machine Learning para análisis automatizado de logs mediante herramientas especializadas y detección inteligente de patrones.

## 📋 Descripción

Sistema automatizado de análisis de logs que:
- 🔍 **Parsea y estructura logs** de aplicaciones Java
- 🎯 **Identifica tipos de excepciones** (NullPointerException, SQLException, TimeoutException, etc.)
- 📊 **Detecta patrones** (errores repetitivos, hotspots, ventanas temporales)
- 📝 **Genera reportes profesionales** en Markdown con análisis detallado
- ⚡ **Cross-platform** con scripts para Windows y Unix

## 🏗️ Arquitectura

```
llm-lab/
├── orchestrator/          # Agente orquestador principal
│   ├── agent.py          # Lógica de orquestación y análisis
│   └── __init__.py
├── tools/                # Herramientas especializadas
│   ├── log_analyzer.py   # Parser y analizador de logs
│   ├── report_generator.py  # Generador de reportes MD
│   └── __init__.py
├── datasets/             # Logs de entrada
│   └── generated_logs.txt
├── out/                  # Reportes generados (creado automáticamente)
├── run.sh               # Script Unix para ejecutar
├── run.bat              # Script Windows para ejecutar
├── generate_logs.sh     # Generador de logs de prueba (Unix)
├── generate_logs.bat    # Generador de logs de prueba (Windows)
└── requirements.txt     # Dependencias Python
```

## 🚀 Inicio Rápido

### Prerrequisitos

- Python 3.8 o superior
- (Opcional) Entorno virtual Python
- Conexión a internet para instalar dependencias

### Instalación

1. **Clonar o descargar el proyecto**

2. **Crear entorno virtual (recomendado)**
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate

   # Unix/Linux/macOS
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Las dependencias se instalan automáticamente al ejecutar los scripts**

### Uso

#### Generar logs de prueba

```bash
# Windows
generate_logs.bat

# Unix/Linux/macOS
bash generate_logs.sh
```

Esto crea `datasets/generated_logs.txt` con errores simulados.

#### Ejecutar análisis

```bash
# Windows
run.bat

# Unix/Linux/macOS
bash run.sh
```

El script automáticamente:
1. ✅ Activa el entorno virtual (si existe)
2. ✅ Instala dependencias desde `requirements.txt`
3. ✅ Analiza los logs
4. ✅ Genera reporte en `out/log_analysis_[timestamp].md`

#### Opciones avanzadas

```bash
# Analizar un archivo específico
python orchestrator/agent.py --log-file path/to/your/logfile.txt
```

## 📊 Capacidades de Análisis

### Tipos de Errores Detectados

- **NullPointerException**: Acceso a referencias nulas
- **SQLException**: Errores de base de datos (timeouts, duplicados, etc.)
- **SocketTimeoutException**: Timeouts en conexiones HTTP/Socket
- **MessagingException**: Errores en envío de emails
- Y cualquier otra excepción Java estándar

### Análisis de Patrones

1. **Errores Repetitivos**: Identifica excepciones recurrentes con contador
2. **Hotspots**: Componentes/clases con mayor cantidad de errores
3. **Ventana Temporal**: Rango de tiempo de los incidentes
4. **Agrupación Inteligente**: Por tipo + ubicación + línea

### Formato del Reporte

El reporte generado incluye:

```markdown
# 📊 Reporte de Análisis de Logs

## 📈 Resumen Ejecutivo
- Total de eventos, errores, warnings

## 🔴 Tipos de Errores Encontrados
- Distribución por tipo de excepción

## 🔍 Análisis de Patrones
- Errores repetitivos
- Hotspots (componentes más afectados)
- Ventana temporal

## 📋 Detalle de Grupos de Errores
- Stack traces
- Muestras de errores
- Rangos temporales

## ⚡ Advertencias (WARN)
```

## 🛠️ Tecnologías

- **Python 3.8+**: Lenguaje principal
- **Requests**: Cliente HTTP para APIs
- **Regex**: Parseo avanzado de logs
- **Bash/Batch**: Scripts de automatización cross-platform

## 📁 Estructura de Datos

### Formato de Entrada (Logs)

```
2026-02-13 08:30:15 ERROR [main] com.example.service.UserService - Error al procesar solicitud
java.lang.NullPointerException: Cannot invoke method on null object
	at com.example.service.UserService.getUserById(UserService.java:45)
	at com.example.controller.UserController.getUser(UserController.java:89)
```

### Formato de Salida (JSON interno)

```json
{
  "summary": {
    "total_events": 15,
    "total_errors": 8,
    "total_warnings": 3
  },
  "error_groups": [
    {
      "exception": "java.lang.NullPointerException",
      "count": 2,
      "top_frame": {
        "where": "com.example.service.UserService.getUserById",
        "file": "UserService.java",
        "line": 45
      }
    }
  ]
}
```

## 🧪 Desarrollo

### Estructura de Módulos

#### `tools/log_analyzer.py`
Parser especializado en logs Java con regex avanzados para:
- Headers con timestamp, nivel, thread, logger
- Excepciones con mensajes
- Stack traces con ubicación exacta

#### `tools/report_generator.py`
Generador de reportes Markdown que:
- Analiza distribución de errores
- Detecta patrones automáticamente
- Formatea con emojis y estructura clara

#### `orchestrator/agent.py`
Orquestador principal que:
- Gestiona el flujo de análisis
- Coordina herramientas
- Genera salida final

## 🤝 Contribución

Este es un proyecto de laboratorio educativo. Sugerencias y mejoras son bienvenidas.

## 📄 Licencia

MIT License - Ver archivo LICENSE para más detalles

## 🔗 Enlaces Útiles

- [Python Documentation](https://docs.python.org/3/)
- [Regular Expressions Guide](https://docs.python.org/3/library/re.html)
- [Markdown Guide](https://www.markdownguide.org/)

## 📞 Soporte

Para reportar bugs o solicitar features, crea un issue en el repositorio.

---

**Desarrollado con ❤️ para DevOps y SRE Teams**
