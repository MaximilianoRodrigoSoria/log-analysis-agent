import argparse
from pathlib import Path
from tools.log_analyzer import analyze_log
from tools.report_generator import ReportGenerator


def main():
    """
    Punto de entrada principal del agente orchestrator.

    Lee el archivo de logs, ejecuta análisis estructurado mediante herramienta,
    y genera un reporte profesional en formato Markdown en la carpeta /out.
    """
    parser = argparse.ArgumentParser(
        description="Agente Orchestrator: analiza logs y genera reportes profesionales"
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=Path("datasets/generated_logs.txt"),
        help="Ruta al archivo de logs a analizar (default: datasets/generated_logs.txt)"
    )

    args = parser.parse_args()

    # Validar que el archivo de logs existe
    if not args.log_file.exists():
        print(f"[ERROR] No se encontró el archivo de logs: {args.log_file}")
        return 1

    print(f"[INFO] Leyendo logs desde: {args.log_file}")
    log_text = args.log_file.read_text(encoding="utf-8")

    print(f"[INFO] Log leído correctamente ({len(log_text)} caracteres)")

    # Ejecutar análisis estructurado con la herramienta
    print("[INFO] Analizando estructura del log...")
    analysis = analyze_log(log_text)

    print(f"[INFO] Análisis completado:")
    print(f"  - Total eventos: {analysis['summary']['total_events']}")
    print(f"  - Errores: {analysis['summary']['total_errors']}")
    print(f"  - Warnings: {analysis['summary']['total_warnings']}")
    print(f"  - Grupos de error: {len(analysis['error_groups'])}")

    # Detectar tipos de errores
    error_types = {}
    for group in analysis.get('error_groups', []):
        exc_type = group.get('exception', 'Unknown')
        if exc_type not in error_types:
            error_types[exc_type] = 0
        error_types[exc_type] += group.get('count', 0)

    if error_types:
        print(f"\n[INFO] Tipos de errores detectados:")
        for exc_type, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {exc_type}: {count} ocurrencia(s)")

    # Detectar patrones
    repeated = [g for g in analysis.get('error_groups', []) if g.get('count', 0) > 1]
    if repeated:
        print(f"\n[INFO] Patrones detectados:")
        print(f"  - {len(repeated)} error(es) con múltiples ocurrencias")

    # Generar reporte con ReportGenerator
    print("\n[INFO] Generando reporte en formato Markdown...")
    report_gen = ReportGenerator(output_dir="out")
    report_path = report_gen.generate_report(analysis, log_source=str(args.log_file))

    print(f"\n[OK] ✅ Reporte generado exitosamente: {report_path}")

    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n[WARNING] Proceso interrumpido por el usuario")
        exit(130)
    except Exception as e:
        print(f"[ERROR] Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
