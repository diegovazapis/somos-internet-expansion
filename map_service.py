"""
=====================================================================
SOMOS Internet — Expansión Nacional de Red de Fibra Óptica (México)
Sprint 3: GIS Layer — Map Service (map_service.py)
=====================================================================
Servicio de Procesamiento Geoespacial y GeoJSON para PyDeck / Streamlit
"""

import sqlite3
import json
import os
import math

DB_FILE = "somos_network.db"

# Coordenadas y Viewport por Defecto para las 5 Ciudades (Vista 2D Limpia sobre Carreteras)
CITY_VIEWPORTS = {
    "MEXICO": {"latitude": 23.6345, "longitude": -102.5528, "zoom": 4.8, "pitch": 0.0},
    "CDMX": {"latitude": 19.4126, "longitude": -99.1732, "zoom": 11.2, "pitch": 0.0},
    "MTY": {"latitude": 25.6866, "longitude": -100.3561, "zoom": 11.2, "pitch": 0.0},
    "GDL": {"latitude": 20.6897, "longitude": -103.3696, "zoom": 11.2, "pitch": 0.0},
    "TIJ": {"latitude": 32.5149, "longitude": -117.0382, "zoom": 11.2, "pitch": 0.0},
    "MID": {"latitude": 20.9876, "longitude": -89.5926, "zoom": 11.2, "pitch": 0.0},
}

class MapService:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), DB_FILE)
        self.db_path = db_path

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def get_viewport_for_city(self, city_id="MEXICO"):
        """
        Retorna el estado de viewport de PyDeck para la ciudad seleccionada.
        """
        return CITY_VIEWPORTS.get(city_id.upper(), CITY_VIEWPORTS["MEXICO"])

    def get_nodes_gis_data(self, city_id=None):
        """
        Retorna datos de nodos formateados para capas de puntos/columnas en PyDeck.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if city_id and city_id.upper() != "MEXICO":
            cursor.execute("""
                SELECT n.node_id, n.name, n.city_id, c.name, n.node_type, n.latitude, n.longitude,
                       n.total_capacity_gbps, n.used_capacity_gbps, n.redundancy_level, n.status
                FROM network_nodes n
                JOIN cities c ON n.city_id = c.city_id
                WHERE n.city_id = ?
            """, (city_id.upper(),))
        else:
            cursor.execute("""
                SELECT n.node_id, n.name, n.city_id, c.name, n.node_type, n.latitude, n.longitude,
                       n.total_capacity_gbps, n.used_capacity_gbps, n.redundancy_level, n.status
                FROM network_nodes n
                JOIN cities c ON n.city_id = c.city_id
            """)
        rows = cursor.fetchall()
        conn.close()

        nodes = []
        for n_id, name, c_id, c_name, ntype, lat, lon, total_cap, used_cap, redundancy, status in rows:
            utilization_pct = (used_cap / total_cap) * 100.0 if total_cap > 0 else 0.0
            
            # Color por tipo de nodo (RGB) - Estilo SOMOS Internet Colombia
            if ntype == "NATIONAL_POP":
                color = [230, 57, 70] # Rojo Neón POP Nacional
                elevation = 0.0
                radius = 1800
            elif ntype == "METRO_CORE":
                color = [58, 134, 255] # Azul Eléctrico Core Metro
                elevation = 0.0
                radius = 1200
            elif ntype == "MICRO_POP":
                color = [0, 245, 212] # Cian Neón MicroPOP Descentralizado SOMOS Colombia
                elevation = 0.0
                radius = 800
            else:
                color = [42, 157, 143] # Verde Mar
                elevation = 0.0
                radius = 800

            nodes.append({
                "node_id": n_id,
                "name": name,
                "city_id": c_id,
                "city_name": c_name,
                "node_type": ntype,
                "latitude": lat,
                "longitude": lon,
                "coordinates": [lon, lat],
                "total_capacity_gbps": total_cap,
                "used_capacity_gbps": used_cap,
                "utilization_percent": round(utilization_pct, 1),
                "redundancy_level": redundancy,
                "status": status,
                "color": color,
                "elevation": elevation,
                "tooltip_line1": f"Tipo: {ntype} | Ciudad: {c_name}",
                "tooltip_line2": f"Capacidad: {total_cap:,} Gbps | Uso: {round(utilization_pct, 1)}% ({used_cap:,} Gbps) | Redundancia: {redundancy}"
            })
        return nodes

    def get_fiber_links_gis_data(self, city_id=None, link_type_filter=None):
        """
        Retorna los tramos de fibra óptica formateados para PathLayer / LineLayer de PyDeck.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        query = """
            SELECT f.link_id, f.name, f.city_id, f.link_type, f.distance_km, f.strand_count,
                   f.used_strand_count, f.cfe_pole_agreement, f.deployment_cost_mxn, f.geojson_geometry, f.status
            FROM fiber_links f
        """
        conditions = []
        params = []

        if city_id and city_id.upper() != "MEXICO":
            conditions.append("(f.city_id = ? OR f.link_type = 'BACKBONE_LONG_HAUL')")
            params.append(city_id.upper())

        if link_type_filter:
            conditions.append("f.link_type = ?")
            params.append(link_type_filter)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()

        links = []
        for l_id, name, c_id, ltype, dist, strands, used_strands, cfe_agrmnt, cost, geojson_str, status in rows:
            geo = json.loads(geojson_str)
            path_coords = geo.get("coordinates", [])

            # Color y ancho de trazo por tipo de enlace
            if ltype == "BACKBONE_LONG_HAUL":
                color = [255, 183, 3] # Amarillo Neón Larga Distancia
                width = 8
            elif ltype == "METRO_RING":
                color = [0, 180, 216] # Cian Anillo Metro
                width = 5
            else:
                color = [144, 224, 239] # Azul Claro Acceso
                width = 3

            strand_pct = (used_strands / strands) * 100.0 if strands > 0 else 0.0

            links.append({
                "link_id": l_id,
                "name": name,
                "city_id": c_id or "NACIONAL",
                "link_type": ltype,
                "distance_km": dist,
                "strand_count": strands,
                "used_strand_count": used_strands,
                "strand_utilization_percent": round(strand_pct, 1),
                "cfe_pole_agreement": cfe_agrmnt,
                "deployment_cost_mxn": cost,
                "path": path_coords,
                "status": status,
                "color": color,
                "width": width,
                "tooltip_line1": f"Tipo: {ltype} | Ámbito: {c_id or 'NACIONAL'} | Distancia: {dist:,} km",
                "tooltip_line2": f"Hilos: {used_strands}/{strands} ({round(strand_pct, 1)}%) | Convenio CFE: {cfe_agrmnt}"
            })
        return links

    def get_access_clusters_gis_data(self, city_id=None):
        """
        Retorna los bloques de acceso y casas pasadas para capas de disperse puntos/scatter en PyDeck.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if city_id and city_id.upper() != "MEXICO":
            cursor.execute("""
                SELECT a.cluster_id, a.city_id, c.name, a.name, a.homes_passed, a.active_subscribers,
                       a.arpu_monthly_mxn, a.capex_access_mxn, a.cost_per_home_passed, a.latitude, a.longitude
                FROM access_clusters a
                JOIN cities c ON a.city_id = c.city_id
                WHERE a.city_id = ?
            """, (city_id.upper(),))
        else:
            cursor.execute("""
                SELECT a.cluster_id, a.city_id, c.name, a.name, a.homes_passed, a.active_subscribers,
                       a.arpu_monthly_mxn, a.capex_access_mxn, a.cost_per_home_passed, a.latitude, a.longitude
                FROM access_clusters a
                JOIN cities c ON a.city_id = c.city_id
            """)
        rows = cursor.fetchall()
        conn.close()

        clusters = []
        for clus_id, c_id, c_name, name, homes, subs, arpu, capex, cphp, lat, lon in rows:
            penetration_pct = (subs / homes) * 100.0 if homes > 0 else 0.0
            
            # CPHP indicador de color
            if cphp <= 450.0:
                color = [46, 196, 182] # Verde excelente
            else:
                color = [255, 159, 28] # Naranja neutro

            clusters.append({
                "cluster_id": clus_id,
                "city_id": c_id,
                "city_name": c_name,
                "name": name,
                "homes_passed": homes,
                "active_subscribers": subs,
                "penetration_percent": round(penetration_pct, 1),
                "arpu_monthly_mxn": arpu,
                "capex_access_mxn": capex,
                "cost_per_home_passed": cphp,
                "latitude": lat,
                "longitude": lon,
                "coordinates": [lon, lat],
                "color": color,
                "radius": math.sqrt(homes) * 4.0,
                "tooltip_line1": f"Ciudad: {c_name} | Casas Pasadas: {homes:,} | Suscriptores: {subs:,} ({round(penetration_pct, 1)}%)",
                "tooltip_line2": f"CPHP: ${cphp:.2f} MXN | ARPU: ${arpu:.2f} MXN"
            })
        return clusters

if __name__ == "__main__":
    service = MapService()
    nodes = service.get_nodes_gis_data("CDMX")
    links = service.get_fiber_links_gis_data("CDMX")
    clusters = service.get_access_clusters_gis_data("CDMX")
    print(f"--- MAP SERVICE DEMO (CDMX) ---")
    print(f"Nodos CDMX: {len(nodes)} | Tramos CDMX: {len(links)} | Clusters CDMX: {len(clusters)}")
