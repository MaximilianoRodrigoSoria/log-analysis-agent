"""
Configuración centralizada del proyecto log_analyzer.
Lee variables de entorno con defaults razonables.
"""

import os
from pathlib import Path


class Settings:
    """
    Clase de configuración que lee parámetros desde variables de entorno
    con valores por defecto razonables.
    """
    
    def __init__(self):
        # Ollama / LLM
        self.OLLAMA_BASE_URL = os.environ.get(
            "OLLAMA_BASE_URL",
            "http://localhost:11434"
        )
        
        self.OLLAMA_MODEL = os.environ.get(
            "OLLAMA_MODEL",
            "mistral"
        )
        
        # Directorio de salida
        self.OUT_DIR = Path(os.environ.get(
            "OUT_DIR",
            "./out"
        ))
        
        # Nivel de logging
        self.LOG_LEVEL = os.environ.get(
            "LOG_LEVEL",
            "INFO"
        ).upper()
        
        # Timeout para requests HTTP
        self.REQUEST_TIMEOUT_SECONDS = int(os.environ.get(
            "REQUEST_TIMEOUT_SECONDS",
            "120"
        ))
        
        # Endpoint completo de generación de Ollama
        self.OLLAMA_GENERATE_URL = f"{self.OLLAMA_BASE_URL}/api/generate"
        
        # Paths derivados
        self.REPORTS_DIR = self.OUT_DIR / "reports"
        self.ANALYSIS_DIR = self.OUT_DIR / "analysis"
    
    def ensure_output_dirs(self):
        """Crea los directorios de salida si no existen"""
        self.OUT_DIR.mkdir(parents=True, exist_ok=True)
        self.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        self.ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    
    def __repr__(self):
        return (
            f"Settings("
            f"OLLAMA_BASE_URL={self.OLLAMA_BASE_URL}, "
            f"OLLAMA_MODEL={self.OLLAMA_MODEL}, "
            f"OUT_DIR={self.OUT_DIR}, "
            f"LOG_LEVEL={self.LOG_LEVEL}, "
            f"REQUEST_TIMEOUT_SECONDS={self.REQUEST_TIMEOUT_SECONDS})"
        )


# Instancia global por defecto (singleton simple)
settings = Settings()
