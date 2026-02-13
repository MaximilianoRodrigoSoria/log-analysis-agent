"""
Modelos de dominio para log_analyzer.
Entidades y objetos de valor del dominio de análisis de logs.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime


@dataclass
class LogEvent:
    """Representa un evento individual parseado del log"""
    timestamp: str
    level: str
    thread: str
    logger: str
    message: str
    exception: Optional[str] = None
    exception_message: Optional[str] = None
    top_frame: Optional[Dict] = None
    raw_block: Optional[str] = None


@dataclass
class ErrorGroup:
    """Grupo de errores similares (misma excepción + ubicación)"""
    count: int
    exception: Optional[str]
    top_frame: Optional[Dict]
    logger: str
    samples: List[Dict]
    first_ts: str
    last_ts: str


@dataclass
class LogAnalysis:
    """Resultado del análisis estructurado de logs"""
    summary: Dict[str, int]
    error_groups: List[Dict]
    warnings: List[Dict]
    events: List[Dict]
    
    def to_dict(self) -> Dict:
        """Convierte el análisis a diccionario serializable"""
        return {
            "summary": self.summary,
            "error_groups": self.error_groups,
            "warnings": self.warnings,
            "events": self.events
        }


@dataclass
class ReportOutput:
    """Salida del proceso de generación de reporte"""
    run_id: str
    report_path: str
    analysis_path: str
    summary: Dict[str, int]
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """Convierte a diccionario para respuestas API"""
        return {
            "run_id": self.run_id,
            "report_path": self.report_path,
            "analysis_path": self.analysis_path,
            "summary": self.summary,
            "timestamp": self.timestamp.isoformat()
        }
