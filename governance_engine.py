"""
=====================================================================
SOMOS Internet — Expansión Nacional de Red de Fibra Óptica (México)
Sprint 2: Business Engine 5 — Governance Engine (governance_engine.py)
=====================================================================
Motor de Gobernanza, Cadencias de Control y Flujo de Aprobación CAPEX
"""

import sqlite3
import os

DB_FILE = "somos_network.db"

class GovernanceEngine:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), DB_FILE)
        self.db_path = db_path

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def get_governance_cadences(self):
        """
        Retorna los niveles de gobernanza y cadencias de seguimiento.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT cadence_id, level, forum_name, frequency, participants, kpis_reviewed FROM governance_cadences")
        rows = cursor.fetchall()

        cadences = []
        for c_id, level, forum, freq, participants, kpis in rows:
            cadences.append({
                "cadence_id": c_id,
                "level": level,
                "forum_name": forum,
                "frequency": freq,
                "participants": participants,
                "kpis_reviewed": kpis
            })

        conn.close()
        return cadences

    def evaluate_capex_approval_gate(self, capex_amount_mxn, city_id, project_name):
        """
        Determina el nivel de gobernanza requerido para aprobar un proyecto de expansión según su monto de CAPEX.
        """
        if capex_amount_mxn >= 15000000.0:
            required_forum = "Comité Ejecutivo de Expansión de Red (Board Executive)"
            required_level = "STRATEGIC"
            approvers = ["CEO", "VP Redes", "VP Finanzas"]
            approval_type = "Aprobación Estratégica de Junta Directiva"
        elif capex_amount_mxn >= 5000000.0:
            required_forum = "War Room Semanal de Despliegue & CFE"
            required_level = "OPERATIONAL"
            approvers = ["Director de Despliegue", "Gerente Regional de Red"]
            approval_type = "Aprobación Operativa Regional"
        else:
            required_forum = "Comité de Resiliencia & Operación Local"
            required_level = "TACTICAL"
            approvers = ["Jefe de Proyecto Local"]
            approval_type = "Aprobación Táctica Local"

        return {
            "project_name": project_name,
            "city_id": city_id,
            "capex_amount_mxn": round(capex_amount_mxn, 2),
            "required_level": required_level,
            "required_forum": required_forum,
            "approvers": approvers,
            "approval_type": approval_type,
            "status": "GATE_READY_FOR_SUBMISSION"
        }

if __name__ == "__main__":
    engine = GovernanceEngine()
    cadences = engine.get_governance_cadences()
    print(f"--- MOTOR DE GOBERNANZA ({len(cadences)} Cadencias) ---")
    for c in cadences:
        print(f"  [{c['level']}] {c['forum_name']} ({c['frequency']})")
    gate = engine.evaluate_capex_approval_gate(22500000.0, "CDMX", "Expansión Cluster Residencial Polanco")
    print(f"\n--- EVALUACIÓN GATE CAPEX ---")
    print(f"Proyecto: {gate['project_name']} (${gate['capex_amount_mxn']:,.2f} MXN)")
    print(f"Nivel Requerido: {gate['required_level']} -> {gate['required_forum']}")
