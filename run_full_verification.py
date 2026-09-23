"""
=====================================================================
SOMOS Internet — Expansión Nacional de Red de Fibra Óptica (México)
Sprint 5: Full Verification Suite Runner (run_full_verification.py)
=====================================================================
"""

import pytest
import sys
import os

def run_all_tests():
    test_files = [
        "test_sprint1_deliverables.py",
        "test_sprint2_engines.py",
        "test_sprint3_gis.py",
        "test_sprint4_frontend.py",
        "test_sprint6_ceo_simulation.py"
    ]

    print("=====================================================================")
    print("EJECUTANDO SUITE COMPLETA DE PRUEBAS AUTOMATIZADAS — SPRINT 6")
    print("=====================================================================")

    exit_code = int(pytest.main(["-v"] + test_files))
    if exit_code == 0:
        print("\n[OK] TODAS LAS PRUEBAS AUTOMATIZADAS HAN PASADO CON EXITO (100% PASS).")
    else:
        print(f"\n[FAIL] SE DETECTARON FALLOS EN LA SUITE DE PRUEBAS. CODIGO DE SALIDA: {exit_code}")
    return exit_code

if __name__ == "__main__":
    sys.exit(run_all_tests())
