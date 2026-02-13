import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class ReportGenerator:
    """
    Generador de reportes en formato Markdown a partir del análisis de logs.
    Identifica tipos de errores, patrones y genera salida en /out
    """
    
    def __init__(self, output_dir: str = "out"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_report(self, analysis: Dict, log_source: str = "unknown") -> str:
        """
        Genera reporte MD a partir del análisis de logs.
        Retorna la ruta del archivo generado.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"log_analysis_{timestamp}.md"
        filepath = self.output_dir / filename
        
        # Construir contenido del reporte
        content = self._build_markdown(analysis, log_source)
        
        # Escribir archivo
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filepath)
    
    def _build_markdown(self, analysis: Dict, log_source: str) -> str:
        """Construye el contenido Markdown del reporte"""
        lines = []
        
        # Header
        lines.append("# 📊 Reporte de Análisis de Logs")
        lines.append("")
        lines.append(f"**Fuente:** `{log_source}`  ")
        lines.append(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Resumen ejecutivo
        summary = analysis.get("summary", {})
        lines.append("## 📈 Resumen Ejecutivo")
        lines.append("")
        lines.append(f"- **Total de eventos:** {summary.get('total_events', 0)}")
        lines.append(f"- **Errores (ERROR):** {summary.get('total_errors', 0)}")
        lines.append(f"- **Advertencias (WARN):** {summary.get('total_warnings', 0)}")
        lines.append("")
        
        # Tipos de errores encontrados
        error_groups = analysis.get("error_groups", [])
        if error_groups:
            lines.append("## 🔴 Tipos de Errores Encontrados")
            lines.append("")
            
            # Extraer tipos únicos de excepciones
            exception_types = {}
            for group in error_groups:
                exc_type = group.get("exception") or "Unknown"
                if exc_type not in exception_types:
                    exception_types[exc_type] = 0
                exception_types[exc_type] += group.get("count", 0)
            
            lines.append("### Distribución por Tipo de Excepción")
            lines.append("")
            for exc_type, count in sorted(exception_types.items(), key=lambda x: x[1], reverse=True):
                lines.append(f"- **{exc_type}**: {count} ocurrencia(s)")
            lines.append("")
        
        # Análisis de patrones
        lines.append("## 🔍 Análisis de Patrones")
        lines.append("")
        
        if error_groups:
            patterns = self._detect_patterns(error_groups)
            
            if patterns.get("repeated_errors"):
                lines.append("### ⚠️ Errores Repetitivos")
                lines.append("")
                lines.append("Los siguientes errores se repiten múltiples veces:")
                lines.append("")
                for pattern in patterns["repeated_errors"]:
                    lines.append(f"#### {pattern['exception']} (x{pattern['count']})")
                    lines.append("")
                    lines.append(f"- **Ubicación:** `{pattern['location']}`")
                    lines.append(f"- **Primera ocurrencia:** {pattern['first_ts']}")
                    lines.append(f"- **Última ocurrencia:** {pattern['last_ts']}")
                    if pattern.get('sample_message'):
                        lines.append(f"- **Mensaje:** {pattern['sample_message']}")
                    lines.append("")
            
            if patterns.get("hotspots"):
                lines.append("### 🔥 Hotspots (Componentes más afectados)")
                lines.append("")
                for hotspot in patterns["hotspots"]:
                    lines.append(f"- **{hotspot['logger']}**: {hotspot['count']} error(es)")
                lines.append("")
            
            if patterns.get("timeframe"):
                lines.append("### ⏱️ Ventana Temporal")
                lines.append("")
                tf = patterns["timeframe"]
                lines.append(f"- **Primer error:** {tf['first']}")
                lines.append(f"- **Último error:** {tf['last']}")
                lines.append("")
        else:
            lines.append("No se detectaron patrones significativos.")
            lines.append("")
        
        # Detalle de grupos de errores
        if error_groups:
            lines.append("## 📋 Detalle de Grupos de Errores")
            lines.append("")
            
            # Ordenar por count descendente
            sorted_groups = sorted(error_groups, key=lambda x: x.get("count", 0), reverse=True)
            
            for idx, group in enumerate(sorted_groups[:10], 1):  # Top 10
                exc = group.get("exception") or "Unknown"
                count = group.get("count", 0)
                
                lines.append(f"### {idx}. {exc} ({count}x)")
                lines.append("")
                
                top_frame = group.get("top_frame")
                if top_frame:
                    lines.append(f"**Stack trace:**")
                    lines.append(f"```")
                    lines.append(f"at {top_frame['where']}({top_frame['file']}:{top_frame['line']})")
                    lines.append(f"```")
                    lines.append("")
                
                lines.append(f"**Logger:** `{group.get('logger', 'N/A')}`  ")
                lines.append(f"**Rango temporal:** {group.get('first_ts')} → {group.get('last_ts')}")
                lines.append("")
                
                samples = group.get("samples", [])
                if samples:
                    lines.append("**Muestras:**")
                    lines.append("")
                    for sample in samples:
                        lines.append(f"- `[{sample['ts']}]` {sample['message']}")
                        if sample.get('exception_message'):
                            lines.append(f"  - Detalle: *{sample['exception_message']}*")
                    lines.append("")
        
        # Advertencias
        warnings = analysis.get("warnings", [])
        if warnings:
            lines.append("## ⚡ Advertencias (WARN)")
            lines.append("")
            for warn in warnings[:5]:  # Top 5
                lines.append(f"- `[{warn['ts']}]` **{warn['logger']}**: {warn['message']}")
            lines.append("")
        
        # Footer
        lines.append("---")
        lines.append("")
        lines.append("*Reporte generado automáticamente por Log Analyzer Tool*")
        
        return "\n".join(lines)
    
    def _detect_patterns(self, error_groups: List[Dict]) -> Dict:
        """Detecta patrones en los grupos de errores"""
        patterns = {
            "repeated_errors": [],
            "hotspots": [],
            "timeframe": {}
        }
        
        # Errores repetitivos (count > 1)
        for group in error_groups:
            if group.get("count", 0) > 1:
                top_frame = group.get("top_frame") or {}
                location = f"{top_frame.get('where', 'N/A')}:{top_frame.get('line', '?')}"
                
                sample_msg = None
                samples = group.get("samples", [])
                if samples:
                    sample_msg = samples[0].get("exception_message")
                
                patterns["repeated_errors"].append({
                    "exception": group.get("exception", "Unknown"),
                    "count": group.get("count"),
                    "location": location,
                    "first_ts": group.get("first_ts"),
                    "last_ts": group.get("last_ts"),
                    "sample_message": sample_msg
                })
        
        # Hotspots: componentes (loggers) con más errores
        logger_counts = {}
        for group in error_groups:
            logger = group.get("logger", "Unknown")
            count = group.get("count", 0)
            logger_counts[logger] = logger_counts.get(logger, 0) + count
        
        patterns["hotspots"] = [
            {"logger": logger, "count": count}
            for logger, count in sorted(logger_counts.items(), key=lambda x: x[1], reverse=True)
        ][:5]  # Top 5
        
        # Timeframe
        all_timestamps = []
        for group in error_groups:
            if group.get("first_ts"):
                all_timestamps.append(group["first_ts"])
            if group.get("last_ts"):
                all_timestamps.append(group["last_ts"])
        
        if all_timestamps:
            patterns["timeframe"] = {
                "first": min(all_timestamps),
                "last": max(all_timestamps)
            }
        
        return patterns
