"""
Adapter de escritura de reportes al filesystem.
Implementa ReportWriterPort para escribir archivos locales.
"""

import json
import logging
from pathlib import Path
from typing import Dict

from ..ports.report_writer_port import ReportWriterPort
from ..config.settings import settings
from ..config.constants import Constants


logger = logging.getLogger(__name__)


class FileSystemReportWriter(ReportWriterPort):
    """Escribe reportes y análisis en el filesystem local"""
    
    def __init__(self):
        """Inicializa el writer con configuración de settings"""
        self.reports_dir = settings.REPORTS_DIR
        self.analysis_dir = settings.ANALYSIS_DIR
        
        logger.debug(
            f"FileSystemReportWriter: "
            f"reports={self.reports_dir}, analysis={self.analysis_dir}"
        )
    
    def write_analysis(self, run_id: str, analysis: Dict) -> str:
        """
        Escribe el análisis en formato JSON.
        
        Args:
            run_id: Identificador de la ejecución
            analysis: Diccionario con el análisis
        
        Returns:
            Path absoluto del archivo generado
        """
        # Asegurar que existe el directorio
        self.analysis_dir.mkdir(parents=True, exist_ok=True)
        
        # Construir path del archivo
        filename = f"{run_id}{Constants.ANALYSIS_FILE_EXTENSION}"
        filepath = self.analysis_dir / filename
        
        logger.debug(f"Escribiendo análisis: {filepath}")
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Análisis guardado: {filepath}")
            return str(filepath.resolve())
            
        except Exception as e:
            logger.error(f"Error al escribir análisis: {e}")
            raise IOError(f"{Constants.ERROR_WRITE_FAILED}: {e}") from e
    
    def write_report(self, run_id: str, report_content: str) -> str:
        """
        Escribe el reporte en formato Markdown.
        
        Args:
            run_id: Identificador de la ejecución
            report_content: Contenido del reporte en Markdown
        
        Returns:
            Path absoluto del archivo generado
        """
        # Asegurar que existe el directorio
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Construir path del archivo
        filename = f"{run_id}{Constants.REPORT_FILE_EXTENSION}"
        filepath = self.reports_dir / filename
        
        logger.debug(f"Escribiendo reporte: {filepath}")
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            logger.info(f"Reporte guardado: {filepath}")
            return str(filepath.resolve())
            
        except Exception as e:
            logger.error(f"Error al escribir reporte: {e}")
            raise IOError(f"{Constants.ERROR_WRITE_FAILED}: {e}") from e
