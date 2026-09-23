"""
=====================================================================
SOMOS Internet — Expansión Nacional de Red de Fibra Óptica (México)
Sprint 4: Master Application Controller (app.py)
=====================================================================
"""

import streamlit as st
import os

# Configuración de Página Principal
st.set_page_config(
    page_title="SOMOS Internet — Expansión Nacional Fibra Óptica",
    page_icon="📶",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS Corporativos SOMOS Internet
st.markdown("""
    <style>
        .main {
            background-color: #0e1117;
        }
        .stMetric {
            background-color: #161b22;
            padding: 12px;
            border-radius: 8px;
            border: 1px solid #30363d;
        }
        .stSelectbox, .stSlider {
            background-color: #161b22;
            border-radius: 6px;
        }
        .sidebar .sidebar-content {
            background-color: #0d1117;
        }
    </style>
""", unsafe_allow_html=True)

# Importar Módulos con Recarga Dinámica (Previene Caché de Capas 3D Antiguas)
import importlib
import pydeck_layers
import map_service

importlib.reload(map_service)
importlib.reload(pydeck_layers)

mod_01 = importlib.import_module("01_architecture")
mod_02 = importlib.import_module("02_planning")
mod_03 = importlib.import_module("03_rollout")
mod_04 = importlib.import_module("04_capacity")
mod_05 = importlib.import_module("05_risk")
mod_06 = importlib.import_module("06_executive")
mod_07 = importlib.import_module("ceo_simulation")

importlib.reload(mod_01)
importlib.reload(mod_02)
importlib.reload(mod_03)
importlib.reload(mod_04)
importlib.reload(mod_05)
importlib.reload(mod_06)
importlib.reload(mod_07)

# Sidebar — Logo Corporativo y Navegación
logo_path = os.path.join(os.path.dirname(__file__), "logo.jpg")
if not os.path.exists(logo_path):
    logo_path = os.path.join(os.path.dirname(__file__), "Logo.gif")

if os.path.exists(logo_path):
    st.sidebar.image(logo_path, use_container_width=True)
else:
    st.sidebar.title("📶 SOMOS Internet")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🗺️ Navegación de Módulos")

module_choice = st.sidebar.radio(
    "Seleccionar Módulo del Sistema:",
    [
        "01: Arquitectura & Topología",
        "02: Estrategia & Trade-offs",
        "03: Modelo Operativo & Despliegue",
        "04: Capacidad & Crisis Protocol",
        "05: Gobernanza & Matriz de Riesgos",
        "06: Dashboard Ejecutivo Board",
        "07: Simulador CEO & Boardroom"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("👤 **Rol**: Coordinador de Planeación y Expansión de Red FTTH\n\n"
               "🏢 **Empresa**: SOMOS Internet México\n\n"
               "🎯 **Costo/Casa Pasada**: < $500 MXN\n\n"
               "📊 **Métricas**: VAN, TIR, ROI, Payback")

# Enrutamiento de Módulos
if module_choice.startswith("01"):
    mod_01.render()
elif module_choice.startswith("02"):
    mod_02.render()
elif module_choice.startswith("03"):
    mod_03.render()
elif module_choice.startswith("04"):
    mod_04.render()
elif module_choice.startswith("05"):
    mod_05.render()
elif module_choice.startswith("06"):
    mod_06.render()
elif module_choice.startswith("07"):
    mod_07.render()
