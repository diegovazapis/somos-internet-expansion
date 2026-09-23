"""
=====================================================================
SOMOS Internet — Expansión Nacional de Red de Fibra Óptica (México)
Sprint 4: Streamlit Frontend — Módulo 02: Estrategia & Trade-offs
=====================================================================
"""

import streamlit as st
from planning_engine import PlanningEngine
from finance_engine import FinanceEngine

def render():
    st.title("🎯 Módulo 2: Estrategia de Expansión & Trade-offs de Inversión")
    st.caption("Evaluación cuantitativa de escenarios de inversión (Pregunta 10 del Examen Técnico Executivo)")

    # Ponderaciones dinámicas con Sliders
    st.sidebar.markdown("### 🎛️ Ponderación de Variables Estratégicas")
    w_demand = st.sidebar.slider("Ponderación Demanda Comercial", 0.0, 1.0, 0.4, 0.05)
    w_cost = st.sidebar.slider("Ponderación Eficiencia CPHP", 0.0, 1.0, 0.3, 0.05)
    w_cfe = st.sidebar.slider("Ponderación Disponibilidad CFE", 0.0, 1.0, 0.3, 0.05)

    st.sidebar.markdown("---")
    discount_rate = st.sidebar.slider("Tasa de Descuento WACC (VAN)", 0.05, 0.12, 0.075, 0.005, format="%.3f")

    plan_engine = PlanningEngine()
    fin_engine = FinanceEngine()

    options = plan_engine.evaluate_expansion_options(
        weight_demand=w_demand, weight_cost=w_cost, weight_cfe=w_cfe
    )
    fin_summary = fin_engine.run_full_financial_analysis(discount_rate=discount_rate)

    st.markdown("### ⚖️ Comparativa de Opciones Estratégicas (CAPEX Limitado)")

    col_optA, col_optB, col_optC = st.columns(3)

    with col_optA:
        opt_a = options["Option_A_Tier1"]
        st.markdown(f"#### 🏢 {opt_a['name']}")
        st.write(opt_a['description'])
        st.metric("VAN Acumulado Estimado", f"${opt_a['total_van_mxn']:,.2f} MXN")
        st.metric("Score Estratégico", f"{opt_a['avg_strategic_score']} / 100")
        st.error(f"**Perfil de Riesgo**: {opt_a['risk_profile']}")
        st.markdown(f"**Enfoque Recomendado**: {opt_a['recommended_focus']}")

    with col_optB:
        opt_b = options["Option_B_Tier2"]
        st.markdown(f"#### 🚀 {opt_b['name']}")
        st.write(opt_b['description'])
        st.metric("VAN Acumulado Estimado", f"${opt_b['total_van_mxn']:,.2f} MXN")
        st.metric("Score Estratégico", f"{opt_b['avg_strategic_score']} / 100")
        st.warning(f"**Perfil de Riesgo**: {opt_b['risk_profile']}")
        st.markdown(f"**Enfoque Recomendado**: {opt_b['recommended_focus']}")

    with col_optC:
        opt_c = options["Option_C_Optimization"]
        st.markdown(f"#### ⚡ {opt_c['name']}")
        st.write(opt_c['description'])
        st.metric("VAN Acumulado Estimado", f"${opt_c['total_van_mxn']:,.2f} MXN")
        st.metric("Score Estratégico", f"{opt_c['avg_strategic_score']} / 100")
        st.success(f"**Perfil de Riesgo**: {opt_c['risk_profile']}")
        st.markdown(f"**Enfoque Recomendado**: {opt_c['recommended_focus']}")

    st.markdown("---")
    st.subheader("📊 Tabla de Desglose Financiero por Ciudad")

    city_data = fin_summary["city_breakdown"]
    st.dataframe(
        city_data,
        column_config={
            "city_name": "Ciudad",
            "tier_category": "Categoría Tier",
            "capex_initial_mxn": st.column_config.NumberColumn("CAPEX Inicial (MXN)", format="$%.2f"),
            "van_mxn": st.column_config.NumberColumn(f"VAN (r={discount_rate*100:.1f}%)", format="$%.2f"),
            "tir_percent": st.column_config.NumberColumn("TIR (%)", format="%.2f%%"),
            "roi_percent": st.column_config.NumberColumn("ROI (%)", format="%.2f%%"),
            "payback_months": st.column_config.NumberColumn("Payback (Meses)", format="%.1f m")
        },
        use_container_width=True
    )

if __name__ == "__main__":
    st.set_page_config(page_title="SOMOS Internet - Estrategia", layout="wide")
    render()
