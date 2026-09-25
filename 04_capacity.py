"""
=====================================================================
SOMOS Internet — Expansión Nacional de Red de Fibra Óptica (México)
Sprint 4: Streamlit Frontend — Módulo 04: Capacidad & Crisis Protocol
Con KPIs de Red & Operativos de Crisis y Modelo de Medición OTDR Híbrido
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
        st.error("⚠️ **Escenario Simulado**: Corte de fibra óptica por obra civil de terceros en el enlace Backbone Nacional.")

        risk_eng = RiskEngine()
        link_sel = st.selectbox("Seleccionar Tramo Backbone Afectado:", ["LINK_BB_CDMX_GDL", "LINK_BB_CDMX_MTY", "LINK_BB_GDL_TIJ"])
        crisis_data = risk_eng.simulate_backbone_crisis_protocol_2h(link_sel)

        st.markdown("---")
        st.markdown("### 📊 Matriz de KPIs Críticos de Crisis (Red vs Operativos)")
        st.write("Medidores de desempeño prioritarios para salvaguardar la disponibilidad del 99.999% y minimizar el MTTR:")

        # =====================================================================
        # BLOQUE DE KPIS DE RED Y OPERATIVOS
        # =====================================================================
        col_kpi_red, col_kpi_ops = st.columns(2)

        with col_kpi_red:
            st.markdown("""
                <div style="background-color: #0f2b1d; border-left: 5px solid #00f5d4; padding: 15px; border-radius: 6px;">
                    <span style="font-size: 16px; color: #00f5d4; font-weight: bold;">🌐 Top 3 KPIs de Red (Infraestructura & Conmutación)</span>
                </div>
            """, unsafe_allow_html=True)
            
            st.metric(
                label="1. TTR (Time to Re-route / Conmutación 1+1)",
                value="< 50 ms",
                delta="Conmutación Óptica Automática DWDM / ERPS",
                delta_color="normal"
            )
            st.caption("⏱️ **Objetivo**: Redireccionar el tráfico por la Ruta B disjunta de forma imperceptible para el usuario sin caída de sesiones.")

            st.metric(
                label="2. Disponibilidad Acumulada de Red (SLA Uptime)",
                value="99.999 %",
                delta="Cinco Nueves (Max 5.26 min/año)",
                delta_color="normal"
            )
            st.caption("🔒 **Objetivo**: Garantía contractual para clientes FTTB/Enterprise AON P2P.")

            st.metric(
                label="3. Pérdida Máxima por Fusión (Splice Loss Index)",
                value="≤ 0.05 dB",
                delta="Empalme Limpio Certificado",
                delta_color="normal"
            )
            st.caption("📉 **Objetivo**: Asegurar que la reparación física no introduzca atenuación en la ventana de 1550 nm.")

        with col_kpi_ops:
            st.markdown("""
                <div style="background-color: #3d2600; border-left: 5px solid #ffb703; padding: 15px; border-radius: 6px;">
                    <span style="font-size: 16px; color: #ffb703; font-weight: bold;">🛠️ Top 3 KPIs Operativos (Campo & Mantenimiento)</span>
                </div>
            """, unsafe_allow_html=True)

            st.metric(
                label="1. MTTD (Mean Time to Detect / Detección iOTDR)",
                value="< 5 min",
                delta="Telemetría iOTDR 1625nm Out-of-band",
                delta_color="normal"
            )
            st.caption("🎯 **Objetivo**: Ubiación geográfica exacta (GPS) del corte desde el MicroPOP/NOC en menos de 5 minutos.")

            st.metric(
                label="2. TTA (Time to Arrive / Arribo de Brigada a Sitio)",
                value="< 45 min",
                delta="Despacho Urgente NOC / Campo",
                delta_color="normal"
            )
            st.caption("🚚 **Objetivo**: Arribo de la cuadrilla de empalme con fusionadora al punto de falla.")

            st.metric(
                label="3. MTTR (Mean Time to Repair / Reparación Física)",
                value="< 120 min",
                delta="Restauración Total en 2 Horas",
                delta_color="normal"
            )
            st.caption("🛠️ **Objetivo**: Fusión física de hilos, prueba de certificación OTDR y entrega del enlace a producción.")

        st.markdown("---")
        st.markdown("### 📡 Estrategia de Medición OTDR Híbrida (Interna + Externa)")
        
        col_otdr1, col_otdr2 = st.columns(2)

        with col_otdr1:
            st.info("""
                **🛰️ Medición Interna Automatizada (iOTDR / RTU)**
                - **Ubicación**: Integrado en transceptores SFP del MicroPOP / DWDM.
                - **Longitud de Onda**: *Out-of-band* a **1625 nm** (Monitoreo en vivo 24/7 sin afectar datos).
                - **Propósito**: Detección instantánea del corte y cálculo automático de distancia GPS al NOC en < 1 min.
            """)

        with col_otdr2:
            st.success("""
                **🧰 Medición Tradicional de Campo (OTDR Portátil EXFO / VIAVI)**
                - **Ubicación**: Reflectómetro portátil en manos de la brigada de campo.
                - **Longitud de Onda**: *In-band* en **1310 / 1550 nm**.
                - **Propósito**: Guiar la fusión física hilo por hilo en sitio y certificar la entrega técnica (`.SOR`) a CFE.
            """)

        st.markdown("---")
        st.markdown("### ⏱️ Cronograma de Acción Ejecutiva (0 a 120 Minutos)")

        for step in crisis_data["timeline_first_2h"]:
            st.markdown(f"#### 🔹 {step['minute_range']} — {step['phase']} `{step['status']}`")
            for act in step["actions"]:
                st.write(f"- {act}")
            st.markdown("---")

if __name__ == "__main__":
    st.set_page_config(page_title="SOMOS Internet - Capacidad & Crisis", layout="wide")
    render()
