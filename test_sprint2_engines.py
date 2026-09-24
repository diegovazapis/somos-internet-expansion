"""
=====================================================================
SOMOS Internet — Expansión Nacional de Red de Fibra Óptica (México)
Sprint 2 Unit Tests — Business Engines Verification
=====================================================================
"""

import pytest
import os
from planning_engine import PlanningEngine
from finance_engine import FinanceEngine
from capacity_engine import CapacityEngine
from risk_engine import RiskEngine
from governance_engine import GovernanceEngine

def test_planning_engine():
    engine = PlanningEngine()
    options = engine.evaluate_expansion_options()
    assert "Option_A_Tier1" in options
    assert "Option_B_Tier2" in options
    assert "Option_C_Optimization" in options
    assert options["Option_A_Tier1"]["total_van_mxn"] > 0

def test_finance_engine_van():
    engine = FinanceEngine()
    capex = 10000000.0
    cash_flows = [3000000.0, 3500000.0, 4000000.0, 4500000.0, 5000000.0]
    van = engine.calculate_van(capex, cash_flows, discount_rate=0.075)
    assert van > 0

def test_finance_engine_tir():
    engine = FinanceEngine()
    capex = 10000000.0
    cash_flows = [3000000.0, 3500000.0, 4000000.0, 4500000.0, 5000000.0]
    tir = engine.calculate_tir(capex, cash_flows)
    assert tir > 0.0

def test_finance_engine_cphp_validation():
    engine = FinanceEngine()
    cphp, valid = engine.validate_cphp(4200000.0, 10000)
    assert cphp == 420.0
    assert valid is True

    cphp_fail, valid_fail = engine.validate_cphp(6000000.0, 10000)
    assert cphp_fail == 600.0
    assert valid_fail is False

def test_capacity_engine():
    engine = CapacityEngine()
    cap = engine.analyze_network_capacity(threshold_percent=50.0)
    assert cap["total_nodes_monitored"] == 22
    assert cap["total_links_monitored"] == 15

def test_risk_engine():
    engine = RiskEngine()
    matrix = engine.get_risk_matrix()
    assert len(matrix) == 4
    crisis = engine.simulate_backbone_crisis_protocol_2h()
    assert crisis["sla_availability_target"] == "99.999%"
    assert len(crisis["timeline_first_2h"]) == 4

def test_governance_engine():
    engine = GovernanceEngine()
    cadences = engine.get_governance_cadences()
    assert len(cadences) == 3
    gate = engine.evaluate_capex_approval_gate(20000000.0, "CDMX", "Expansión Polanco")
    assert gate["required_level"] == "STRATEGIC"
