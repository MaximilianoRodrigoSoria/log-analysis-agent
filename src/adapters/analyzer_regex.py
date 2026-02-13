"""
Adapter de análisis de logs usando regex.
Implementa AnalyzerPort con parsing basado en expresiones regulares.
"""

import re
import logging
from typing import List, Dict, Optional

from ..ports.analyzer_port import AnalyzerPort
from ..config.constants import Constants


logger = logging.getLogger(__name__)


# Patrones regex para parsing de logs
HEADER_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\s+"
    r"(?P<level>ERROR|WARN|INFO)\s+\[(?P<thread>[^\]]+)\]\s+"
    r"(?P<logger>[\w\.\$]+)\s+-\s+(?P<message>.*)$"
)

EXC_RE = re.compile(
    r"^(?P<exc>[a-zA-Z0-9\._$]+Exception|Error)(?::\s*(?P<excmsg>.*))?$"
)

FRAME_RE = re.compile(
    r"^\s*at\s+(?P<where>[\w\.\$]+)\((?P<file>[^:]+):(?P<line>\d+)\)\s*$"
)


class RegexLogAnalyzer(AnalyzerPort):
    """Analizador de logs basado en expresiones regulares"""
    
    def analyze(self, log_text: str) -> Dict:
        """
        Parse de logs multilinea:
        - Agrupa entradas por header timestamp+level+logger
        - Si es ERROR/WARN, captura exception (si existe) y top frame
        - Devuelve estructura lista para que el LLM redacte un reporte
        
        Args:
            log_text: Texto completo del log
        
        Returns:
            Diccionario con análisis estructurado
        """
        logger.debug(f"Analizando log de {len(log_text)} caracteres")
        
        lines = log_text.splitlines()
        events: List[Dict] = []
        
        current: Optional[Dict] = None
        stack: List[str] = []
        
        def flush():
            """Procesa el evento acumulado actual"""
            nonlocal current, stack
            if not current:
                return
            
            # Detectar excepción y top frame dentro del bloque acumulado
            exc = None
            excmsg = None
            top_frame = None
            
            for ln in stack:
                m = EXC_RE.match(ln.strip())
                if m and not exc:
                    exc = m.group("exc")
                    excmsg = (m.group("excmsg") or "").strip() or None
                
                fm = FRAME_RE.match(ln)
                if fm and not top_frame:
                    top_frame = {
                        "where": fm.group("where"),
                        "file": fm.group("file"),
                        "line": int(fm.group("line")),
                    }
            
            current["exception"] = exc
            current["exception_message"] = excmsg
            current["top_frame"] = top_frame
            current["raw_block"] = "\n".join(stack).strip() or None
            
            events.append(current)
            current = None
            stack = []
        
        # Parsear línea por línea
        for ln in lines:
            h = HEADER_RE.match(ln)
            if h:
                # Nueva entrada de log encontrada
                flush()
                current = h.groupdict()
                stack = []
            else:
                # Línea suelta asociada al último header (stacktrace u otra info)
                if current is not None:
                    if ln.strip() != "":
                        stack.append(ln)
        
        # Flush final
        flush()
        
        logger.debug(f"Parseados {len(events)} eventos")
        
        # Agregados útiles
        errors = [e for e in events if e["level"] == Constants.LEVEL_ERROR]
        warns = [e for e in events if e["level"] == Constants.LEVEL_WARN]
        
        logger.debug(f"Encontrados {len(errors)} errores y {len(warns)} warnings")
        
        # Agrupar errores por excepción + top frame (si hay)
        groups: Dict[str, Dict] = {}
        for e in errors:
            key = self._make_error_key(e)
            g = groups.setdefault(key, {
                "count": 0,
                "exception": e.get("exception"),
                "top_frame": e.get("top_frame"),
                "logger": e.get("logger"),
                "samples": [],
                "first_ts": e.get("ts"),
                "last_ts": e.get("ts"),
            })
            g["count"] += 1
            g["last_ts"] = e.get("ts")
            if len(g["samples"]) < Constants.MAX_SAMPLES_PER_GROUP:
                g["samples"].append({
                    "ts": e.get("ts"),
                    "message": e.get("message"),
                    "exception_message": e.get("exception_message"),
                })
        
        logger.debug(f"Agrupados en {len(groups)} grupos de errores")
        
        return {
            "summary": {
                "total_events": len(events),
                "total_errors": len(errors),
                "total_warnings": len(warns),
            },
            "error_groups": list(groups.values()),
            "warnings": warns[:Constants.MAX_WARNINGS_IN_ANALYSIS],
            "events": events[:Constants.MAX_EVENTS_IN_ANALYSIS],
        }
    
    def _make_error_key(self, error: Dict) -> str:
        """
        Genera una clave única para agrupar errores similares.
        
        Args:
            error: Diccionario con información del error
        
        Returns:
            String que identifica el grupo de error
        """
        exc = error.get("exception")
        top_frame = error.get("top_frame") or {}
        where = top_frame.get("where")
        line = top_frame.get("line")
        
        return f"{exc}|{where}|{line}"
