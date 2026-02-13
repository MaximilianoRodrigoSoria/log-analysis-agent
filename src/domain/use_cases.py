"""
Casos de uso del dominio log_analyzer.
Contiene la lógica de negocio principal.
"""

import json
import logging
from typing import Optional
from uuid import uuid4

from .model import LogAnalysis, ReportOutput
from ..ports.log_reader_port import LogReaderPort
from ..ports.analyzer_port import AnalyzerPort
from ..ports.llm_port import LLMPort
from ..ports.report_writer_port import ReportWriterPort
from ..config.settings import settings
from ..config.constants import Constants
from ..config.logging_config import log_with_run_id


logger = logging.getLogger(__name__)


class GenerateReportUseCase:
    """
    Caso de uso principal: Generar reporte de análisis de logs.
    
    Flujo:
    1. Leer logs (desde texto o archivo)
    2. Analizar con analyzer determinista (regex)
    3. Construir prompt robusto para LLM
    4. Llamar a LLM para generar reporte Markdown
    5. Escribir archivos de salida (JSON + MD)
    6. Retornar paths y resumen
    """
    
    def __init__(
        self,
        log_reader: LogReaderPort,
        analyzer: AnalyzerPort,
        llm: LLMPort,
        report_writer: ReportWriterPort
    ):
        self.log_reader = log_reader
        self.analyzer = analyzer
        self.llm = llm
        self.report_writer = report_writer
    
    def execute(
        self,
        log_text: Optional[str] = None,
        log_path: Optional[str] = None,
        run_id: Optional[str] = None
    ) -> ReportOutput:
        """
        Ejecuta el caso de uso completo.
        
        Args:
            log_text: Texto de logs directamente (para API)
            log_path: Path al archivo de logs (para CLI)
            run_id: Identificador único de ejecución (se genera si no se provee)
        
        Returns:
            ReportOutput con paths generados y resumen
        
        Raises:
            ValueError: Si no se provee ni log_text ni log_path
            Exception: Si falla alguna etapa del proceso
        """
        # Generar run_id si no existe
        if run_id is None:
            run_id = self._generate_run_id()
        
        log_with_run_id(logger, logging.INFO, run_id, "Iniciando generación de reporte")
        
        # 1. Obtener texto de logs
        if log_text is None and log_path is None:
            raise ValueError("Debe proveer log_text o log_path")
        
        if log_text is None:
            log_with_run_id(
                logger, 
                logging.INFO, 
                run_id, 
                f"{Constants.LOG_READING_FILE}: {log_path}"
            )
            log_text = self.log_reader.read_log(log_path)
        
        log_with_run_id(
            logger, 
            logging.INFO, 
            run_id, 
            f"Log cargado: {len(log_text)} caracteres"
        )
        
        # 2. Analizar logs con analyzer determinista
        log_with_run_id(logger, logging.INFO, run_id, Constants.LOG_ANALYZING)
        analysis_dict = self.analyzer.analyze(log_text)
        analysis = LogAnalysis(**analysis_dict)
        
        log_with_run_id(
            logger, 
            logging.INFO, 
            run_id, 
            f"{Constants.LOG_ANALYSIS_COMPLETE}: "
            f"{analysis.summary['total_events']} eventos, "
            f"{analysis.summary['total_errors']} errores, "
            f"{analysis.summary['total_warnings']} warnings"
        )
        
        # 3. Construir prompt robusto para LLM
        prompt = self._build_llm_prompt(analysis_dict, log_text)
        
        # 4. Llamar a LLM para generar reporte Markdown
        log_with_run_id(logger, logging.INFO, run_id, Constants.LOG_GENERATING_REPORT)
        report_markdown = self.llm.generate_text(
            prompt=prompt,
            system_prompt=Constants.LLM_SYSTEM_PROMPT
        )
        
        # 5. Escribir archivos de salida
        log_with_run_id(logger, logging.INFO, run_id, Constants.LOG_WRITING_OUTPUT)
        
        # Asegurar que existen los directorios
        settings.ensure_output_dirs()
        
        # Escribir análisis JSON
        analysis_path = self.report_writer.write_analysis(
            run_id=run_id,
            analysis=analysis_dict
        )
        
        # Escribir reporte Markdown
        report_path = self.report_writer.write_report(
            run_id=run_id,
            report_content=report_markdown
        )
        
        log_with_run_id(
            logger, 
            logging.INFO, 
            run_id, 
            f"{Constants.LOG_REPORT_GENERATED}: {report_path}"
        )
        
        # 6. Construir y retornar output
        output = ReportOutput(
            run_id=run_id,
            report_path=report_path,
            analysis_path=analysis_path,
            summary=analysis.summary
        )
        
        return output
    
    def _generate_run_id(self) -> str:
        """Genera un identificador único para la ejecución"""
        return uuid4().hex[:12]
    
    def _build_llm_prompt(self, analysis: dict, log_text: str) -> str:
        """
        Construye el prompt para el LLM incluyendo:
        - Análisis estructurado en JSON
        - Extracto de logs originales
        
        Args:
            analysis: Diccionario con el análisis estructurado
            log_text: Texto original de logs
        
        Returns:
            Prompt formateado para el LLM
        """
        # Serializar análisis a JSON limpio
        analysis_json = json.dumps(analysis, indent=2, ensure_ascii=False)
        
        # Extraer primeras líneas del log (extracto)
        log_lines = log_text.splitlines()
        excerpt_lines = min(30, len(log_lines))
        log_excerpt = "\n".join(log_lines[:excerpt_lines])
        if len(log_lines) > excerpt_lines:
            log_excerpt += f"\n... ({len(log_lines) - excerpt_lines} líneas adicionales)"
        
        # Construir prompt usando template
        prompt = Constants.LLM_USER_PROMPT_TEMPLATE.format(
            analysis_json=analysis_json,
            log_excerpt=log_excerpt
        )
        
        return prompt
