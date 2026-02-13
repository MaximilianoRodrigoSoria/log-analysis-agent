#!/usr/bin/env python
"""Script de prueba para verificar que log_analyzer.py lee correctamente el archivo de logs."""

from pathlib import Path
from tools.log_analyzer import analyze_log

def test_analyzer():
    log_file = Path("datasets/generated_logs.txt")

    if not log_file.exists():
        print(f"[ERROR] No existe el archivo: {log_file}")
        return 1

    print(f"[INFO] Leyendo logs desde: {log_file}")
    log_text = log_file.read_text(encoding="utf-8")
    print(f"[INFO] Log leído: {len(log_text)} caracteres")

    print("[INFO] Analizando logs...")
    analysis = analyze_log(log_text)

    print("\n=== RESULTADOS DEL ANÁLISIS ===")
    print(f"Total eventos: {analysis['summary']['total_events']}")
    print(f"Errores: {analysis['summary']['total_errors']}")
    print(f"Warnings: {analysis['summary']['total_warnings']}")
    print(f"Grupos de error: {len(analysis['error_groups'])}")

    print("\n=== GRUPOS DE ERROR ===")
    for i, group in enumerate(analysis['error_groups'][:5], 1):
        print(f"\n{i}. {group.get('exception', 'N/A')}")
        print(f"   Ocurrencias: {group['count']}")
        print(f"   Logger: {group.get('logger', 'N/A')}")
        if group.get('top_frame'):
            frame = group['top_frame']
            print(f"   Ubicación: {frame['where']} ({frame['file']}:{frame['line']})")

    print("\n[OK] Análisis completado exitosamente")
    return 0

if __name__ == "__main__":
    exit(test_analyzer())

