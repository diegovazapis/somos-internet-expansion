"""
=====================================================================
SOMOS Internet — Expansión Nacional de Red de Fibra Óptica (México)
Sprint 4 Unit Tests — Streamlit Frontend Modules Import Verification
=====================================================================
"""

import pytest
import importlib
import os

def test_logo_file_exists():
    logo_jpg = os.path.join(os.path.dirname(__file__), "logo.jpg")
    logo_gif = os.path.join(os.path.dirname(__file__), "Logo.gif")
    assert os.path.exists(logo_jpg) or os.path.exists(logo_gif)

def test_module_imports():
    modules = [
        "01_architecture",
        "02_planning",
        "03_rollout",
        "04_capacity",
        "05_risk",
        "06_executive",
        "app"
    ]
    for mod_name in modules:
        mod = importlib.import_module(mod_name)
        assert mod is not None
        assert hasattr(mod, "render") or mod_name == "app"
