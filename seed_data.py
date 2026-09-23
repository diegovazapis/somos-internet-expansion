"""
=====================================================================
SOMOS Internet — Expansión Nacional de Red de Fibra Óptica (México)
Seed Data Generator & SQLite Database Ingestion (Versión Carreteras & MicroPOPs SOMOS Colombia)
Sprint 1 / 3 / 6: Data Foundation & GIS Topology
=====================================================================
"""

import sqlite3
import json
import os
import math

DB_FILE = "somos_network.db"
SCHEMA_FILE = "schema.sql"

def calculate_financials(capex, opex_annual, arpu, subscribers_initial, growth_rate, discount_rate=0.075, years=5):
    """
    Calcula VAN (NPV), TIR (IRR), ROI y Payback formalmente a 5 años.
    """
    cash_flows = [-capex]
    current_subs = subscribers_initial
    total_net_income = 0
    
    for t in range(1, years + 1):
        current_subs = current_subs * (1 + growth_rate)
        annual_revenue = current_subs * arpu * 12
        net_cash_flow = annual_revenue - opex_annual
        cash_flows.append(net_cash_flow)
        total_net_income += net_cash_flow

    # VAN (Valor Actual Neto)
    van = sum(cf / ((1 + discount_rate) ** t) for t, cf in enumerate(cash_flows))
    
    # TIR / IRR aproximación numérica bisección
    def npv_at_rate(r):
        return sum(cf / ((1 + r) ** t) for t, cf in enumerate(cash_flows))
    
    low, high = -0.5, 2.0
    for _ in range(50):
        mid = (low + high) / 2.0
        val = npv_at_rate(mid)
        if abs(val) < 1e-4:
            break
        if val > 0:
            low = mid
        else:
            high = mid
    irr = mid * 100.0

    # ROI acumulado %
    roi = ((total_net_income - capex) / capex) * 100.0

    # Payback en meses
    cumulative = -capex
    payback_months = years * 12.0
    for month in range(1, years * 12 + 1):
        monthly_subs = subscribers_initial * ((1 + growth_rate) ** (month / 12.0))
        monthly_net = (monthly_subs * arpu) - (opex_annual / 12.0)
        cumulative += monthly_net
        if cumulative >= 0:
            payback_months = month
            break

    return round(van, 2), round(irr, 2), round(roi, 2), round(payback_months, 1)

def run_seed():
    db_path = os.path.join(os.path.dirname(__file__), DB_FILE)
    schema_path = os.path.join(os.path.dirname(__file__), SCHEMA_FILE)

    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)

    # 1. Ciudades
    cities = [
        ("CDMX", "Ciudad de México", "CDMX", "Tier 1", 9200000, 95.5, 0.85, 19.4326, -99.1332),
        ("MTY", "Monterrey", "Nuevo León", "Tier 1", 5300000, 91.0, 0.88, 25.6866, -100.3161),
        ("GDL", "Guadalajara", "Jalisco", "Tier 1", 5200000, 89.0, 0.82, 20.6597, -103.3496),
        ("TIJ", "Tijuana", "Baja California", "Tier 2", 2100000, 84.5, 0.78, 32.5149, -117.0382),
        ("MID", "Mérida", "Yucatán", "Tier 2", 1200000, 82.0, 0.90, 20.9676, -89.5926),
    ]
    cursor.executemany("""
        INSERT INTO cities (city_id, name, state, tier_category, population, demand_index, cfe_availability_ratio, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, cities)

    # 2. Nodos de Red (POPs Nacionales, Cores Metro y MicroPOPs SOMOS Colombia Style)
    nodes = [
        # POPs Nacionales Principal Malla
        ("NODE_POP_CDMX", "CDMX", "POP Nacional CDMX Centenario", "NATIONAL_POP", 19.4326, -99.1332, 1000, 420, "2N", "ACTIVE"),
        ("NODE_POP_MTY", "MTY", "POP Nacional MTY Valle", "NATIONAL_POP", 25.6866, -100.3161, 800, 310, "2N", "ACTIVE"),
        ("NODE_POP_GDL", "GDL", "POP Nacional GDL Minerva", "NATIONAL_POP", 20.6597, -103.3496, 800, 290, "2N", "ACTIVE"),
        ("NODE_POP_TIJ", "TIJ", "POP Nacional TIJ Frontera", "NATIONAL_POP", 32.5149, -117.0382, 400, 180, "N+1", "ACTIVE"),
        ("NODE_POP_MID", "MID", "POP Nacional MID Paseo Montejo", "NATIONAL_POP", 20.9676, -89.5926, 400, 140, "N+1", "ACTIVE"),

        # Cores Metro
        ("NODE_METRO_CDMX_N", "CDMX", "Hub Metro CDMX Polanco", "METRO_CORE", 19.4400, -99.1900, 400, 190, "2N", "ACTIVE"),
        ("NODE_METRO_CDMX_S", "CDMX", "Hub Metro CDMX Coyoacán", "METRO_CORE", 19.3500, -99.1600, 400, 160, "2N", "ACTIVE"),
        ("NODE_METRO_MTY_S", "MTY", "Hub Metro MTY San Pedro", "METRO_CORE", 25.6500, -100.3600, 300, 120, "2N", "ACTIVE"),
        ("NODE_METRO_GDL_Z", "GDL", "Hub Metro GDL Zapopan", "METRO_CORE", 20.7200, -103.3900, 300, 110, "2N", "ACTIVE"),
        ("NODE_METRO_TIJ_Z", "TIJ", "Hub Metro TIJ Otay", "METRO_CORE", 32.5300, -116.9700, 200, 80, "N+1", "ACTIVE"),
        ("NODE_METRO_MID_N", "MID", "Hub Metro MID Altabrisa", "METRO_CORE", 21.0100, -89.5800, 200, 60, "N+1", "ACTIVE"),

        # MicroPOPs de Acceso SOMOS Internet (Topología Descentralizada Estilo Colombia)
        ("MPOP_CDMX_POL", "CDMX", "MicroPOP SOMOS Polanco Residencial", "MICRO_POP", 19.4350, -99.1920, 100, 42, "N+1", "ACTIVE"),
        ("MPOP_CDMX_CND", "CDMX", "MicroPOP SOMOS Condesa-Roma", "MICRO_POP", 19.4120, -99.1680, 100, 51, "N+1", "ACTIVE"),
        ("MPOP_CDMX_STF", "CDMX", "MicroPOP SOMOS Santa Fe Enterprise", "MICRO_POP", 19.3600, -99.2600, 100, 29, "N+1", "ACTIVE"),
        ("MPOP_MTY_SPG", "MTY", "MicroPOP SOMOS San Pedro Valle", "MICRO_POP", 25.6550, -100.4000, 100, 38, "N+1", "ACTIVE"),
        ("MPOP_MTY_CUM", "MTY", "MicroPOP SOMOS Cumbres Residential", "MICRO_POP", 25.7100, -100.3800, 100, 55, "N+1", "ACTIVE"),
        ("MPOP_GDL_ZAP", "GDL", "MicroPOP SOMOS Puerta de Hierro", "MICRO_POP", 20.7100, -103.4100, 100, 36, "N+1", "ACTIVE"),
        ("MPOP_GDL_PRV", "GDL", "MicroPOP SOMOS Providencia", "MICRO_POP", 20.6900, -103.3800, 100, 41, "N+1", "ACTIVE"),
        ("MPOP_TIJ_OTY", "TIJ", "MicroPOP SOMOS Otay Industrial", "MICRO_POP", 32.5350, -116.9600, 100, 28, "N+1", "ACTIVE"),
        ("MPOP_TIJ_PLY", "TIJ", "MicroPOP SOMOS Playas de Tijuana", "MICRO_POP", 32.5200, -117.1200, 100, 21, "N+1", "ACTIVE"),
        ("MPOP_MID_ALT", "MID", "MicroPOP SOMOS Altabrisa Norte", "MICRO_POP", 21.0150, -89.5850, 100, 26, "N+1", "ACTIVE"),
        ("MPOP_MID_TEM", "MID", "MicroPOP SOMOS Temozón Norte", "MICRO_POP", 21.0500, -89.6200, 100, 19, "N+1", "ACTIVE")
    ]
    cursor.executemany("""
        INSERT INTO network_nodes (node_id, city_id, name, node_type, latitude, longitude, total_capacity_gbps, used_capacity_gbps, redundancy_level, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, nodes)

    # 3. Tramos de Fibra Óptica (Rutas por Carreteras Federales Reales & Anillos Cerrados)
    # Carretera 57D (CDMX -> Querétaro -> San Luis Potosí -> Saltillo -> Monterrey)
    path_cdmx_mty_hw = [
        [-99.1332, 19.4326], # CDMX
        [-99.2000, 19.5500], # Tepotzotlán
        [-100.3899, 20.5888], # Querétaro
        [-100.9855, 22.1565], # San Luis Potosí
        [-100.6436, 23.6496], # Matehuala
        [-101.0053, 25.4260], # Saltillo
        [-100.3161, 25.6866]  # Monterrey
    ]

    # Autopista 15D (CDMX -> Toluca -> Morelia -> Zamora -> Guadalajara)
    path_cdmx_gdl_hw = [
        [-99.1332, 19.4326], # CDMX
        [-99.6557, 19.2826], # Toluca
        [-100.4422, 19.8927], # Maravatío
        [-101.1949, 19.7060], # Morelia
        [-102.2833, 19.9833], # Zamora
        [-103.3496, 20.6597]  # Guadalajara
    ]

    # Autopista 80D/57D (GDL -> Aguascalientes -> Zacatecas -> Saltillo -> MTY) - Cierra Anillo Backbone Central
    path_gdl_mty_hw = [
        [-103.3496, 20.6597], # Guadalajara
        [-101.9333, 21.3500], # Lagos de Moreno
        [-102.2960, 21.8853], # Aguascalientes
        [-102.5832, 22.7709], # Zacatecas
        [-101.0053, 25.4260], # Saltillo
        [-100.3161, 25.6866]  # Monterrey
    ]

    # Autopista 15D Pacífico (GDL -> Tepic -> Mazatlán -> Culiacán -> Hermosillo -> Mexicali -> Tijuana)
    path_gdl_tij_hw = [
        [-103.3496, 20.6597], # Guadalajara
        [-104.8947, 21.5039], # Tepic
        [-106.4111, 23.2494], # Mazatlán
        [-107.3940, 24.8091], # Culiacán
        [-110.9559, 29.0729], # Hermosillo
        [-115.4683, 32.6245], # Mexicali
        [-117.0382, 32.5149]  # Tijuana
    ]

    # Autopista 150D / Corredor Golfo-Sureste (CDMX -> Puebla -> Orizaba -> Coatzacoalcos -> Villahermosa -> Campeche -> Mérida)
    path_cdmx_mid_hw = [
        [-99.1332, 19.4326], # CDMX
        [-98.2063, 19.0414], # Puebla
        [-97.1000, 18.8500], # Orizaba / Córdoba
        [-94.4667, 18.1500], # Coatzacoalcos
        [-92.9303, 17.9895], # Villahermosa
        [-91.8333, 18.6333], # Ciudad del Carmen
        [-90.5349, 19.8301], # Campeche
        [-89.5926, 20.9676]  # Mérida
    ]

    links = [
        # Backbone Anillo Central y Ramales por Carreteras Federales
        ("LINK_BB_CDMX_MTY", "CDMX", "Backbone DWDM CDMX-MTY (Carretera 57D)", "NODE_POP_CDMX", "NODE_POP_MTY", "BACKBONE_LONG_HAUL", 920.0, 144, 48, "CFE-LONG-HAUL-01", 45000000.0,
         json.dumps({"type": "LineString", "coordinates": path_cdmx_mty_hw}), "OPERATIONAL"),
        ("LINK_BB_CDMX_GDL", "CDMX", "Backbone DWDM CDMX-GDL (Autopista 15D)", "NODE_POP_CDMX", "NODE_POP_GDL", "BACKBONE_LONG_HAUL", 550.0, 144, 48, "CFE-LONG-HAUL-02", 28000000.0,
         json.dumps({"type": "LineString", "coordinates": path_cdmx_gdl_hw}), "OPERATIONAL"),
        ("LINK_BB_GDL_MTY", "GDL", "Backbone DWDM GDL-MTY (Autopista 80D Anillo)", "NODE_POP_GDL", "NODE_POP_MTY", "BACKBONE_LONG_HAUL", 790.0, 96, 32, "CFE-LONG-HAUL-03", 38000000.0,
         json.dumps({"type": "LineString", "coordinates": path_gdl_mty_hw}), "OPERATIONAL"),
        ("LINK_BB_GDL_TIJ", "GDL", "Backbone DWDM GDL-TIJ (Corredor Pacífico 15D)", "NODE_POP_GDL", "NODE_POP_TIJ", "BACKBONE_LONG_HAUL", 2200.0, 96, 24, "CFE-LONG-HAUL-04", 95000000.0,
         json.dumps({"type": "LineString", "coordinates": path_gdl_tij_hw}), "OPERATIONAL"),
        ("LINK_BB_CDMX_MID", "CDMX", "Backbone DWDM CDMX-MID (Corredor Golfo 150D)", "NODE_POP_CDMX", "NODE_POP_MID", "BACKBONE_LONG_HAUL", 1310.0, 96, 24, "CFE-LONG-HAUL-05", 62000000.0,
         json.dumps({"type": "LineString", "coordinates": path_cdmx_mid_hw}), "OPERATIONAL"),

        # Anillos Metropolitanos Cerrados (Seguimiento de Arterias Viales Urbanas)
        ("LINK_METRO_CDMX_RING1", "CDMX", "Anillo Metro CDMX Periférico Norte-Sur", "NODE_POP_CDMX", "NODE_METRO_CDMX_N", "METRO_RING", 18.5, 96, 36, "CFE-METRO-CDMX-01", 3200000.0,
         json.dumps({"type": "LineString", "coordinates": [[-99.1332, 19.4326], [-99.1600, 19.4500], [-99.1900, 19.4400], [-99.1800, 19.3800], [-99.1332, 19.4326]]}), "OPERATIONAL"),
        ("LINK_METRO_MTY_RING1", "MTY", "Anillo Metro MTY Periférico Valle", "NODE_POP_MTY", "NODE_METRO_MTY_S", "METRO_RING", 14.2, 96, 28, "CFE-METRO-MTY-01", 2400000.0,
         json.dumps({"type": "LineString", "coordinates": [[-100.3161, 25.6866], [-100.3400, 25.6700], [-100.3600, 25.6500], [-100.3300, 25.6400], [-100.3161, 25.6866]]}), "OPERATIONAL"),
        ("LINK_METRO_GDL_RING1", "GDL", "Anillo Metro GDL Periférico Gómez Morín", "NODE_POP_GDL", "NODE_METRO_GDL_Z", "METRO_RING", 12.8, 96, 24, "CFE-METRO-GDL-01", 2100000.0,
         json.dumps({"type": "LineString", "coordinates": [[-103.3496, 20.6597], [-103.3700, 20.6900], [-103.3900, 20.7200], [-103.3600, 20.7000], [-103.3496, 20.6597]]}), "OPERATIONAL"),
        ("LINK_METRO_TIJ_RING1", "TIJ", "Anillo Metro TIJ Otay-Vía Rápida", "NODE_POP_TIJ", "NODE_METRO_TIJ_Z", "METRO_RING", 9.6, 48, 16, "CFE-METRO-TIJ-01", 1600000.0,
         json.dumps({"type": "LineString", "coordinates": [[-117.0382, 32.5149], [-117.0000, 32.5250], [-116.9700, 32.5300], [-117.0100, 32.5050], [-117.0382, 32.5149]]}), "OPERATIONAL"),
        ("LINK_METRO_MID_RING1", "MID", "Anillo Metro MID Periférico Norte", "NODE_POP_MID", "NODE_METRO_MID_N", "METRO_RING", 8.2, 48, 12, "CFE-METRO-MID-01", 1300000.0,
         json.dumps({"type": "LineString", "coordinates": [[-89.5926, 20.9676], [-89.5850, 20.9900], [-89.5800, 21.0100], [-89.6000, 21.0000], [-89.5926, 20.9676]]}), "OPERATIONAL")
    ]
    cursor.executemany("""
        INSERT INTO fiber_links (link_id, city_id, name, origin_node_id, destination_node_id, link_type, distance_km, strand_count, used_strand_count, cfe_pole_agreement, deployment_cost_mxn, geojson_geometry, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, links)

    # 4. Bloques de Acceso (Casas Pasadas y CPHP < $500 MXN)
    clusters = [
        ("CLUS_CDMX_POLANCO", "CDMX", "Cluster Residencial & Corp Polanco", 18000, 4200, 580.0, 7560000.0, 420.0, 19.4350, -99.1920),
        ("CLUS_CDMX_CONDESA", "CDMX", "Cluster Residencial Condesa-Roma", 22000, 5100, 520.0, 9460000.0, 430.0, 19.4120, -99.1680),
        ("CLUS_CDMX_SANTAFE", "CDMX", "Cluster Empresarial Santa Fe", 12000, 2900, 750.0, 5520000.0, 460.0, 19.3600, -99.2600),
        ("CLUS_MTY_SANPEDRO", "MTY", "Cluster San Pedro Garza García", 15000, 3800, 620.0, 6600000.0, 440.0, 25.6550, -100.4000),
        ("CLUS_MTY_CUMBRES", "MTY", "Cluster Residencial Cumbres", 25000, 5500, 480.0, 10250000.0, 410.0, 25.7100, -100.3800),
        ("CLUS_GDL_ZAPOPAN", "GDL", "Cluster Puerta de Hierro - Zapopan", 16000, 3600, 550.0, 6720000.0, 420.0, 20.7100, -103.4100),
        ("CLUS_GDL_PROVIDENCIA", "GDL", "Cluster Providencia - Americas", 19000, 4100, 500.0, 8170000.0, 430.0, 20.6900, -103.3800),
        ("CLUS_TIJ_OTAY", "TIJ", "Cluster Otay Industrial & Residencial", 14000, 2800, 490.0, 6300000.0, 450.0, 32.5350, -116.9600),
        ("CLUS_TIJ_CABAÑAS", "TIJ", "Cluster Playas de Tijuana", 11000, 2100, 470.0, 5060000.0, 460.0, 32.5200, -117.1200),
        ("CLUS_MID_ALTABRISA", "MID", "Cluster Altabrisa Residencial", 13000, 2600, 460.0, 5070000.0, 390.0, 21.0150, -89.5850),
        ("CLUS_MID_TEMOZON", "MID", "Cluster Temozón Norte", 10000, 1900, 480.0, 4100000.0, 410.0, 21.0500, -89.6200)
    ]
    cursor.executemany("""
        INSERT INTO access_clusters (cluster_id, city_id, name, homes_passed, active_subscribers, arpu_monthly_mxn, capex_access_mxn, cost_per_home_passed, latitude, longitude)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, clusters)

    # 5. Proyecciones Financieras Oficiales
    financials = []
    city_params = [
        ("CDMX", "Proyección 5 Años Tier 1 Base", 22540000.0, 4800000.0, 580.0, 12200, 0.18),
        ("MTY", "Proyección 5 Años Tier 1 Base", 16850000.0, 3600000.0, 550.0, 9300, 0.16),
        ("GDL", "Proyección 5 Años Tier 1 Base", 14890000.0, 3200000.0, 520.0, 7700, 0.15),
        ("TIJ", "Proyección 5 Años Tier 2 Base", 11360000.0, 2500000.0, 480.0, 4900, 0.20),
        ("MID", "Proyección 5 Años Tier 2 Base", 9170000.0, 1900000.0, 470.0, 4500, 0.22)
    ]

    for city_id, scenario, capex, opex, arpu, subs, growth in city_params:
        van, irr, roi, payback = calculate_financials(capex, opex, arpu, subs, growth, discount_rate=0.075, years=5)
        financials.append((
            f"FIN_{city_id}_BASE", city_id, scenario, capex, opex, arpu, growth, 0.075, 5, van, irr, roi, payback
        ))

    cursor.executemany("""
        INSERT INTO financial_projections (projection_id, city_id, scenario_name, capex_initial_mxn, opex_annual_mxn, arpu_monthly_mxn, subscriber_growth_rate, discount_rate, projection_years, van_mxn, irr_percent, roi_percent, payback_months)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, financials)

    # 6. Matriz de Riesgos
    risks = [
        ("RISK_CFE_01", "CDMX", "REGULATORY", "Demoras en permisos de adosamiento a postería CFE", "Saturación administrativa en la división centro CFE para aprobar dictámenes de tensión.", "HIGH", "HIGH", "Mesa de trabajo técnica bilateral semanal con gerencia regional CFE y prereserva de capacidad.", 8),
        ("RISK_TRAMO_01", "GDL", "TECHNICAL", "Corte crítico en Backbone Fibra Tramo GDL-TIJ", "Accidente de obra civil ajena interrumpe enlace principal de larga distancia.", "CRITICAL", "MEDIUM", "Protección 1+1 activa por ruta alterna DWDM vía MTY y conmutación automática < 50ms.", 9),
        ("RISK_PERMISOS_01", "TIJ", "OPERATIONAL", "Permisos de paso de vía municipales en Tijuana", "Retraso en licencias de construcción de microzanjado urbano por alcaldía.", "MEDIUM", "HIGH", "Acuerdo marco corporativo con cámaras empresariales y despliegue sobre infraestructura CFE existente.", 6),
        ("RISK_CAPEX_01", "MID", "FINANCIAL", "Volatilidad de costo de insumos de fibra óptica importada", "Incremento en tipo de cambio afecta precio de hilos de fibra XGS-PON y transceptores.", "MEDIUM", "MEDIUM", "Contratos de suministro a precio fijo a 12 meses con proveedores Tier 1.", 5)
    ]
    cursor.executemany("""
        INSERT INTO risk_events (risk_id, city_id, category, title, description, severity, probability, mitigation_strategy, impact_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, risks)

    # 7. Cadencias de Gobernanza
    cadences = [
        ("GOV_EXEC_BOARD", "STRATEGIC", "Comité Ejecutivo de Expansión de Red", "Mensual", "CEO, VP Redes, VP Finanzas, Arquitecto de Red", "VAN acumulado, avance CAPEX nacional, ROI a 5 años, alineación estratégica"),
        ("GOV_OPS_WARROOM", "OPERATIONAL", "War Room Semanal de Despliegue & CFE", "Semanal", "Director Despliegue, Gerentes Regionales, Contratistas", "Casas Pasadas por semana, avance de permisos CFE, Costo por Casa Pasada (CPHP < $500 MXN)"),
        ("GOV_TECH_INCIDENT", "TACTICAL", "Comité de Resiliencia & Incidencias Backbone", "Quincenal", "Jefe de NOC, Ingenieros de Transporte DWDM", "MTTR, disponibilidad 99.999%, conmutación de anillos ERPS")
    ]
    cursor.executemany("""
        INSERT INTO governance_cadences (cadence_id, level, forum_name, frequency, participants, kpis_reviewed)
        VALUES (?, ?, ?, ?, ?, ?)
    """, cadences)

    conn.commit()
    conn.close()
    print("Base de datos SQLite 'somos_network.db' generada exitosamente con Rutas de Carreteras Reales y MicroPOPs SOMOS Colombia.")

if __name__ == "__main__":
    run_seed()
