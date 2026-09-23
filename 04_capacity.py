"""
=====================================================================
SOMOS Internet — Expansión Nacional de Red de Fibra Óptica (México)
Sprint 4: Streamlit Frontend — Módulo 04: Capacidad & Crisis Protocol
=====================================================================
"""

import streamlit as st
from capacity_engine import CapacityEngine
from risk_engine import RiskEngine

def render():
    st.title("📈 Módulo 4: Capacidad de Red & Protocolo de Crisis (Falla 2h)")
    st.caption("Planeación de escalabilidad de hilos/nodos y simulación de respuesta a crisis en Backbone (Preguntas 5 y 6)")

    tab_cap, tab_crisis = st.tabs(["📊 Planeación de Capacidad & Redundancia", "🚨 Simulador de Crisis Backbone (2 Horas)"])

    with tab_cap:
        st.subheader("🔍 Monitoreo de Ocupación de Nodos & Hilos de Fibra")
        cap_engine = CapacityEngine()
        threshold = st.slider("Umbral de Alerta de Ocupación (%)", 40.0, 90.0, 75.0, 5.0)

        analysis = cap_engine.analyze_network_capacity(threshold_percent=threshold)

        c_m1, c_m2, c_m3 = st.columns(3)
        with c_m1:
            st.metric("Total Nodos Monitoreados", analysis["total_nodes_monitored"])
        with c_m2:
            st.metric("Total Tramos Monitoreados", analysis["total_links_monitored"])
        with c_m3:
            st.metric("Alertas de Capacidad (> " + str(threshold) + "%)", analysis["node_high_utilization_alerts"] + analysis["link_high_utilization_alerts"])

        st.markdown("#### 🏢 Capacidad de Nodos (Gbps)")
        st.dataframe(
            analysis["nodes_detail"],
            column_config={
                "name": "Nodo",
                "city_id": "Ciudad",
                "node_type": "Tipo",
                "total_gbps": st.column_config.NumberColumn("Capacidad Total (Gbps)", format="%d Gbps"),
                "used_gbps": st.column_config.NumberColumn("Uso Actual (Gbps)", format="%d Gbps"),
                "utilization_percent": st.column_config.NumberColumn("Ocupación (%)", format="%.1f%%"),
                "redundancy_level": "Redundancia",
                "requires_expansion": "Alerta Expansión"
            },
            use_container_width=True
        )

        st.markdown("#### 🧵 Ocupación de Hilos de Fibra Óptica")
        st.dataframe(
            analysis["links_detail"],
            column_config={
                "name": "Tramo",
                "link_type": "Tipo Enlace",
                "distance_km": st.column_config.NumberColumn("Distancia (km)", format="%.1f km"),
                "total_strands": "Hilos Totales",
                "used_strands": "Hilos Usados",
                "strand_utilization_percent": st.column_config.NumberColumn("Ocupación (%)", format="%.1f%%"),
                "cfe_pole_agreement": "Convenio CFE",
                "status": "Estado"
            },
            use_container_width=True
        )

    with tab_crisis:
        st.subheader("🚨 Escenario de Crisis: Falla Crítica en Backbone (Primeras 2 Horas)")
        st.error("⚠️ **Escenario Simulado**: Corte de fibra óptica por obra civil de terceros en el enlace Backbone CDMX - Guadalajara.")

        risk_eng = RiskEngine()
        link_sel = st.selectbox("Seleccionar Tramo Backbone Afectado:", ["LINK_BB_CDMX_GDL", "LINK_BB_CDMX_MTY", "LINK_BB_GDL_TIJ"])
        crisis_data = risk_eng.simulate_backbone_crisis_protocol_2h(link_sel)

        col_sla1, col_sla2 = st.columns(2)
        with col_sla1:
            st.metric("Disponibilidad Target SLA", crisis_data["sla_availability_target"])
        with col_sla2:
            st.metric("Conmutación Automática DWDM 1+1", "< 50 ms", delta="Protección Activa", delta_color="normal")

        st.markdown("### ⏱️ Cronograma de Acción Ejecutiva (0 a 120 Minutos)")

        for step in crisis_data["timeline_first_2h"]:
            st.markdown(f"#### 🔹 {step['minute_range']} — {step['phase']} `{step['status']}`")
            for act in step["actions"]:
                st.write(f"- {act}")
            st.markdown("---")

if __name__ == "__main__":
    st.set_page_config(page_title="SOMOS Internet - Capacidad & Crisis", layout="wide")
    render()
