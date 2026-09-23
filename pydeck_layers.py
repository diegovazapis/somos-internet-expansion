"""
=====================================================================
SOMOS Internet — Expansión Nacional de Red de Fibra Óptica (México)
Sprint 3 & 6: GIS Layer — PyDeck Layers Builder (Versión 2D Limpia sobre Carreteras & MicroPOPs)
=====================================================================
"""

import pydeck as pdk
from map_service import MapService

def create_nodes_layer(nodes_data):
    """
    Crea la capa de Nodos de Red (POPs Nacionales, Cores Metro & MicroPOPs SOMOS Colombia).
    Utiliza ScatterplotLayer de alta visibilidad para mapa plano 2D.
    """
    return pdk.Layer(
        "ScatterplotLayer",
        data=nodes_data,
        get_position="coordinates",
        get_color="color",
        get_radius="radius",
        radius_scale=1,
        radius_min_pixels=8,
        radius_max_pixels=30,
        pickable=True,
        opacity=0.95,
        stroked=True,
        get_line_color=[255, 255, 255],
        line_width_min_pixels=2,
    )

def create_fiber_links_layer(links_data):
    """
    Crea la capa PathLayer para los Tramos de Fibra Óptica trazados sobre Carreteras Federales Reales.
    """
    return pdk.Layer(
        "PathLayer",
        data=links_data,
        get_path="path",
        get_color="color",
        get_width="width",
        width_scale=20,
        width_min_pixels=3,
        pickable=True,
        auto_highlight=True,
    )

def create_access_clusters_layer(clusters_data):
    """
    Crea la capa ScatterplotLayer para los Bloques de Acceso (Casas Pasadas & CPHP).
    """
    return pdk.Layer(
        "ScatterplotLayer",
        data=clusters_data,
        get_position="coordinates",
        get_color="color",
        get_radius="radius",
        radius_min_pixels=5,
        radius_max_pixels=20,
        pickable=True,
        opacity=0.7,
        stroked=True,
        get_line_color=[200, 200, 200],
        line_width_min_pixels=1,
    )

def render_national_network_deck(city_id="MEXICO", pitch=0.0, db_path=None, layer_filter="ALL"):
    """
    Ensambla el mapa interactivo en PyDeck con la topología de red SOMOS Internet sobre Carreteras en 2D Plano.
    Permite filtrar por capas específicas: ALL, BACKBONE, METRO, MICROPOP_ACCESS.
    """
    service = MapService(db_path=db_path)
    viewport = service.get_viewport_for_city(city_id)

    nodes = service.get_nodes_gis_data(city_id)
    links = service.get_fiber_links_gis_data(city_id)
    clusters = service.get_access_clusters_gis_data(city_id)

    if layer_filter == "BACKBONE":
        nodes = [n for n in nodes if n["node_type"] == "NATIONAL_POP"]
        links = [l for l in links if l["link_type"] == "BACKBONE_LONG_HAUL"]
        clusters = []
    elif layer_filter == "METRO":
        nodes = [n for n in nodes if n["node_type"] in ["METRO_CORE", "NATIONAL_POP"]]
        links = [l for l in links if l["link_type"] == "METRO_RING"]
        clusters = []
    elif layer_filter == "MICROPOP_ACCESS":
        nodes = [n for n in nodes if n["node_type"] == "MICRO_POP"]
        links = []
        # keep access clusters
    
    layers = []
    if links:
        layers.append(create_fiber_links_layer(links))
    if clusters and layer_filter in ["ALL", "MICROPOP_ACCESS"]:
        layers.append(create_access_clusters_layer(clusters))
    if nodes:
        layers.append(create_nodes_layer(nodes))

    initial_view_state = pdk.ViewState(
        latitude=viewport["latitude"],
        longitude=viewport["longitude"],
        zoom=viewport["zoom"],
        pitch=0.0, # Vista estrictamente 2D plana superior (Top-Down)
        bearing=0.0
    )

    tooltip = {
        "html": "<div style='color: #38bdf8; font-weight: bold; font-size: 13px;'>{name}</div><div style='color: #e2e8f0; font-size: 11px; margin-top: 3px;'>{tooltip_line1}</div><div style='color: #94a3b8; font-size: 11px; margin-top: 2px;'>{tooltip_line2}</div>",
        "style": {
            "backgroundColor": "#0b0f19",
            "color": "#ffffff",
            "border": "1px solid #1e293b",
            "borderRadius": "6px",
            "padding": "8px 12px",
            "boxShadow": "0 4px 6px -1px rgba(0, 0, 0, 0.5)"
        }
    }

    deck = pdk.Deck(
        layers=layers,
        initial_view_state=initial_view_state,
        map_style=pdk.map_styles.CARTO_DARK,
        tooltip=tooltip
    )
    return deck

if __name__ == "__main__":
    deck = render_national_network_deck("MEXICO")
    print("PyDeck map object constructed successfully for national network (2D Highway Mode).")
