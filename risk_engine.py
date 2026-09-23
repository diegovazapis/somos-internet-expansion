"""
=====================================================================
SOMOS Internet — Expansión Nacional de Red de Fibra Óptica (México)
Sprint 2: Business Engine 4 — Risk Engine (risk_engine.py)
=====================================================================
Motor de Evaluación de Riesgos y Gestión de Crisis (Falla 2h Backbone)
"""

import sqlite3
import os

DB_FILE = "somos_network.db"

class RiskEngine:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), DB_FILE)
        self.db_path = db_path

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def get_risk_matrix(self):
        """
        Retorna la matriz completa de riesgos categorizada.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT r.risk_id, r.city_id, c.name, r.category, r.title, r.description,
                   r.severity, r.probability, r.mitigation_strategy, r.impact_score
            FROM risk_events r
            LEFT JOIN cities c ON r.city_id = c.city_id
        """)
        rows = cursor.fetchall()

        matrix = []
        for r_id, city_id, city_name, category, title, desc, severity, prob, mitigation, impact in rows:
            matrix.append({
                "risk_id": r_id,
                "city_id": city_id or "NACIONAL",
                "city_name": city_name or "Nacional",
                "category": category,
                "title": title,
                "description": desc,
                "severity": severity,
                "probability": prob,
                "mitigation_strategy": mitigation,
                "impact_score": impact
            })

        conn.close()
        return matrix

    def simulate_backbone_crisis_protocol_2h(self, affected_link_id="LINK_BB_CDMX_GDL"):
        """
        Escenario 6 del Examen: Simulador del Protocolo de Respuesta en las Primeras 2 Horas
        ante una falla crítica en un tramo del Backbone.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT name, origin_node_id, destination_node_id, distance_km FROM fiber_links WHERE link_id = ?", (affected_link_id,))
        link_info = cursor.fetchone()
        conn.close()

        link_name = link_info[0] if link_info else affected_link_id

        timeline = [
            {
                "minute_range": "0 - 15 min",
                "phase": "Detección & Aislamiento NOC",
                "actions": [
                    f"Alarma OTDR/DWDM disparada en tramo {link_name}.",
                    "Conmutación automática de tráfico a ruta 1+1 redundante vía MTY/Querétaro (< 50ms).",
                    "Aislamiento de la falla e identificación de coordenadas exactas del corte."
                ],
                "status": "CONTROLADO"
            },
            {
                "minute_range": "15 - 45 min",
                "phase": "Despliegue de Cuadrilla & Cadena de Mando",
                "actions": [
                    "Despacho de brigada de empalme de fibra más cercana a la coordenada.",
                    "Notificación a War Room Ejecutivo y Dirección de Operaciones.",
                    "Verificación de niveles de atenuación en ruta protectora."
                ],
                "status": "EN PROGRESO"
            },
            {
                "minute_range": "45 - 90 min",
                "phase": "Reparación Física en Campo",
                "actions": [
                    "Arribo de cuadrilla al sitio de la falla civil.",
                    "Tendido de cable de empalme temporal de emergencia.",
                    "Fusión de hilos de fibra prioritarios para servicios de alta disponibilidad."
                ],
                "status": "EN EJECUCIÓN"
            },
            {
                "minute_range": "90 - 120 min",
                "phase": "Restablecimiento & Comunicación",
                "actions": [
                    "Prueba OTDR de reflectometría confirmada.",
                    "Re-retorno coordinado de tráfico a la ruta principal.",
                    "Emisión de comunicado ejecutivo oficial a clientes Enterprise e IFT."
                ],
                "status": "COMPLETADO"
            }
        ]

        crisis_report = {
            "incident_id": f"INC-BB-{affected_link_id}",
            "affected_link": link_name,
            "sla_availability_target": "99.999%",
            "max_disruption_time_seconds": 0.05, # < 50ms por 1+1
            "timeline_first_2h": timeline
        }

        return crisis_report

if __name__ == "__main__":
    engine = RiskEngine()
    matrix = engine.get_risk_matrix()
    print(f"--- MOTOR DE RIESGOS ({len(matrix)} Registrados) ---")
    for r in matrix:
        print(f"  [{r['category']}] {r['title']} (Severidad: {r['severity']}, Impacto: {r['impact_score']}/10)")
    crisis = engine.simulate_backbone_crisis_protocol_2h()
    print(f"\n--- PROTOCOLO CRISIS FALLA 2H ({crisis['affected_link']}) ---")
    for step in crisis['timeline_first_2h']:
        print(f"  {step['minute_range']} | {step['phase']}: {step['status']}")
