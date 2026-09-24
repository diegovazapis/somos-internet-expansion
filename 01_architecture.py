"""
=====================================================================
SOMOS Internet — Expansión Nacional de Red de Fibra Óptica (México)
Sprint 4: Streamlit Frontend — Módulo 01: Arquitectura & Topología
=====================================================================
"""

import streamlit as st
import os
from pydeck_layers import render_national_network_deck
from map_service import MapService

def render():
    st.title("🌐 Módulo 1: Arquitectura de Red & Topología Nacional")
    st.caption("Visión jerárquica 2D de 3 capas: Backbone DWDM 400G (Carreteras), Distribución Metro Activa 100G (ERPS) y Acceso Fibra Óptica Activa (FOA) / AON Punto a Punto (P2P)")

    # Controles de navegación y filtrado por ciudad y capa
    col_sel, col_filter, col_stat1, col_stat2, col_stat3 = st.columns([2, 2, 1, 1, 1])

    with col_sel:
        city_selected = st.selectbox(
            "Seleccionar Ámbito / Ciudad:",
            ["MEXICO", "CDMX", "MTY", "GDL", "TIJ", "MID"],
            format_func=lambda x: "Red Nacional México" if x == "MEXICO" else f"📍 {x}"
        )

    with col_filter:
        layer_option = st.selectbox(
            "Filtrar Capa de Red (Vista 2D):",
            ["ALL", "BACKBONE", "METRO", "MICROPOP_ACCESS"],
            format_func=lambda x: {
                "ALL": "🟡🔵🟢 Todas las Capas (Visión Completa 2D)",
                "BACKBONE": "🟡 Backbone DWDM (Anillos Redundantes Carreteras)",
                "METRO": "🔵 Distribución Metro (Redes Activas IP/MPLS ERPS)",
                "MICROPOP_ACCESS": "🟢 Acceso Fibra Óptica Activa FOA (AON P2P MicroPOPs)"
            }[x]
        )

    service = MapService()
    nodes = service.get_nodes_gis_data(city_selected)
    links = service.get_fiber_links_gis_data(city_selected)
    clusters = service.get_access_clusters_gis_data(city_selected)

    with col_stat1:
        st.metric("Nodos de Red", len(nodes))
    with col_stat2:
        st.metric("Tramos de Fibra", len(links))
    with col_stat3:
        st.metric("Clusters Acceso FOA", len(clusters))

    # Banner de Diferencial Tecnológico SOMOS Internet
    st.info(
        "⚡ **Diferencial Competitivo SOMOS Internet — Red de Fibra Óptica Activa (FOA) / AON Punto a Punto**:\n\n"
        "A diferencia de los operadores tradicionales (Claro, Tigo, Movistar, ETB) que despliegan redes pasivas GPON/PON donde hasta 64 vecinos comparten la misma fibra, **SOMOS Internet opera con arquitectura AON (Active Optical Network) Punto a Punto (P2P)**. "
        "Cada cliente/edificio (FTTB) cuenta con un **cable de fibra dedicado** conectado a MicroPOPs energizados e inteligentes, garantizando **ancho de banda 100% dedicado, velocidad 100% simétrica de hasta 2 Gbps (subida = bajada)** y **cero caídas por saturación en horas pico**."
    )

    # Mapa 2D Plano Interactivo PyDeck
    st.markdown("### 🗺️ Mapa de Topología de Red (Vista Superior 2D Plana)")
    st.caption("🟢 **MicroPOPs Activos AON (Cian/Verde)** | 🔵 **Core Metro (Azul)** | 🔴 **POP Nacional (Rojo)** | 🟡 **Carreteras Backbone (Amarillo)** | 🔵 **Anillos Metro (Cian)**")
    
    deck = render_national_network_deck(city_selected, pitch=0.0, layer_filter=layer_option)
    st.pydeck_chart(deck, use_container_width=True)

    # Detalle de capas de arquitectura
    st.markdown("---")
    st.subheader("📚 Especificaciones Técnicas por Capa de Red (Arquitectura SOMOS Internet)")

    col_c1, col_c2, col_c3 = st.columns(3)

    with col_c1:
        st.markdown("#### 🟡 1. Backbone Nacional Redundante")
        st.info("**Tecnología**: DWDM / ROADM 400Gbps por lambda\n\n"
                "**Topología**: Malla de anillos redundantes sobre carreteras federales (57D, 15D, 80D) con rutas 1+1 disjuntas\n\n"
                "**Disponibilidad Target**: **99.999%** (Cinco nueves)")

    with col_c2:
        st.markdown("#### 🔵 2. Distribución Metro (Redes Activas)")
        st.success("**Tecnología**: IP/MPLS + Ethernet Metro Activo a 100G\n\n"
                   "**Protección**: Anillos cerrados ERPS (ITU-T G.8032) con conmutación < 50ms\n\n"
                   "**Infraestructura**: Compartición de postería CFE (Norma CFE-PROT-2024)")

    with col_c3:
        st.markdown("#### 🟢 3. Acceso FOA / AON Punto a Punto")
        st.warning("**Tecnología**: **Fibra Óptica Activa (FOA) / AON P2P** desde **MicroPOPs Energizados (Modelo SOMOS Colombia)**\n\n"
                   "**Garantía**: Hilo dedicado por cliente/edificio, **hasta 2 Gbps simétricos (Subida = Bajada)** sin saturación\n\n"
                   "**Eficiencia CAPEX**: Costo por casa pasada **CPHP <= $500 MXN**")

if __name__ == "__main__":
    st.set_page_config(page_title="SOMOS Internet - Arquitectura", layout="wide")
    render()
