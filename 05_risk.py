"""
=====================================================================
SOMOS Internet — Expansión Nacional de Red de Fibra Óptica (México)
Sprint 4: Streamlit Frontend — Módulo 05: Gobernanza & Matriz de Riesgos
=====================================================================
"""

import streamlit as st
from risk_engine import RiskEngine
from governance_engine import GovernanceEngine

def render():
    st.title("🛡️ Módulo 5: Gobernanza del Proyecto & Matriz de Riesgos")
    st.caption("Estructura de gobierno, cadencias de seguimiento y mitigación de riesgos en México (Preguntas 4, 7, 8 y 9)")

    tab_gov, tab_risk = st.tabs(["🏛️ Gobernanza & Cadencias de Control", "⚠️ Matriz de Riesgos & Mitigación"])

    with tab_gov:
        st.subheader("🏛️ Cadencias de Control y Niveles de Decisión")

        gov_eng = GovernanceEngine()
        cadences = gov_eng.get_governance_cadences()

        for c in cadences:
            badge_color = "red" if c["level"] == "STRATEGIC" else ("blue" if c["level"] == "OPERATIONAL" else "green")
            st.markdown(f"#### 🏢 [{c['level']}] {c['forum_name']} ({c['frequency']})")
            st.write(f"**Participantes**: {c['participants']}")
            st.write(f"**KPIs Evaluados**: {c['kpis_reviewed']}")
            st.markdown("---")

        st.subheader("💰 Evaluador de Gate de Aprobación CAPEX")
        st.caption("Simula qué nivel de gobernanza requiere un proyecto según su monto presupuestal")

        col_amt, col_city = st.columns(2)
        with col_amt:
            capex_val = st.number_input("Monto de CAPEX del Proyecto (MXN):", min_value=500000.0, max_value=100000000.0, value=18000000.0, step=1000000.0)
        with col_city:
            city_val = st.selectbox("Ciudad Objetivo:", ["CDMX", "MTY", "GDL", "TIJ", "MID"])

        gate_res = gov_eng.evaluate_capex_approval_gate(capex_val, city_val, f"Expansión Fibra {city_val}")

        st.info(f"**Nivel de Gobernanza Requerido**: `{gate_res['required_level']}`\n\n"
                f"**Foro de Aprobación**: {gate_res['required_forum']}\n\n"
                f"**Aprobadores Autorizados**: {', '.join(gate_res['approvers'])}\n\n"
                f"**Tipo de Dictamen**: {gate_res['approval_type']}")

    with tab_risk:
        st.subheader("⚠️ Matriz de Riesgos Específicos en México")

        risk_eng = RiskEngine()
        matrix = risk_eng.get_risk_matrix()

        st.dataframe(
            matrix,
            column_config={
                "risk_id": "ID Riesgo",
                "category": "Categoría",
                "city_name": "Ciudad",
                "title": "Riesgo",
                "description": "Descripción",
                "severity": "Severidad",
                "probability": "Probabilidad",
                "mitigation_strategy": "Estrategia de Mitigación",
                "impact_score": st.column_config.NumberColumn("Score Impacto (1-10)", format="%d / 10")
            },
            use_container_width=True
        )

        st.markdown("### 🔧 Adaptación ante Restricciones (Pregunta 9)")
        st.markdown("- **Restricción de Permisos CFE/Municipales**: Se priorizan tramos con convenios ya aprobados y despliegue sobre postería existente.\n"
                    r"- **Limitaciones de Capacidad Operativa**: Despliegue faseado por clústeres residenciales de alta densidad ($CPHP < \$500 \text{ MXN}$)." "\n"
                    "- **Volatilidad Financiera**: Contratos de suministro de fibra óptica a precio cerrado a 12 meses.")

if __name__ == "__main__":
    st.set_page_config(page_title="SOMOS Internet - Gobernanza & Riesgos", layout="wide")
    render()
