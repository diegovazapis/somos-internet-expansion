"""
=====================================================================
SOMOS Internet — Expansión Nacional de Red de Fibra Óptica (México)
Sprint 2: Business Engine 3 — Capacity Engine (capacity_engine.py)
=====================================================================
Motor de Capacidad, Ocupación de Hilos y Redundancia (1+1 / ERPS)
"""

import sqlite3
import os

DB_FILE = "somos_network.db"

class CapacityEngine:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), DB_FILE)
        self.db_path = db_path

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def analyze_network_capacity(self, threshold_percent=80.0):
        """
        Analiza la capacidad de nodos y la utilización de hilos de fibra óptica.
        Detecta cuellos de botella y verifica redundancia 1+1.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        # 1. Análisis de Capacidad de Nodos
        cursor.execute("""
            SELECT node_id, name, city_id, node_type, total_capacity_gbps, used_capacity_gbps, redundancy_level
            FROM network_nodes
        """)
        node_rows = cursor.fetchall()

        nodes_analysis = []
        node_alerts = []
        for node_id, name, city_id, ntype, total_cap, used_cap, redundancy in node_rows:
            utilization_pct = (used_cap / total_cap) * 100.0 if total_cap > 0 else 0.0
            is_alert = utilization_pct >= threshold_percent

            node_data = {
                "node_id": node_id,
                "name": name,
                "city_id": city_id,
                "node_type": ntype,
                "total_gbps": total_cap,
                "used_gbps": used_cap,
                "utilization_percent": round(utilization_pct, 2),
                "redundancy_level": redundancy,
                "requires_expansion": is_alert
            }
            nodes_analysis.append(node_data)
            if is_alert:
                node_alerts.append(node_data)

        # 2. Análisis de Ocupación de Hilos de Fibra
        cursor.execute("""
            SELECT link_id, name, link_type, distance_km, strand_count, used_strand_count, cfe_pole_agreement, status
            FROM fiber_links
        """)
        link_rows = cursor.fetchall()

        links_analysis = []
        link_alerts = []
        for link_id, name, ltype, dist, total_strands, used_strands, cfe_agrmnt, status in link_rows:
            strand_pct = (used_strands / total_strands) * 100.0 if total_strands > 0 else 0.0
            is_link_alert = strand_pct >= threshold_percent

            link_data = {
                "link_id": link_id,
                "name": name,
                "link_type": ltype,
                "distance_km": dist,
                "total_strands": total_strands,
                "used_strands": used_strands,
                "available_strands": total_strands - used_strands,
                "strand_utilization_percent": round(strand_pct, 2),
                "cfe_pole_agreement": cfe_agrmnt,
                "status": status,
                "requires_strand_expansion": is_link_alert
            }
            links_analysis.append(link_data)
            if is_link_alert:
                link_alerts.append(link_data)

        conn.close()

        summary = {
            "total_nodes_monitored": len(nodes_analysis),
            "total_links_monitored": len(links_analysis),
            "node_high_utilization_alerts": len(node_alerts),
            "link_high_utilization_alerts": len(link_alerts),
            "nodes_detail": nodes_analysis,
            "links_detail": links_analysis
        }
        return summary

if __name__ == "__main__":
    engine = CapacityEngine()
    cap = engine.analyze_network_capacity(threshold_percent=50.0)
    print(f"--- MOTOR DE CAPACIDAD Y REDUNDANCIA ---")
    print(f"Nodos Monitoreados: {cap['total_nodes_monitored']} | Enlaces Monitoreados: {cap['total_links_monitored']}")
    print(f"Alertas de Capacidad Nodos (>50%): {cap['node_high_utilization_alerts']}")
    for n in cap['nodes_detail']:
        print(f"  Nodo {n['name']}: {n['used_gbps']}/{n['total_gbps']} Gbps ({n['utilization_percent']}%) | Redundancia: {n['redundancy_level']}")
