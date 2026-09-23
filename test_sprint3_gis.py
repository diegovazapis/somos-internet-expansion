"""
=====================================================================
SOMOS Internet — Expansión Nacional de Red de Fibra Óptica (México)
Sprint 3 Unit Tests — GIS Layer Verification
=====================================================================
"""

import pytest
import json
from map_service import MapService
from pydeck_layers import render_national_network_deck

def test_map_service_viewports():
    service = MapService()
    cdmx = service.get_viewport_for_city("CDMX")
    assert cdmx["latitude"] == 19.4126
    assert cdmx["zoom"] == 11.2

def test_map_service_nodes():
    service = MapService()
    nodes = service.get_nodes_gis_data("CDMX")
    assert len(nodes) == 6
    for n in nodes:
        assert len(n["coordinates"]) == 2
        assert "color" in n

def test_map_service_links_geojson():
    service = MapService()
    links = service.get_fiber_links_gis_data("MEXICO")
    assert len(links) == 10
    for l in links:
        assert isinstance(l["path"], list)
        assert len(l["path"]) >= 2

def test_pydeck_deck_rendering():
    deck = render_national_network_deck("MEXICO")
    assert deck is not None
    assert len(deck.layers) == 3
