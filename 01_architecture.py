"""
=====================================================================
SOMOS Internet — Expansión Nacional de Red de Fibra Óptica (México)
Sprint 4 & 6: Streamlit Frontend — Módulo 01: Arquitectura & Topología
Con 2 Mapas Independientes: (1) Topología de Red FOA y (2) Geointeligencia por AGEBs INEGI/AMAI
=====================================================================
"""

import streamlit as st
import os
from pydeck_layers import render_national_network_deck, render_ageb_market_deck
from map_service import MapService

import folium
from folium.plugins import Draw
from streamlit_folium import st_folium
import sqlite3
import json

def render():
    st.title("🌐 Módulo 1: Arquitectura de Red & Geointeligencia de Mercado")
    st.caption("Visor dual independiente: Mapa 1 (Topología Física FOA AON P2P) y Mapa 2 (Factibilidad por AGEBs INEGI / AMAI / DENUE)")

    # Selector de Mapa Principal
    map_mode = st.radio(
        "🗺️ Selecciona el Mapa a Visualizar:",
        [
            "Mapa 1: Topología Física & Arquitectura de Red (DWDM 1+1 / Metro / FOA AON P2P)",
            "Mapa 2: Geointeligencia & Factibilidad de Mercado por AGEBs (Matriz INEGI / AMAI 2x2)"
        ],
        horizontal=True
    )

    service = MapService()

    # =========================================================================
    # MAPA 1: TOPOLOGÍA FÍSICA & ARQUITECTURA DE RED
    # =========================================================================
    if "Mapa 1" in map_mode:
        tab_vis, tab_editor = st.tabs(["🗺️ Visualizador Topológico 2D", "✏️ Editor GIS Interactivo"])

        with tab_vis:
            # Controles de navegación y filtrado por ciudad y capa
            col_sel, col_filter, col_stat1, col_stat2, col_stat3 = st.columns([2, 2, 1, 1, 1])

            with col_sel:
                city_selected = st.selectbox(
                    "Seleccionar Ámbito / Ciudad:",
                    ["MEXICO", "CDMX", "MTY", "GDL", "TIJ", "MID"],
                    format_func=lambda x: "Red Nacional México" if x == "MEXICO" else f"📍 {x}",
                    key="vis_city_sel"
                )

            with col_filter:
                layer_option = st.selectbox(
                    "Filtrar Capa de Red (Vista 2D):",
                    ["ALL", "BACKBONE", "METRO", "MICROPOP_ACCESS", "COVERAGE", "CLIENTS"],
                    format_func=lambda x: {
                        "ALL": "🟡🔵🟢 Todas las Capas (Visión Completa 2D)",
                        "BACKBONE": "🟡 Backbone DWDM 1+1 (Carreteras Paralelas)",
                        "METRO": "🔵 Distribución Metro (Redes Activas IP/MPLS ERPS)",
                        "MICROPOP_ACCESS": "🟢 Acceso Fibra Óptica Activa FOA (MicroPOPs AON P2P)",
                        "COVERAGE": "🟩 Manchas de Cobertura Urbana FOA",
                        "CLIENTS": "🟣 Clientes Demo FTTB / Enterprise"
                    }[x],
                    key="vis_layer_sel"
                )

            nodes = service.get_nodes_gis_data(city_selected)
            links = service.get_fiber_links_gis_data(city_selected)
            clusters = service.get_access_clusters_gis_data(city_selected)
            polys = service.get_coverage_polygons_gis_data(city_selected)
            clients = service.get_demo_clients_gis_data(city_selected)

            with col_stat1:
                st.metric("Nodos de Red", len(nodes))
            with col_stat2:
                st.metric("Tramos Fibra (1+1)", len(links))
            with col_stat3:
                st.metric("Clientes Demo FTTB", len(clients))

            # Banner de Diferencial Tecnológico SOMOS Internet
            st.info(
                "⚡ **Diferencial Competitivo SOMOS Internet — Red de Fibra Óptica Activa (FOA) / AON Punto a Punto & Redundancia 1+1**:\n\n"
                "• **Backbone DWDM 1+1**: Enlaces de larga distancia con dos trazados paralelos disjuntos (**Ruta A Primaria** en amarillo y **Ruta B Protección** en naranja) en carreteras federales.\n"
                "• **Acceso FOA AON P2P**: Hilo dedicado por cliente/edificio desde MicroPOPs energizados, garantizando **hasta 2 Gbps simétricos** sin caídas por saturación."
            )

            # Mapa 2D Plano Interactivo PyDeck
            st.markdown("### 🗺️ Mapa 1: Topología de Red Nacional 2D")
            st.caption("🟡 **Backbone Ruta A** | 🟠 **Backbone Ruta B (Protección 1+1)** | 🔵 **Anillos Metro ERPS** | 🟢 **MicroPOPs AON** | 🟩 **Manchas Cobertura FOA** | 🟣 **Clientes FTTB**")
            
            deck = render_national_network_deck(city_selected, pitch=0.0, layer_filter=layer_option)
            st.pydeck_chart(deck, use_container_width=True)

            # Detalle de capas de arquitectura
            st.markdown("---")
            st.subheader("📚 Especificaciones Técnicas por Capa de Red (Arquitectura SOMOS Internet)")

            col_c1, col_c2, col_c3 = st.columns(3)

            with col_c1:
                st.markdown("#### 🟡 1. Backbone Nacional 1+1")
                st.info("**Tecnología**: DWDM / ROADM 400Gbps por lambda\n\n"
                        "**Redundancia**: Malla 1+1 con Rutas Paralelas Disjuntas (Ruta A + Ruta B) en carreteras (57D, 15D, 80D)\n\n"
                        "**Disponibilidad Target**: **99.999%** (Cinco nueves)")

            with col_c2:
                st.markdown("#### 🔵 2. Distribución Metro (Redes Activas)")
                st.success("**Tecnología**: IP/MPLS + Ethernet Metro Activo a 100G\n\n"
                           "**Protección**: Anillos cerrados ERPS (ITU-T G.8032) con conmutación < 50ms\n\n"
                           "**Infraestructura**: Compartición de postería CFE (Norma CFE GD-O-GEN-LC-001)")

            with col_c3:
                st.markdown("#### 🟢 3. Acceso FOA / AON Punto a Punto")
                st.warning("**Tecnología**: **Fibra Óptica Activa (FOA) / AON P2P** desde **MicroPOPs Energizados (Modelo SOMOS Colombia)**\n\n"
                           "**Garantía**: Hilo dedicado por cliente/edificio, **hasta 2 Gbps simétricos (Subida = Bajada)** sin saturación\n\n"
                           "**Eficiencia CAPEX**: Costo por casa pasada **CPHP <= $500 MXN**")

        with tab_editor:
            st.subheader("✏️ Editor GIS Interactivo (Modificación de Vértices & Trazados)")
            st.caption("Edita en tiempo real las coordenadas de nodos, vértices de tramos de fibra y polígonos de cobertura. Al hacer clic en 'Guardar Cambios', la base de datos SQLite `somos_network.db` se actualizará automáticamente.")

            col_ed_city, col_ed_action = st.columns([3, 3])
            with col_ed_city:
                ed_city = st.selectbox(
                    "Seleccionar Ciudad para Editar Topología:",
                    ["CDMX", "MTY", "GDL", "TIJ", "MID"],
                    key="ed_city_sel"
                )

            viewport = service.get_viewport_for_city(ed_city)
            ed_nodes = service.get_nodes_gis_data(ed_city)
            ed_links = service.get_fiber_links_gis_data(ed_city)
            ed_polys = service.get_coverage_polygons_gis_data(ed_city)

            m = folium.Map(
                location=[viewport["latitude"], viewport["longitude"]],
                zoom_start=viewport["zoom"],
                tiles="OpenStreetMap"
            )

            fg = folium.FeatureGroup(name="Capas Editables GIS Topología")

            for p in ed_polys:
                folium.Polygon(
                    locations=[[lat, lon] for lon, lat in p["polygon"]],
                    color="#00f5d4",
                    fill=True,
                    fill_color="#00f5d4",
                    fill_opacity=0.25,
                    weight=2,
                    popup=f"Polígono: {p['name']}"
                ).add_to(fg)

            for l in ed_links:
                coords_latlon = [[lat, lon] for lon, lat in l["path"]]
                line_color = "#ffb703" if "BACKBONE" in l["link_type"] else "#00b4d8"
                folium.PolyLine(
                    locations=coords_latlon,
                    color=line_color,
                    weight=5 if "BACKBONE" in l["link_type"] else 3,
                    popup=f"Tramo: {l['name']}"
                ).add_to(fg)

            for n in ed_nodes:
                folium.Marker(
                    location=[n["latitude"], n["longitude"]],
                    icon=folium.Icon(color="red" if n["node_type"] == "NATIONAL_POP" else ("blue" if n["node_type"] == "METRO_CORE" else "green")),
                    popup=f"Nodo: {n['name']} ({n['node_type']})"
                ).add_to(fg)

            fg.add_to(m)

            draw = Draw(
                export=True,
                feature_group=fg,
                filename=f"somos_{ed_city.lower()}_edited.geojson",
                position="topleft",
                draw_options={
                    "polyline": True,
                    "polygon": True,
                    "circle": False,
                    "rectangle": True,
                    "marker": True,
                    "circlemarker": False
                },
                edit_options={
                    "edit": True,
                    "remove": True
                }
            )
            draw.add_to(m)

            st_data = st_folium(m, width="100%", height=600, key=f"folium_editor_{ed_city}")

            st.markdown("---")
            st.markdown("### 💾 Guardar Cambios en Base de Datos")

            if st_data and st_data.get("all_drawings"):
                st.success(f"📍 **Nuevas geometrías/ediciones capturadas**: {len(st_data['all_drawings'])} elemento(s) modificado(s) en {ed_city}.")
                if st.button("💾 Aplicar & Guardar Cambios en Base de Datos (somos_network.db)", key="btn_save_gis"):
                    db_path = os.path.join(os.path.dirname(__file__), "somos_network.db")
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()

                    for idx, item in enumerate(st_data["all_drawings"]):
                        geom = item.get("geometry", {})
                        g_type = geom.get("type")
                        if g_type == "LineString":
                            link_id = f"EDITED_LINK_{ed_city}_{idx+1}"
                            cursor.execute("""
                                INSERT OR REPLACE INTO fiber_links (link_id, city_id, name, origin_node_id, destination_node_id, link_type, distance_km, strand_count, used_strand_count, cfe_pole_agreement, deployment_cost_mxn, geojson_geometry, status)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (link_id, ed_city, f"Tramo Editado GIS {idx+1}", "NODE_POP_" + ed_city, "NODE_POP_" + ed_city, "METRO_RING", 10.0, 96, 24, "CFE-EDITED", 1500000.0, json.dumps(geom), "OPERATIONAL"))
                        elif g_type == "Polygon":
                            poly_id = f"EDITED_POLY_{ed_city}_{idx+1}"
                            cursor.execute("""
                                INSERT OR REPLACE INTO coverage_polygons (polygon_id, city_id, cluster_id, name, geojson_geometry, area_sqkm, status)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                            """, (poly_id, ed_city, "CLUS_" + ed_city + "_EDITED", f"Mancha Cobertura Editada {idx+1}", json.dumps(geom), 5.0, "ACTIVE"))
                        elif g_type == "Point":
                            node_id = f"EDITED_MPOP_{ed_city}_{idx+1}"
                            coords = geom.get("coordinates", [0, 0])
                            cursor.execute("""
                                INSERT OR REPLACE INTO network_nodes (node_id, city_id, name, node_type, latitude, longitude, total_capacity_gbps, used_capacity_gbps, redundancy_level, status)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (node_id, ed_city, f"MicroPOP Editado {idx+1}", "MICRO_POP", coords[1], coords[0], 100, 20, "N+1", "ACTIVE"))

                    conn.commit()
                    conn.close()
                    st.balloons()
                    st.success("¡Base de datos SQLite 'somos_network.db' actualizada exitosamente con tus ediciones de vértices!")
            else:
                st.info("💡 **Instrucciones del Editor GIS**: Utiliza las herramientas en la esquina superior izquierda del mapa (✏️ para mover/editar vértices existentes, 📏 para dibujar nuevas líneas o polígonos). Una vez realices modificaciones, aparecerá el botón para guardar en la base de datos.")

    # =========================================================================
    # MAPA 2: GEOINTELIGENCIA & FACTIBILIDAD DE MERCADO POR AGEBs (INEGI / AMAI)
    # =========================================================================
    else:
        st.subheader("📊 Mapa 2: Geointeligencia & Análisis de Viabilidad de Mercado por AGEBs (INEGI / AMAI)")
        st.caption("Cruzamiento de variables de Vivienda Horizontal (Censo INEGI SCINCE), Nivel Socioeconómico (Regla AMAI A/B, C+, C, C-) y Competencia DENUE")

        st.markdown("""
            <div style="background-color: #0b132b; border: 1px solid #3a86ff; border-radius: 8px; padding: 14px 18px; margin-bottom: 20px;">
                <span style="font-size: 16px; color: #3a86ff; font-weight: bold;">🎯 Marco Metodológico de Geointeligencia de Mercado por AGEBs</span><br>
                <span style="font-size: 13px; color: #e0e0e0;">
                    Las <b>Áreas Geográficas Estadísticas Básicas (AGEBs)</b> representan la unidad micro-urbana del INEGI. 
                    Evaluamos la factibilidad cruzando la <b>Concentración de Vivienda Horizontal (Casas/km²)</b> con el <b>Nivel Socioeconómico (NSE AMAI)</b> y la densidad de competidores en el <b>DENUE INEGI</b>.
                </span>
            </div>
        """, unsafe_allow_html=True)

        col_mkt_city, col_mkt_quad, col_mkt_denue = st.columns([2, 3, 2])

        with col_mkt_city:
            mkt_city = st.selectbox(
                "Seleccionar Ciudad / Mercado:",
                ["MEXICO", "CDMX", "MTY", "GDL", "TIJ", "MID"],
                format_func=lambda x: "Todas las Ciudades (México)" if x == "MEXICO" else f"📍 {x}",
                key="mkt_city_sel"
            )

        with col_mkt_quad:
            quad_filter = st.selectbox(
                "Filtrar por Cuadrante de Matriz 2x2:",
                ["ALL", "Q1", "Q2", "Q3", "Q4"],
                format_func=lambda x: {
                    "ALL": "🟢🔵🟡🔴 Todos los Cuadrantes (Visión Completa)",
                    "Q1": "🟢 Cuadrante 1: Oportunidad Premium (NSE Alto + Alta Densidad Horiz)",
                    "Q2": "🔵 Cuadrante 2: Nicho Vertical / Corp (NSE Alto + Densidad Vertical)",
                    "Q3": "🟡 Cuadrante 3: Mercado Masivo Periferia (NSE Medio/Bajo + Alta Densidad Horiz)",
                    "Q4": "🔴 Cuadrante 4: Descarte / Zonas Especiales (Industria / Comercio)"
                }[x],
                key="mkt_quad_sel"
            )

        agebs_data = service.get_ageb_market_feasibility_data(mkt_city, filter_quadrant=None if quad_filter == "ALL" else quad_filter)

        with col_mkt_denue:
            st.metric("AGEBs Analizadas", len(agebs_data))

        # Matriz 2x2 Explicativa de Factibilidad
        st.markdown("### 🧱 Matriz de Priorización 2x2 (Concentración Horizontal vs NSE AMAI)")

        q1_count = len([a for a in agebs_data if a["cuadrante_id"] == "Q1"])
        q2_count = len([a for a in agebs_data if a["cuadrante_id"] == "Q2"])
        q3_count = len([a for a in agebs_data if a["cuadrante_id"] == "Q3"])
        q4_count = len([a for a in agebs_data if a["cuadrante_id"] == "Q4"])

        col_q1, col_q2 = st.columns(2)
        with col_q1:
            st.markdown(f"""
                <div style="background-color: #0f2b1d; border-left: 5px solid #00f5d4; padding: 12px; border-radius: 6px; margin-bottom: 10px;">
                    <span style="color: #00f5d4; font-weight: bold;">🟢 Cuadrante 1: Oportunidad Premium ({q1_count} AGEBs)</span><br>
                    <span style="font-size: 12px; color: #e0e0e0;">
                        <b>NSE Alto (A/B, C+) + Alta Concentración Horizontal</b><br>
                        • Fraccionamientos cerrados y colonias de alta plusvalía.<br>
                        • ARPU Alto ($650 - $950 MXN), CPHP Objetivo <= $430 MXN.<br>
                        • <i>Ej: Satélite (CDMX), San Pedro (MTY), Puerta de Hierro (GDL).</i>
                    </span>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
                <div style="background-color: #3d2600; border-left: 5px solid #ffb703; padding: 12px; border-radius: 6px;">
                    <span style="color: #ffb703; font-weight: bold;">🟡 Cuadrante 3: Mercado Masivo / Periferia ({q3_count} AGEBs)</span><br>
                    <span style="font-size: 12px; color: #e0e0e0;">
                        <b>NSE Medio/Bajo (C-, D+) + Alta Concentración Horizontal</b><br>
                        • Zonas dormitorio con densidad masiva de casas independientes.<br>
                        • Océano Azul de penetración masiva, CPHP Cero Desperdicio <= $395 MXN.<br>
                        • <i>Ej: Tecámac (CDMX), Tlajomulco (GDL), Juárez (MTY).</i>
                    </span>
                </div>
            """, unsafe_allow_html=True)

        with col_q2:
            st.markdown(f"""
                <div style="background-color: #0d2137; border-left: 5px solid #00b4d8; padding: 12px; border-radius: 6px; margin-bottom: 10px;">
                    <span style="color: #00b4d8; font-weight: bold;">🔵 Cuadrante 2: Nicho Vertical / Corporativo ({q2_count} AGEBs)</span><br>
                    <span style="font-size: 12px; color: #e0e0e0;">
                        <b>NSE Alto (A/B, C+) + Baja Concentración Horizontal</b><br>
                        • Predominantemente torres de departamentos u oficinas.<br>
                        • Enfoque FTTB / Red Dedicada por Edificio Completo.<br>
                        • <i>Ej: Polanco / Santa Fe (CDMX), Valle Oriente (MTY).</i>
                    </span>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div style="background-color: #2b0f19; border-left: 5px solid #e94560; padding: 12px; border-radius: 6px;">
                    <span style="color: #e94560; font-weight: bold;">🔴 Cuadrante 4: Descarte / Zonas Especiales ({q4_count} AGEBs)</span><br>
                    <span style="font-size: 12px; color: #e0e0e0;">
                        <b>NSE Bajo (D, E) + Baja Concentración Horizontal</b><br>
                        • Parques industriales, bodegas o centros históricos degradados.<br>
                        • Descarte para red residencial horizontal; baja factibilidad.<br>
                        • <i>Ej: Vallejo (CDMX), El Salto (GDL), Umán (MID).</i>
                    </span>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 🗺️ Mapa 2: Geointeligencia de Mercado por AGEBs (Mapa de Calor 2D)")
        st.caption("🟢 **Q1 Premium** | 🔵 **Q2 Vertical/Corp** | 🟡 **Q3 Masivo Periferia** | 🔴 **Q4 Descarte**")

        deck_mkt = render_ageb_market_deck(mkt_city, filter_quadrant=None if quad_filter == "ALL" else quad_filter)
        st.pydeck_chart(deck_mkt, use_container_width=True)

        # Tabla de Micro-Geointeligencia por AGEB
        st.markdown("---")
        st.subheader("📋 Tabla de Análisis de Micro-Factibilidad por AGEB (INEGI SCINCE / AMAI)")

        st.dataframe(
            agebs_data,
            column_config={
                "ageb_id": "AGEB INEGI",
                "city_name": "Ciudad",
                "name": "Subzona / Colonia",
                "cuadrante_nombre": "Cuadrante Matriz",
                "total_viviendas": st.column_config.NumberColumn("Viviendas Totales", format="%d"),
                "pct_vivienda_horizontal": st.column_config.NumberColumn("Horizontalidad (%)", format="%.1f%%"),
                "densidad_casas_sqkm": st.column_config.NumberColumn("Casas/km²", format="%d"),
                "nse_predominante": "NSE AMAI",
                "internet_penetration_pct": st.column_config.NumberColumn("Penetración Internet (%)", format="%.1f%%"),
                "denue_competitors": "Competidores DENUE",
                "score_factibilidad": st.column_config.NumberColumn("Score Factibilidad", format="%.1f pts"),
                "cost_per_home_passed": st.column_config.NumberColumn("CPHP Est. (MXN)", format="$%.2f MXN"),
                "ocean_type": "Diagnóstico de Mercado"
            },
            use_container_width=True
        )

if __name__ == "__main__":
    st.set_page_config(page_title="SOMOS Internet - Arquitectura & Geointeligencia", layout="wide")
    render()
