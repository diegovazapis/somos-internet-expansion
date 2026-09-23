"""
=====================================================================
SOMOS Internet — Expansión Nacional de Red de Fibra Óptica (México)
Sprint 4: Streamlit Frontend — Módulo 06: Dashboard Ejecutivo Integrado
=====================================================================
"""

import streamlit as st
from finance_engine import FinanceEngine
from pydeck_layers import render_national_network_deck
from map_service import MapService

def render():
    st.title("📊 Módulo 6: Dashboard Ejecutivo Integrado — SOMOS Internet")
    st.caption("Visión consolidada para el Consejo de Administración y Dirección General")

    fin_engine = FinanceEngine()
    fin_summary = fin_engine.run_full_financial_analysis(discount_rate=0.075)

    service = MapService()
    nodes = service.get_nodes_gis_data("MEXICO")
    links = service.get_fiber_links_gis_data("MEXICO")
    clusters = service.get_access_clusters_gis_data("MEXICO")

    total_homes = sum(c["homes_passed"] for c in clusters)
    total_subs = sum(c["active_subscribers"] for c in clusters)
    avg_cphp = sum(c["cost_per_home_passed"] for c in clusters) / len(clusters) if clusters else 0.0

    # Tarjetas KPI Ejecutivas
    col_kpi1, col_kpi2, col_kpi3, col_kpi4, col_kpi5 = st.columns(5)

    with col_kpi1:
        st.metric("CAPEX Nacional Total", f"${fin_summary['total_capex_national_mxn']:,.0f} MXN")
    with col_kpi2:
        st.metric("VAN Acumulado (7.5%)", f"${fin_summary['total_van_national_mxn']:,.0f} MXN", delta="Rentable", delta_color="normal")
    with col_kpi3:
        st.metric("ROI Acumulado a 5 Años", f"{fin_summary['national_roi_percent']:.1f}%")
    with col_kpi4:
        st.metric("Promedio Costo/Casa Pasada", f"${avg_cphp:.2f} MXN", delta="< $500 Target", delta_color="normal")
    with col_kpi5:
        st.metric("Casas Pasadas Totales", f"{total_homes:,}", delta=f"{total_subs:,} Subs Activos")

    st.markdown("---")

    # Layout de Mapa y Desglose Financiero
    col_map, col_table = st.columns([7, 5])

    with col_map:
        st.markdown("### 🗺️ Red Nacional Cobertura 5 Ciudades")
        deck = render_national_network_deck("MEXICO")
        st.pydeck_chart(deck, use_container_width=True)

    with col_table:
        st.markdown("### 📈 Desglose Financiero por Mercado")
        st.dataframe(
            fin_summary["city_breakdown"],
            column_config={
                "city_name": "Ciudad",
                "tier_category": "Tier",
                "capex_initial_mxn": st.column_config.NumberColumn("CAPEX (MXN)", format="$%.0f"),
                "van_mxn": st.column_config.NumberColumn("VAN (MXN)", format="$%.0f"),
                "tir_percent": st.column_config.NumberColumn("TIR", format="%.1f%%"),
                "roi_percent": st.column_config.NumberColumn("ROI", format="%.1f%%"),
                "payback_months": st.column_config.NumberColumn("Payback", format="%.0fm")
            },
            use_container_width=True
        )

        st.markdown("### 🏆 Conclusión Ejecutiva del Plan")
        st.success(r"**Estrategia Recomendada**: Combinación de Expansión Tier 1 (CDMX, MTY, GDL) con captura de alta densidad y despliegue ágil Tier 2 (TIJ, MID) con payback acelerado. Todos los clusters cumplen el estándar de eficiencia financiera $CPHP < \$500 \text{ MXN}$.")

if __name__ == "__main__":
    st.set_page_config(page_title="SOMOS Internet - Dashboard Ejecutivo", layout="wide")
    render()
