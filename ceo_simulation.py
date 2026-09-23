"""
=====================================================================
SOMOS Internet — Expansión Nacional de Red de Fibra Óptica (México)
Sprint 6: CEO Simulation Mode (ceo_simulation.py)
=====================================================================
Módulo de Simulación en Tiempo Real para la Entrevista Ejecutiva
"""

import streamlit as st
from finance_engine import FinanceEngine
from pydeck_layers import render_national_network_deck

def render():
    st.title("💼 Módulo Simulador CEO & Boardroom (Entrevista Ejecutiva)")
    st.caption("Herramienta interactiva de simulación de hipótesis macroeconómicas y operativas en tiempo real")

    st.markdown("### 🎛️ Panel de Control de Hipótesis Macro y Operativas (Sensibilidad)")

    col_s1, col_s2, col_s3 = st.columns(3)

    with col_s1:
        capex_mult = st.slider("Ajuste de CAPEX (%)", 70.0, 150.0, 100.0, 5.0, format="%.0f%%") / 100.0
        opex_mult = st.slider("Ajuste de OPEX (%)", 70.0, 150.0, 100.0, 5.0, format="%.0f%%") / 100.0

    with col_s2:
        arpu_mult = st.slider("Ajuste de ARPU (%)", 80.0, 130.0, 100.0, 5.0, format="%.0f%%") / 100.0
        churn_pct = st.slider("Tasa Anual de Churn (%)", 1.0, 15.0, 5.0, 0.5, format="%.1f%%")

    with col_s3:
        wacc_rate = st.slider("Tasa de Descuento WACC (VAN)", 5.0, 12.0, 7.5, 0.5, format="%.1f%%") / 100.0
        growth_boost = st.slider("Boost de Crecimiento Suscriptores (%)", -10.0, 20.0, 0.0, 1.0, format="%.0f%%") / 100.0

    fin_engine = FinanceEngine()
    analysis = fin_engine.run_full_financial_analysis(
        discount_rate=wacc_rate,
        arpu_multiplier=arpu_mult,
        opex_multiplier=opex_mult
    )

    # Recalculate with CAPEX multiplier
    adj_total_capex = analysis["total_capex_national_mxn"] * capex_mult
    adj_total_van = analysis["total_van_national_mxn"] * (arpu_mult / capex_mult)
    adj_roi = ((adj_total_van / adj_total_capex) * 100.0) if adj_total_capex > 0 else 0.0

    st.markdown("---")
    st.subheader("📊 Resultados de Simulación en Tiempo Real")

    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
    with col_r1:
        st.metric("CAPEX Nacional Simulado", f"${adj_total_capex:,.0f} MXN", delta=f"{(capex_mult - 1.0)*100:+.0f}%")
    with col_r2:
        st.metric(f"VAN Simulado (r={wacc_rate*100:.1f}%)", f"${adj_total_van:,.0f} MXN", delta="Rentable" if adj_total_van > 0 else "Riesgo", delta_color="normal" if adj_total_van > 0 else "inverse")
    with col_r3:
        st.metric("ROI Simulado a 5 Años", f"{adj_roi:.1f}%")
    with col_r4:
        st.metric("Payback Promedio", f"{33.0 / (arpu_mult):.1f} meses")

    st.markdown("---")
    col_sim_map, col_sim_table = st.columns([6, 6])

    with col_sim_map:
        st.markdown("### 🗺️ Visualización de Red Nacional")
        deck = render_national_network_deck("MEXICO")
        st.pydeck_chart(deck, use_container_width=True)

    with col_sim_table:
        st.markdown("### 📋 Desglose Simulado por Ciudad")
        sim_breakdown = []
        for city in analysis["city_breakdown"]:
            c_capex = city["capex_initial_mxn"] * capex_mult
            c_van = city["van_mxn"] * (arpu_mult / capex_mult)
            c_roi = ((c_van / c_capex) * 100.0) if c_capex > 0 else 0.0
            sim_breakdown.append({
                "city_name": city["city_name"],
                "tier_category": city["tier_category"],
                "capex_simulated_mxn": c_capex,
                "van_simulated_mxn": c_van,
                "roi_simulated_percent": c_roi,
                "payback_months": city["payback_months"]
            })

        st.dataframe(
            sim_breakdown,
            column_config={
                "city_name": "Ciudad",
                "tier_category": "Tier",
                "capex_simulated_mxn": st.column_config.NumberColumn("CAPEX Simulado", format="$%.0f"),
                "van_simulated_mxn": st.column_config.NumberColumn("VAN Simulado", format="$%.0f"),
                "roi_simulated_percent": st.column_config.NumberColumn("ROI Simulado", format="%.1f%%"),
                "payback_months": st.column_config.NumberColumn("Payback", format="%.0fm")
            },
            use_container_width=True
        )

if __name__ == "__main__":
    st.set_page_config(page_title="SOMOS Internet - Simulador CEO", layout="wide")
    render()
