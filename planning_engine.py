"""
=====================================================================
SOMOS Internet — Expansión Nacional de Red de Fibra Óptica (México)
Sprint 2: Business Engine 1 — Planning Engine (planning_engine.py)
=====================================================================
Motor de Priorización y Evaluación Estratégica de Expansión
(Tier 1 vs Tier 2 vs Optimización de Red Existente)
"""

import sqlite3
import os

DB_FILE = "somos_network.db"

class PlanningEngine:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), DB_FILE)
        self.db_path = db_path

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def evaluate_expansion_options(self, capex_budget_mxn=50000000.0, weight_demand=0.4, weight_cost=0.3, weight_cfe=0.3):
        """
        Evalúa las opciones estratégicas de expansión (Trade-off de Inversión):
        Option A: Expansión Tier 1 (CDMX, MTY, GDL)
        Option B: Expansión Tier 2 (TIJ, MID)
        Option C: Optimización de Red Existente (Expansión de Capacidad)
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT city_id, name, tier_category, demand_index, cfe_availability_ratio, population FROM cities")
        cities = cursor.fetchall()

        city_evaluations = []
        for city_id, name, tier, demand, cfe, pop in cities:
            cursor.execute("""
                SELECT SUM(capex_access_mxn), SUM(homes_passed), AVG(cost_per_home_passed)
                FROM access_clusters WHERE city_id = ?
            """, (city_id,))
            capex_sum, homes_sum, avg_cphp = cursor.fetchone()

            cursor.execute("SELECT van_mxn, irr_percent, roi_percent FROM financial_projections WHERE city_id = ?", (city_id,))
            fin = cursor.fetchone()
            van = fin[0] if fin else 0.0
            irr = fin[1] if fin else 0.0
            roi = fin[2] if fin else 0.0

            # Score Estratégico Normalizado (0 - 100)
            cphp_score = max(0, 100 - (avg_cphp / 500.0) * 50) if avg_cphp else 50.0
            strategic_score = (demand * weight_demand) + (cphp_score * weight_cost) + ((cfe * 100) * weight_cfe)

            city_evaluations.append({
                "city_id": city_id,
                "name": name,
                "tier_category": tier,
                "population": pop,
                "demand_index": demand,
                "cfe_availability_ratio": cfe,
                "homes_passed": homes_sum or 0,
                "avg_cphp_mxn": round(avg_cphp or 0.0, 2),
                "van_mxn": van,
                "irr_percent": irr,
                "roi_percent": roi,
                "strategic_score": round(strategic_score, 2)
            })

        conn.close()

        # Agrupar por Opciones Estratégicas
        tier1_cities = [c for c in city_evaluations if c["tier_category"] == "Tier 1"]
        tier2_cities = [c for c in city_evaluations if c["tier_category"] == "Tier 2"]

        total_van_tier1 = sum(c["van_mxn"] for c in tier1_cities)
        total_van_tier2 = sum(c["van_mxn"] for c in tier2_cities)

        options_summary = {
            "Option_A_Tier1": {
                "name": "Opción A: Expansión Tier 1 (CDMX, MTY, GDL)",
                "description": "Alta densidad comercial, alta competencia, mayor CAPEX inicial, VAN acumulado elevado.",
                "cities": tier1_cities,
                "total_van_mxn": round(total_van_tier1, 2),
                "avg_strategic_score": round(sum(c["strategic_score"] for c in tier1_cities) / len(tier1_cities), 2),
                "risk_profile": "Alto despliegue urbano / Competencia intensa",
                "recommended_focus": "Captura de clientes enterprise y ARPU elevado"
            },
            "Option_B_Tier2": {
                "name": "Opción B: Expansión Tier 2 (Tijuana, Mérida)",
                "description": "Crecimiento acelerado, menor competencia, rápida adopción, excelente ROI relativo.",
                "cities": tier2_cities,
                "total_van_mxn": round(total_van_tier2, 2),
                "avg_strategic_score": round(sum(c["strategic_score"] for c in tier2_cities) / len(tier2_cities), 2),
                "risk_profile": "Permisos locales / Crecimiento de infraestructura",
                "recommended_focus": "Rápido payback y expansión de cobertura geográfica"
            },
            "Option_C_Optimization": {
                "name": "Opción C: Optimización de Red Existente",
                "description": "Menor CAPEX incremental, incremento de densidad de suscriptores en nodos activos.",
                "cities": city_evaluations,
                "total_van_mxn": round((total_van_tier1 + total_van_tier2) * 0.4, 2),
                "avg_strategic_score": 85.0,
                "risk_profile": "Bajo riesgo operacional",
                "recommended_focus": "Maximizacion de margen EBITDA y conversión de casas pasadas a clientes activos"
            }
        }

        return options_summary

if __name__ == "__main__":
    engine = PlanningEngine()
    evals = engine.evaluate_expansion_options()
    print("--- EVALUACIÓN ESTRATÉGICA DE PLANIFICACIÓN ---")
    for opt_key, opt_data in evals.items():
        print(f"\n{opt_data['name']}")
        print(f"  VAN Total: ${opt_data['total_van_mxn']:,.2f} MXN | Score Promedio: {opt_data['avg_strategic_score']}")
