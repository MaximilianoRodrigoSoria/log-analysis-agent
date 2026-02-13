"""
Entrypoint API (Flask) para log_analyzer.
Expone endpoint REST para análisis de logs con Swagger UI.

ADVERTENCIA DE SEGURIDAD:
⚠️ Esta API NO tiene autenticación implementada.
⚠️ NO expongas esto en producción sin agregar autenticación/autorización.
⚠️ Riesgo de prompt injection si los logs contienen contenido malicioso.

Uso:
    python app/api.py
    
    # Swagger UI disponible en:
    http://localhost:8080/apidocs
"""

import sys
from pathlib import Path

# Agregar el directorio raíz al path para importar src
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, request, jsonify, send_file
from flasgger import Swagger, swag_from
import logging

from src.config.logging_config import setup_logging
from src.config.settings import settings
from src.config.constants import Constants
from src.domain.use_cases import GenerateReportUseCase
from src.adapters.log_reader_fs import FileSystemLogReader
from src.adapters.analyzer_regex import RegexLogAnalyzer
from src.adapters.llm_ollama import OllamaLLM
from src.adapters.report_writer_fs import FileSystemReportWriter


# Configurar logging
setup_logging()
logger = logging.getLogger(__name__)

# Crear app Flask
app = Flask(__name__)

# Configurar Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs"
}

swagger_template = {
    "swagger": "2.0",
    "info": {
        "title": "Log Analyzer API",
        "description": "API REST para análisis automático de logs con LLM (Ollama)",
        "version": "1.0.0",
        "contact": {
            "name": "Log Analyzer",
            "url": "https://github.com/log-analyzer"
        }
    },
    "host": "localhost:8080",
    "basePath": "/",
    "schemes": ["http"],
    "securityDefinitions": {
        "APIKeyHeader": {
            "type": "apiKey",
            "name": "X-API-Key",
            "in": "header",
            "description": "API Key (no implementado aún)"
        }
    }
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Componer dependencias (singleton para la app)
log_reader = FileSystemLogReader()
analyzer = RegexLogAnalyzer()
llm = OllamaLLM()
report_writer = FileSystemReportWriter()

use_case = GenerateReportUseCase(
    log_reader=log_reader,
    analyzer=analyzer,
    llm=llm,
    report_writer=report_writer
)


@app.route("/", methods=["GET"])
def index():
    """
    Información de la API
    ---
    tags:
      - Info
    responses:
      200:
        description: Información del servicio
        schema:
          type: object
          properties:
            service:
              type: string
              example: log_analyzer
            version:
              type: string
              example: 1.0.0
            swagger_ui:
              type: string
              example: http://localhost:8080/apidocs
    """
    return jsonify({
        "service": "log_analyzer",
        "version": "1.0.0",
        "swagger_ui": "http://localhost:8080/apidocs",
        "endpoints": {
            "/datasets": "GET - Lista archivos de logs disponibles",
            "/analyze": "POST - Analiza logs y genera reporte"
        },
        "config": {
            "ollama_model": settings.OLLAMA_MODEL,
            "ollama_url": settings.OLLAMA_BASE_URL,
            "output_dir": str(settings.OUT_DIR)
        }
    })


@app.route("/datasets", methods=["GET"])
def list_datasets():
    """
    Lista archivos de logs disponibles
    ---
    tags:
      - Datasets
    responses:
      200:
        description: Lista de archivos .txt en datasets/
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            datasets:
              type: array
              items:
                type: string
              example: ["generated_logs.txt", "app_errors.txt"]
            count:
              type: integer
              example: 2
    """
    try:
        # Path absoluto al directorio datasets
        datasets_dir = Path(__file__).parent.parent / "datasets"
        
        if not datasets_dir.exists():
            return jsonify({
                Constants.API_RESPONSE_STATUS: Constants.STATUS_ERROR,
                Constants.API_RESPONSE_ERROR: "Directorio datasets/ no existe"
            }), 404
        
        # Listar archivos .txt
        files = [f.name for f in datasets_dir.glob("*.txt")]
        files.sort()
        
        return jsonify({
            Constants.API_RESPONSE_STATUS: Constants.STATUS_SUCCESS,
            "datasets": files,
            "count": len(files)
        }), 200
        
    except Exception as e:
        logger.error(f"Error al listar datasets: {e}")
        return jsonify({
            Constants.API_RESPONSE_STATUS: Constants.STATUS_ERROR,
            Constants.API_RESPONSE_ERROR: str(e)
        }), 500


@app.route(Constants.API_ENDPOINT_ANALYZE, methods=["POST"])
def analyze():
    """
    Analiza logs y genera reporte completo en Markdown
    ---
    tags:
      - Análisis
    parameters:
      - in: body
        name: body
        required: true
        description: Solicitud de análisis de logs
        schema:
          type: object
          required:
            - log_filename
          properties:
            log_filename:
              type: string
              description: Nombre del archivo .txt en datasets/
              example: generated_logs.txt
            run_id:
              type: string
              description: Nombre del archivo de salida (requerido)
              example: mi-analisis-001
        examples:
          ejemplo_basico:
            summary: Análisis básico
            value:
              log_filename: generated_logs.txt
          ejemplo_con_id:
            summary: Análisis con run_id personalizado
            value:
              log_filename: generated_logs.txt
              run_id: produccion-2026-02-13
    responses:
      200:
        description: Descarga directa del archivo de reporte en Markdown
        content:
          text/markdown:
            schema:
              type: string
              format: binary
      400:
        description: Error de validación en la solicitud
        schema:
          type: object
          properties:
            status:
              type: string
              example: error
            error:
              type: string
              example: Campo 'log_filename' es requerido
        examples:
          sin_filename:
            summary: Falta log_filename
            value:
              status: error
              error: Campo 'log_filename' es requerido
      404:
        description: Archivo de log no encontrado
        schema:
          type: object
          properties:
            status:
              type: string
              example: error
            error:
              type: string
              example: Archivo 'app.log' no existe en datasets/
      503:
        description: No se puede conectar a Ollama
        schema:
          type: object
          properties:
            status:
              type: string
              example: error
            error:
              type: string
              example: No se puede conectar a Ollama en http://localhost:11434
      504:
        description: Timeout al procesar el request
        schema:
          type: object
          properties:
            status:
              type: string
              example: error
            error:
              type: string
              example: Timeout después de 120s al procesar request
    """
    try:
        # Validar Content-Type
        if not request.is_json:
            return jsonify({
                Constants.API_RESPONSE_STATUS: Constants.STATUS_ERROR,
                Constants.API_RESPONSE_ERROR: "Content-Type debe ser application/json"
            }), 400
        
        # Obtener datos del request
        data = request.get_json()
        
        # Validar campo requerido: log_filename
        log_filename = data.get("log_filename")
        if not log_filename:
            return jsonify({
                Constants.API_RESPONSE_STATUS: Constants.STATUS_ERROR,
                Constants.API_RESPONSE_ERROR: "Campo 'log_filename' es requerido"
            }), 400
        
        # run_id requerido - será el nombre del archivo de salida
        run_id = data.get(Constants.API_FIELD_RUN_ID)
        if not run_id:
            return jsonify({
                Constants.API_RESPONSE_STATUS: Constants.STATUS_ERROR,
                Constants.API_RESPONSE_ERROR: "Campo 'run_id' es requerido"
            }), 400
        
        # Construir path absoluto al archivo
        datasets_dir = Path(__file__).parent.parent / "datasets"
        log_path = datasets_dir / log_filename
        
        if not log_path.exists():
            return jsonify({
                Constants.API_RESPONSE_STATUS: Constants.STATUS_ERROR,
                Constants.API_RESPONSE_ERROR: f"Archivo '{log_filename}' no existe en datasets/"
            }), 404
        
        logger.info(f"Recibido request de análisis (log_filename: {log_filename}, run_id: {run_id})")
        
        # Ejecutar caso de uso
        result = use_case.execute(
            log_path=str(log_path),
            run_id=run_id
        )
        
        logger.info(f"Análisis completado exitosamente: run_id={result.run_id}")
        
        # Retornar el archivo Markdown directamente para descarga
        return send_file(
            result.report_path,
            mimetype='text/markdown',
            as_attachment=True,
            download_name=f"{result.run_id}.md"
        )
        
    except ValueError as e:
        logger.error(f"Error de validación: {e}")
        return jsonify({
            Constants.API_RESPONSE_STATUS: Constants.STATUS_ERROR,
            Constants.API_RESPONSE_ERROR: str(e)
        }), 400
        
    except ConnectionError as e:
        logger.error(f"Error de conexión: {e}")
        return jsonify({
            Constants.API_RESPONSE_STATUS: Constants.STATUS_ERROR,
            Constants.API_RESPONSE_ERROR: f"No se puede conectar a Ollama: {e}"
        }), 503
        
    except TimeoutError as e:
        logger.error(f"Timeout: {e}")
        return jsonify({
            Constants.API_RESPONSE_STATUS: Constants.STATUS_ERROR,
            Constants.API_RESPONSE_ERROR: f"Timeout al procesar request: {e}"
        }), 504
        
    except Exception as e:
        logger.error(f"Error inesperado: {e}", exc_info=True)
        return jsonify({
            Constants.API_RESPONSE_STATUS: Constants.STATUS_ERROR,
            Constants.API_RESPONSE_ERROR: f"Error interno del servidor: {str(e)}"
        }), 500


@app.route("/health", methods=["GET"])
def health():
    """
    Health check
    ---
    tags:
      - Info
    responses:
      200:
        description: Servicio saludable
        schema:
          type: object
          properties:
            status:
              type: string
              example: healthy
            ollama_url:
              type: string
              example: http://localhost:11434
            model:
              type: string
              example: mistral
    """
    return jsonify({
        "status": "healthy",
        "ollama_url": settings.OLLAMA_BASE_URL,
        "model": settings.OLLAMA_MODEL
    }), 200


def main():
    """Inicia el servidor Flask"""
    print("=" * 60)
    print("  Log Analyzer API")
    print("=" * 60)
    print()
    print(f"  Ollama URL: {settings.OLLAMA_BASE_URL}")
    print(f"  Modelo: {settings.OLLAMA_MODEL}")
    print(f"  Output: {settings.OUT_DIR}")
    print()
    print(f"  ⚠️  {Constants.SECURITY_WARNING_API}")
    print(f"  ⚠️  {Constants.SECURITY_WARNING_PROMPT_INJECTION}")
    print()
    print("=" * 60)
    print()
    print("Endpoints disponibles:")
    print("  GET  /           - Info de la API")
    print("  GET  /health     - Health check")
    print("  GET  /datasets   - Listar archivos disponibles")
    print("  POST /analyze    - Analizar logs")
    print()
    print("Swagger UI: http://localhost:8080/apidocs")
    print("Iniciando servidor en http://0.0.0.0:8080")
    print()
    
    # Iniciar servidor
    app.run(
        host="0.0.0.0",
        port=8080,
        debug=False
    )


if __name__ == "__main__":
    main()
