"""
Port para escritura de reportes.
Define la interfaz para persistir análisis y reportes.
"""

from abc import ABC, abstractmethod
from typing import Dict


class ReportWriterPort(ABC):
    """Interfaz para escribir reportes y análisis"""
    
    @abstractmethod
    def write_analysis(self, run_id: str, analysis: Dict) -> str:
        """
        Escribe el análisis estructurado en formato JSON.
        
        Args:
            run_id: Identificador único de la ejecución
            analysis: Diccionario con el análisis
        
        Returns:
            Path del archivo generado
        """
        pass
    
    @abstractmethod
    def write_report(self, run_id: str, report_content: str) -> str:
        """
        Escribe el reporte en formato Markdown.
        
        Args:
            run_id: Identificador único de la ejecución
            report_content: Contenido del reporte en Markdown
        
        Returns:
            Path del archivo generado
        """
        pass
