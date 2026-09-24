"""
=====================================================================
SOMOS Internet — Expansión Nacional de Red de Fibra Óptica (México)
Sprint 4: Streamlit Frontend — Módulo 03: Modelo Operativo & Despliegue
=====================================================================
"""

import streamlit as st

def render():
    st.title("🏗️ Módulo 3: Modelo Operativo de Despliegue & Permisos CFE")
    st.caption("Estructura de ejecución por fases, coordinación CFE y gestión de contratistas (Pregunta 3 del Examen Técnico)")

    st.markdown("### 🔄 5 Fases del Modelo de Despliegue Nacional")

    phases = [
        ("1. Planeación & Diseño (0 - 4 sem)", "Levantamiento de infraestructura CFE existente, ingeniería de detalle (GIS), cálculo de cargas mecánicas en postería norma CFE-PROT-2024."),
        ("2. Gestión de Permisos (4 - 12 sem)", "Trámite de convenios de adosamiento con divisiones regionales de CFE, permisos municipales de paso de vía y licencias urbanas."),
        ("3. Construcción & Tendido (12 - 20 sem)", "Tendido de cable de fibra óptica (Backbone/Metro), instalación de herrajes, cajas de empalme y colocación de splitters de acceso."),
        ("4. Empalme & Activación (20 - 24 sem)", "Fusión de hilos de fibra óptica, pruebas de reflectometría OTDR, certificación de enlace y comisión de nodos POP/Metro."),
        ("5. Entrega & Operación (24+ sem)", "Paso de la red a producción, monitoreo 24/7 en NOC, mantenimiento preventivo/correctivo y habilitación comercial de clientes.")
    ]

    for title, desc in phases:
        with st.expander(f"📍 {title}", expanded=True):
            st.write(desc)

    st.markdown("---")
    st.subheader("⚖️ Centralización Ejecutiva vs Ejecución Regional Local")

    col_cent, col_loc = st.columns(2)

    with col_cent:
        st.markdown("#### 🎯 Decisiones Centralizadas (Headquarters)")
        st.info("- **Estándares de Ingeniería & Red**: Arquitectura DWDM/ERPS/FOA AON P2P estandarizada.\n"
                "- **Negociación Nacional CFE**: Convenio marco corporativo de precios de adosamiento.\n"
                "- **Asignación de CAPEX**: Priorización nacional basada en VAN/ROI.\n"
                "- **Homologación de Proveedores**: Homologación Tier 1 de fabricantes (Cisco, Huawei, Corning).")

    with col_loc:
        st.markdown("#### 🛠️ Ejecución Local (Gerencias Regionales)")
        st.success("- **Gestión en Campo**: Supervisión directa de contratistas de tendido.\n"
                   "- **Relación con Autoridades Municipales**: Tramitación de licencias de obra civil local.\n"
                   "- **Respuesta a Fichas de Incidencia**: Brigadas de empalme y mantenimiento 24/7.\n"
                   "- **Atención a Clientes Locales**: Coordinación de instalaciones de última milla.")

    st.markdown("---")
    st.subheader("📋 Garantía de Calidad y Cumplimiento CFE")
    st.warning("⚠️ **Normativa Obligatoria CFE-PROT-2024**: Todo adosamiento debe cumplir con la distancia mínima a líneas de media tensión (1.8m) y tensión máxima permitida por tramo.")

if __name__ == "__main__":
    st.set_page_config(page_title="SOMOS Internet - Despliegue", layout="wide")
    render()
