"""
=====================================================================
SOMOS Internet — Expansión Nacional de Red de Fibra Óptica (México)
Sprint 6 Unit Tests — CEO Simulation Mode & Deliverables Verification
=====================================================================
"""

import pytest
import importlib
import os

def test_sprint6_files_exist():
    files = [
        "ceo_simulation.py",
        "executive_demo_guide.md",
        "interview_walkthrough.md"
    ]
    for f in files:
        path = os.path.join(os.path.dirname(__file__), f)
        assert os.path.exists(path)

def test_ceo_simulation_module():
    mod = importlib.import_module("ceo_simulation")
    assert mod is not None
    assert hasattr(mod, "render")

def test_master_app_import():
    app_mod = importlib.import_module("app")
    assert app_mod is not None

def test_ceo_simulation_sliders_present():
    with open(os.path.join(os.path.dirname(__file__), "ceo_simulation.py"), "r", encoding="utf-8") as f:
        code = f.read()
    assert "Ajuste de CAPEX" in code
    assert "Ajuste de OPEX" in code
    assert "Ajuste de ARPU" in code
    assert "Tasa Anual de Churn" in code
    assert "Tasa de Descuento WACC" in code

def test_interview_walkthrough_covers_10_questions():
    with open(os.path.join(os.path.dirname(__file__), "interview_walkthrough.md"), "r", encoding="utf-8") as f:
        content = f.read()
    for q_num in range(1, 11):
        assert f"## {q_num}." in content or f"Pregunta {q_num}" in content or f"Pregunta {q_num}:" in content
    assert "CPHP < $500" in content or "CPHP < \\$500" in content or "500" in content
    assert "VAN" in content
    assert "TIR" in content
    assert "ROI" in content
    assert "payback" in content.lower()

def test_zero_vpn_terminology():
    dir_path = os.path.dirname(__file__)
    target_files = [
        "ceo_simulation.py",
        "executive_demo_guide.md",
        "interview_walkthrough.md",
        "app.py",
        "finance_engine.py",
        "planning_engine.py",
        "capacity_engine.py",
        "risk_engine.py",
        "governance_engine.py",
        "01_architecture.py",
        "02_planning.py",
        "03_rollout.py",
        "04_capacity.py",
        "05_risk.py",
        "06_executive.py",
        "seed_data.py",
        "schema.sql"
    ]
    for filename in target_files:
        filepath = os.path.join(dir_path, filename)
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
                assert "VPN" not in text, f"Found prohibited financial term 'VPN' in {filename}"





