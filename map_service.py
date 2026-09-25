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

    def get_coverage_polygons_gis_data(self, city_id=None):
        """
        Retorna los polígonos de mancha urbana de cobertura FOA para PyDeck GeoJsonLayer / PolygonLayer.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if city_id and city_id.upper() != "MEXICO":
            cursor.execute("""
                SELECT polygon_id, city_id, cluster_id, name, geojson_geometry, area_sqkm, status
                FROM coverage_polygons
                WHERE city_id = ?
            """, (city_id.upper(),))
        else:
            cursor.execute("""
                SELECT polygon_id, city_id, cluster_id, name, geojson_geometry, area_sqkm, status
                FROM coverage_polygons
            """)
        rows = cursor.fetchall()
        conn.close()

        polygons = []
        for p_id, c_id, clus_id, name, geojson_str, area, status in rows:
            geo = json.loads(geojson_str)
            coords = geo.get("coordinates", [[]])[0]
            polygons.append({
                "polygon_id": p_id,
                "city_id": c_id,
                "cluster_id": clus_id,
                "name": name,
                "polygon": coords,
                "area_sqkm": area,
                "status": status,
                "fill_color": [0, 245, 212, 35], # Cian translucido
                "line_color": [0, 245, 212, 220], # Borde cian neon
                "tooltip_line1": f"Cobertura FOA AON | Área: {area} km²",
                "tooltip_line2": f"Estado: {status} | Fibra Dedicada Directa"
            })
        return polygons

    def get_demo_clients_gis_data(self, city_id=None):
        """
        Retorna los clientes demo (edificios FTTB/Enterprise) para capas de puntos en PyDeck.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if city_id and city_id.upper() != "MEXICO":
            cursor.execute("""
                SELECT d.client_id, d.city_id, c.name, d.cluster_id, d.micropop_node_id, d.name, d.client_type, d.contracted_speed_mbps, d.latitude, d.longitude
                FROM demo_clients d
                JOIN cities c ON d.city_id = c.city_id
                WHERE d.city_id = ?
            """, (city_id.upper(),))
        else:
            cursor.execute("""
                SELECT d.client_id, d.city_id, c.name, d.cluster_id, d.micropop_node_id, d.name, d.client_type, d.contracted_speed_mbps, d.latitude, d.longitude
                FROM demo_clients d
                JOIN cities c ON d.city_id = c.city_id
            """)
        rows = cursor.fetchall()
        conn.close()

        clients = []
        for cli_id, c_id, c_name, clus_id, mpop_id, name, c_type, speed, lat, lon in rows:
            clients.append({
                "client_id": cli_id,
                "city_id": c_id,
                "city_name": c_name,
                "name": name,
                "client_type": c_type,
                "contracted_speed_mbps": speed,
                "coordinates": [lon, lat],
                "color": [247, 37, 133] if c_type == "ENTERPRISE" else [114, 9, 183], # Magenta / Morado
                "radius": 400,
                "tooltip_line1": f"Cliente FTTB: {c_type} | Ciudad: {c_name}",
                "tooltip_line2": f"Conexión AON P2P Dedicada: {speed:,} Mbps Simétricos"
            })
        return clients

    def get_ageb_market_feasibility_data(self, city_id=None, filter_quadrant=None):
        """
        Retorna los datos simulados de Geointeligencia por AGEBs (INEGI SCINCE / AMAI / DENUE)
        para el Mapa 2 del Módulo 01 (Matriz de Factibilidad de Mercado 2x2).
        """
        raw_agebs = [
            # CDMX
            {"ageb_id": "0901500010123", "city_id": "CDMX", "city_name": "Ciudad de México", "name": "Satélite Residencial", "lat": 19.5123, "lon": -99.2345, "viviendas": 4250, "pct_horiz": 84.5, "densidad": 2850, "nse": "A/B", "internet": 92.0, "denue": 2, "quadrant": "Q1", "cphp": 415.0},
            {"ageb_id": "0901500010124", "city_id": "CDMX", "city_name": "Ciudad de México", "name": "Coyoacán Centro Residencial", "lat": 19.3498, "lon": -99.1620, "viviendas": 3890, "pct_horiz": 79.2, "densidad": 2600, "nse": "C+", "internet": 88.5, "denue": 1, "quadrant": "Q1", "cphp": 425.0},
            {"ageb_id": "0901500010125", "city_id": "CDMX", "city_name": "Ciudad de México", "name": "Polanco / Reforma Corporativo", "lat": 19.4326, "lon": -99.1912, "viviendas": 1820, "pct_horiz": 18.5, "densidad": 950, "nse": "A/B", "internet": 96.0, "denue": 4, "quadrant": "Q2", "cphp": 485.0},
            {"ageb_id": "0901500010126", "city_id": "CDMX", "city_name": "Ciudad de México", "name": "Santa Fe Contadero Vertical", "lat": 19.3621, "lon": -99.2611, "viviendas": 1450, "pct_horiz": 22.0, "densidad": 820, "nse": "A/B", "internet": 94.0, "denue": 3, "quadrant": "Q2", "cphp": 490.0},
            {"ageb_id": "0901500010127", "city_id": "CDMX", "city_name": "Ciudad de México", "name": "Tecámac / Ecatepec Norte Horiz", "lat": 19.6012, "lon": -99.0123, "viviendas": 7800, "pct_horiz": 91.0, "densidad": 4100, "nse": "C-", "internet": 68.0, "denue": 1, "quadrant": "Q3", "cphp": 395.0},
            {"ageb_id": "0901500010128", "city_id": "CDMX", "city_name": "Ciudad de México", "name": "Vallejo Zona Industrial", "lat": 19.4890, "lon": -99.1550, "viviendas": 650, "pct_horiz": 12.0, "densidad": 350, "nse": "D+", "internet": 55.0, "denue": 3, "quadrant": "Q4", "cphp": 620.0},

            # MTY
            {"ageb_id": "1903900010201", "city_id": "MTY", "city_name": "Monterrey", "name": "San Pedro Garza García Residencial", "lat": 25.6580, "lon": -100.3680, "viviendas": 3400, "pct_horiz": 81.0, "densidad": 2300, "nse": "A/B", "internet": 95.0, "denue": 2, "quadrant": "Q1", "cphp": 420.0},
            {"ageb_id": "1903900010202", "city_id": "MTY", "city_name": "Monterrey", "name": "Valle Oriente Torre Vertical", "lat": 25.6420, "lon": -100.3180, "viviendas": 1950, "pct_horiz": 25.0, "densidad": 1100, "nse": "A/B", "internet": 93.0, "denue": 3, "quadrant": "Q2", "cphp": 475.0},
            {"ageb_id": "1903900010203", "city_id": "MTY", "city_name": "Monterrey", "name": "Juárez / García Periferia Horiz", "lat": 25.6500, "lon": -100.1800, "viviendas": 6200, "pct_horiz": 94.0, "densidad": 3800, "nse": "C-", "internet": 71.0, "denue": 1, "quadrant": "Q3", "cphp": 390.0},
            {"ageb_id": "1903900010204", "city_id": "MTY", "city_name": "Monterrey", "name": "Santa Catarina Industrial", "lat": 25.6800, "lon": -100.4600, "viviendas": 580, "pct_horiz": 15.0, "densidad": 400, "nse": "D+", "internet": 58.0, "denue": 2, "quadrant": "Q4", "cphp": 650.0},

            # GDL
            {"ageb_id": "1403900010301", "city_id": "GDL", "city_name": "Guadalajara", "name": "Puerta de Hierro / Providencia", "lat": 20.7100, "lon": -103.4100, "viviendas": 3600, "pct_horiz": 77.0, "densidad": 2500, "nse": "A/B", "internet": 91.0, "denue": 2, "quadrant": "Q1", "cphp": 430.0},
            {"ageb_id": "1403900010302", "city_id": "GDL", "city_name": "Guadalajara", "name": "Americana / Chapultepec Corp", "lat": 20.6750, "lon": -103.3700, "viviendas": 1600, "pct_horiz": 30.0, "densidad": 1200, "nse": "C+", "internet": 89.0, "denue": 3, "quadrant": "Q2", "cphp": 460.0},
            {"ageb_id": "1403900010303", "city_id": "GDL", "city_name": "Guadalajara", "name": "Tlajomulco de Zúñiga Horiz", "lat": 20.4700, "lon": -103.4400, "viviendas": 8100, "pct_horiz": 96.0, "densidad": 4200, "nse": "C-", "internet": 69.0, "denue": 1, "quadrant": "Q3", "cphp": 385.0},
            {"ageb_id": "1403900010304", "city_id": "GDL", "city_name": "Guadalajara", "name": "El Salto Parque Industrial", "lat": 20.5200, "lon": -103.2400, "viviendas": 490, "pct_horiz": 10.0, "densidad": 300, "nse": "D+", "internet": 52.0, "denue": 2, "quadrant": "Q4", "cphp": 680.0},

            # TIJ
            {"ageb_id": "0200400010401", "city_id": "TIJ", "city_name": "Tijuana", "name": "Agua Caliente / Chapultepec Residencial", "lat": 32.5100, "lon": -117.0100, "viviendas": 2900, "pct_horiz": 82.0, "densidad": 2200, "nse": "A/B", "internet": 88.0, "denue": 1, "quadrant": "Q1", "cphp": 410.0},
            {"ageb_id": "0200400010402", "city_id": "TIJ", "city_name": "Tijuana", "name": "Zona Río Vertical / Corporativo", "lat": 32.5300, "lon": -117.0200, "viviendas": 1200, "pct_horiz": 20.0, "densidad": 900, "nse": "C+", "internet": 90.0, "denue": 3, "quadrant": "Q2", "cphp": 470.0},
            {"ageb_id": "0200400010403", "city_id": "TIJ", "city_name": "Tijuana", "name": "Villa del Campo / Otay Periferia", "lat": 32.4800, "lon": -116.8500, "viviendas": 5400, "pct_horiz": 92.0, "densidad": 3600, "nse": "C-", "internet": 65.0, "denue": 1, "quadrant": "Q3", "cphp": 398.0},
            {"ageb_id": "0200400010404", "city_id": "TIJ", "city_name": "Tijuana", "name": "Mesa de Otay Industrial", "lat": 32.5400, "lon": -116.9400, "viviendas": 410, "pct_horiz": 14.0, "densidad": 280, "nse": "D+", "internet": 50.0, "denue": 2, "quadrant": "Q4", "cphp": 640.0},

            # MID
            {"ageb_id": "3105000010501", "city_id": "MID", "city_name": "Mérida", "name": "Altabrisa / Temozón Norte Residencial", "lat": 21.0200, "lon": -89.5800, "viviendas": 3100, "pct_horiz": 86.0, "densidad": 2100, "nse": "A/B", "internet": 94.0, "denue": 1, "quadrant": "Q1", "cphp": 405.0},
            {"ageb_id": "3105000010502", "city_id": "MID", "city_name": "Mérida", "name": "Paseo Montejo Centro Histórico", "lat": 20.9800, "lon": -89.6200, "viviendas": 1400, "pct_horiz": 45.0, "densidad": 1300, "nse": "C+", "internet": 87.0, "denue": 3, "quadrant": "Q2", "cphp": 455.0},
            {"ageb_id": "3105000010503", "city_id": "MID", "city_name": "Mérida", "name": "Kanasín Periferia Horizontal", "lat": 20.9300, "lon": -89.5500, "viviendas": 4800, "pct_horiz": 95.0, "densidad": 3300, "nse": "C-", "internet": 67.0, "denue": 1, "quadrant": "Q3", "cphp": 392.0},
            {"ageb_id": "3105000010504", "city_id": "MID", "city_name": "Mérida", "name": "Umán Corredor Industrial", "lat": 20.8800, "lon": -89.7400, "viviendas": 380, "pct_horiz": 18.0, "densidad": 250, "nse": "D+", "internet": 48.0, "denue": 2, "quadrant": "Q4", "cphp": 660.0},
        ]

        output = []
        for item in raw_agebs:
            if city_id and city_id.upper() != "MEXICO" and item["city_id"] != city_id.upper():
                continue
            if filter_quadrant and item["quadrant"] != filter_quadrant:
                continue

            q_id = item["quadrant"]
            if q_id == "Q1":
                q_title = "Cuadrante 1: Oportunidad Premium"
                color = [0, 245, 212] # Verde cian neón
                ocean = "Océano Azul (Alta Oportunidad / Competencia Moderada DENUE)"
            elif q_id == "Q2":
                q_title = "Cuadrante 2: Nicho Vertical / Corp"
                color = [0, 180, 216] # Azul cian neón
                ocean = "Nicho FTTB / Corporativo (Alta Plusvalía Vertical)"
            elif q_id == "Q3":
                q_title = "Cuadrante 3: Mercado Masivo Periferia"
                color = [255, 183, 3] # Amarillo dorado neón
                ocean = "Mercado Masivo Alta Densidad (Volumen Horizontal)"
            else:
                q_title = "Cuadrante 4: Descarte / Zonas Especiales"
                color = [233, 69, 96] # Rojo coral
                ocean = "Zona Industrial / Bajo Interés Comercial"

            score = min(100.0, round((item["pct_horiz"] * 0.4) + (item["internet"] * 0.4) + ((5 - item["denue"]) * 4), 1))

            output.append({
                "ageb_id": item["ageb_id"],
                "city_id": item["city_id"],
                "city_name": item["city_name"],
                "name": item["name"],
                "coordinates": [item["lon"], item["lat"]],
                "latitude": item["lat"],
                "longitude": item["lon"],
                "total_viviendas": item["viviendas"],
                "pct_vivienda_horizontal": item["pct_horiz"],
                "densidad_casas_sqkm": item["densidad"],
                "nse_predominante": item["nse"],
                "internet_penetration_pct": item["internet"],
                "denue_competitors": item["denue"],
                "cuadrante_id": q_id,
                "cuadrante_nombre": q_title,
                "score_factibilidad": score,
                "cost_per_home_passed": item["cphp"],
                "ocean_type": ocean,
                "color": color,
                "radius": math.sqrt(item["viviendas"]) * 6.5,
                "tooltip_line1": f"AGEB {item['ageb_id']} — {item['name']} ({item['nse']})",
                "tooltip_line2": f"Casas/km²: {item['densidad']:,} ({item['pct_horiz']}% Horiz) | CPHP Est: ${item['cphp']:.2f} MXN | DENUE: {item['denue']} comp | {q_title}"
            })
        return output

if __name__ == "__main__":
    service = MapService()
    nodes = service.get_nodes_gis_data("CDMX")
    links = service.get_fiber_links_gis_data("CDMX")
    clusters = service.get_access_clusters_gis_data("CDMX")
    polys = service.get_coverage_polygons_gis_data("CDMX")
    clients = service.get_demo_clients_gis_data("CDMX")
    agebs = service.get_ageb_market_feasibility_data("CDMX")
    print(f"--- MAP SERVICE DEMO (CDMX) ---")
    print(f"Nodos: {len(nodes)} | Tramos: {len(links)} | Clusters: {len(clusters)} | Polígonos: {len(polys)} | Clientes Demo: {len(clients)} | AGEBs Market: {len(agebs)}")

