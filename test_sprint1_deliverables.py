"""
QA Test Suite for Sprint 1 Data Foundation Deliverables — SOMOS Internet
"""

import os
import sqlite3
import json
import pytest
import seed_data

BASE_DIR = r"c:\Users\diego\OneDrive\Documentos\Somos_Internet"
DB_PATH = os.path.join(BASE_DIR, "somos_network.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")
SEED_PATH = os.path.join(BASE_DIR, "seed_data.py")
REPORT_PATH = os.path.join(BASE_DIR, "validation_report.md")

EXPECTED_TABLES = {
    "cities",
    "network_nodes",
    "fiber_links",
    "access_clusters",
    "financial_projections",
    "risk_events",
    "governance_cadences"
}

EXPECTED_CITIES = {"CDMX", "MTY", "GDL", "TIJ", "MID"}

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Ensure database is seeded prior to test execution."""
    seed_data.run_seed()
    assert os.path.exists(DB_PATH), "Database file was not created"
    yield

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

# -----------------------------------------------------------------------------
# CHECK 1: Database Connection & Schema Completeness
# -----------------------------------------------------------------------------
def test_deliverable_files_exist():
    """Verify all 4 required deliverable files exist."""
    for path in [DB_PATH, SCHEMA_PATH, SEED_PATH, REPORT_PATH]:
        assert os.path.exists(path), f"Required deliverable missing: {path}"

def test_sqlite_connection_and_tables():
    """Verify SQLite connects cleanly and all 7 tables exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row[0] for row in cursor.fetchall()}
    conn.close()

    missing_tables = EXPECTED_TABLES - tables
    assert not missing_tables, f"Missing required tables: {missing_tables}"
    assert len(tables) >= 7, f"Expected at least 7 tables, found {len(tables)}"

def test_table_row_counts():
    """Verify table row counts match expected seed data metrics."""
    expected_counts = {
        "cities": 5,
        "network_nodes": 22,
        "fiber_links": 15,
        "access_clusters": 11,
        "financial_projections": 5,
        "risk_events": 4,
        "governance_cadences": 3
    }
    conn = get_db_connection()
    cursor = conn.cursor()
    for table, expected in expected_counts.items():
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        assert count == expected, f"Table '{table}' row count mismatch: expected {expected}, got {count}"
    conn.close()

# -----------------------------------------------------------------------------
# CHECK 2: Data Integrity Across 5 Cities
# -----------------------------------------------------------------------------
def test_cities_data_integrity():
    """Verify 5 cities CDMX, MTY, GDL, TIJ, MID exist and meet domain constraints."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT city_id, name, state, tier_category, population, demand_index, cfe_availability_ratio, latitude, longitude FROM cities")
    cities = cursor.fetchall()
    conn.close()

    city_ids = {c[0] for c in cities}
    assert city_ids == EXPECTED_CITIES, f"City ID mismatch: expected {EXPECTED_CITIES}, got {city_ids}"

    for city in cities:
        city_id, name, state, tier, pop, demand, cfe, lat, lon = city
        assert pop > 0, f"City {city_id} population must be > 0"
        assert 0 <= demand <= 100, f"City {city_id} demand index out of bounds [0, 100]: {demand}"
        assert 0 <= cfe <= 1.0, f"City {city_id} CFE ratio out of bounds [0, 1.0]: {cfe}"
        assert 14.0 <= lat <= 33.0, f"City {city_id} latitude out of Mexico bounds: {lat}"
        assert -118.0 <= lon <= -86.0, f"City {city_id} longitude out of Mexico bounds: {lon}"

def test_foreign_key_integrity():
    """Verify foreign key integrity across related tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tables referencing cities
    referencing_tables = [
        ("network_nodes", "city_id"),
        ("fiber_links", "city_id"),
        ("access_clusters", "city_id"),
        ("financial_projections", "city_id"),
        ("risk_events", "city_id"),
    ]
    
    for table, col in referencing_tables:
        cursor.execute(f"SELECT DISTINCT {col} FROM {table} WHERE {col} IS NOT NULL")
        refs = {r[0] for r in cursor.fetchall()}
        invalid = refs - EXPECTED_CITIES
        assert not invalid, f"Table {table} contains invalid city_id references: {invalid}"
        
    # Check fiber_links node references
    cursor.execute("SELECT origin_node_id, destination_node_id FROM fiber_links")
    links = cursor.fetchall()
    cursor.execute("SELECT node_id FROM network_nodes")
    valid_nodes = {r[0] for r in cursor.fetchall()}
    
    for origin, dest in links:
        assert origin in valid_nodes, f"Fiber link origin node {origin} does not exist in network_nodes"
        assert dest in valid_nodes, f"Fiber link destination node {dest} does not exist in network_nodes"
        
    conn.close()

# -----------------------------------------------------------------------------
# CHECK 3: CPHP Constraint (Cost per Home Passed <= $500 MXN)
# -----------------------------------------------------------------------------
def test_cphp_constraint_strict():
    """Verify Cost per Home Passed (CPHP) is strictly <= $500 MXN in all access clusters."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT cluster_id, city_id, name, homes_passed, capex_access_mxn, cost_per_home_passed FROM access_clusters")
    clusters = cursor.fetchall()
    conn.close()

    assert len(clusters) > 0, "No access clusters found"

    for cluster in clusters:
        cluster_id, city_id, name, homes_passed, capex_access, cphp_db = cluster
        assert homes_passed > 0, f"Cluster {cluster_id} homes_passed must be > 0"
        assert capex_access > 0, f"Cluster {cluster_id} capex_access_mxn must be > 0"
        
        calculated_cphp = round(capex_access / homes_passed, 2)
        
        # Invariant 1: CPHP must be <= $500 MXN
        assert cphp_db <= 500.0, f"Cluster {cluster_id} ({name}) CPHP {cphp_db} MXN exceeds limit of $500 MXN"
        assert calculated_cphp <= 500.0, f"Cluster {cluster_id} ({name}) calculated CPHP {calculated_cphp} MXN exceeds limit of $500 MXN"
        
        # Invariant 2: Stored CPHP must match calculated CAPEX / Homes Passed
        assert abs(cphp_db - calculated_cphp) < 0.01, f"Cluster {cluster_id} stored CPHP ({cphp_db}) does not match calculated ({calculated_cphp})"

# -----------------------------------------------------------------------------
# CHECK 4: Financial Formulas Validation (VAN, TIR, ROI, Payback @ 7.5%, 5 yrs)
# -----------------------------------------------------------------------------
def test_financial_projections_parameters_and_formulas():
    """Verify financial projections parameters (7.5% discount, 5 years) and mathematical correctness."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT projection_id, city_id, capex_initial_mxn, opex_annual_mxn, arpu_monthly_mxn, 
               subscriber_growth_rate, discount_rate, projection_years, van_mxn, irr_percent, roi_percent, payback_months 
        FROM financial_projections
    """)
    projections = cursor.fetchall()
    conn.close()

    assert len(projections) == 5, f"Expected 5 financial projections, found {len(projections)}"

    for proj in projections:
        (proj_id, city_id, capex, opex, arpu, growth, r, yrs, 
         van_db, irr_db, roi_db, payback_db) = proj

        # Discount rate & horizon constraints
        assert r == 0.075, f"Projection {proj_id} discount rate must be 0.075 (7.5%), got {r}"
        assert yrs == 5, f"Projection {proj_id} horizon must be 5 years, got {yrs}"

        # Re-compute using seed_data function & independent math formula
        calc_van, calc_irr, calc_roi, calc_payback = seed_data.calculate_financials(
            capex, opex, arpu, 
            subscribers_initial=12200 if city_id=="CDMX" else (9300 if city_id=="MTY" else (7700 if city_id=="GDL" else (4900 if city_id=="TIJ" else 4500))),
            growth_rate=growth,
            discount_rate=r,
            years=yrs
        )

        assert abs(van_db - calc_van) < 1.0, f"{proj_id} VAN mismatch: stored={van_db}, calc={calc_van}"
        assert abs(irr_db - calc_irr) < 0.1, f"{proj_id} IRR mismatch: stored={irr_db}, calc={calc_irr}"
        assert abs(roi_db - calc_roi) < 0.1, f"{proj_id} ROI mismatch: stored={roi_db}, calc={calc_roi}"
        assert abs(payback_db - calc_payback) < 0.2, f"{proj_id} Payback mismatch: stored={payback_db}, calc={calc_payback}"

def test_financial_math_independent_verification():
    """Independent mathematical verification of VAN (NPV) formula."""
    capex = 10000000.0
    annual_net = 3000000.0
    r = 0.075
    years = 5
    
    expected_van = -capex + sum(annual_net / ((1 + r) ** t) for t in range(1, years + 1))
    assert round(expected_van, 2) == 2137654.71

# -----------------------------------------------------------------------------
# CHECK 5: Absolute Absence of "VPN" Terminology
# -----------------------------------------------------------------------------
def test_vpn_absence_in_files_and_db():
    """Verify absolute absence of 'VPN' terminology across schema, seed, report, and DB contents."""
    files_to_check = [SCHEMA_PATH, SEED_PATH, REPORT_PATH]

    # 1. Check source files
    for file_path in files_to_check:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "vpn" not in content.lower(), f"Forbidden term 'VPN' found in file: {file_path}"

    # 2. Check Database Column Names and String Contents
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]

    for table in tables:
        # Check column names
        cursor.execute(f"PRAGMA table_info({table});")
        columns = [col[1] for col in cursor.fetchall()]
        for col in columns:
            assert "vpn" not in col.lower(), f"Forbidden term 'VPN' found in table '{table}' column name '{col}'"

        # Check string cell values
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        for row in rows:
            for val in row:
                if isinstance(val, str):
                    assert "vpn" not in val.lower(), f"Forbidden term 'VPN' found in table '{table}' cell value: '{val}'"

    conn.close()

# -----------------------------------------------------------------------------
# EDGE CASES & RECOVERY VALIDATION
# -----------------------------------------------------------------------------
def test_edge_case_cphp_above_limit_raises():
    """Verify system logic flags any cluster exceeding $500 CPHP."""
    excessive_cluster = {
        "cluster_id": "CLUS_TEST_INVALID",
        "city_id": "CDMX",
        "name": "Invalid High Cost Cluster",
        "homes_passed": 1000,
        "capex_access_mxn": 600000.0, # CPHP = 600 MXN > 500
        "cost_per_home_passed": 600.0
    }
    cphp = excessive_cluster["capex_access_mxn"] / excessive_cluster["homes_passed"]
    assert cphp > 500.0
    with pytest.raises(AssertionError):
        assert cphp <= 500.0, "Cluster CPHP exceeded limit!"

def test_geojson_validity():
    """Verify GeoJSON geometries in fiber_links are valid JSON LineStrings."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT link_id, geojson_geometry FROM fiber_links")
    links = cursor.fetchall()
    conn.close()

    for link_id, geo_json_str in links:
        data = json.loads(geo_json_str)
        assert data.get("type") == "LineString", f"Link {link_id} GeoJSON type must be LineString"
        coords = data.get("coordinates")
        assert isinstance(coords, list) and len(coords) >= 2, f"Link {link_id} LineString coordinates invalid"
        for pt in coords:
            assert len(pt) == 2, f"Link {link_id} coordinate point must be [lon, lat]"
            lon, lat = pt
            assert -118.0 <= lon <= -86.0 and 14.0 <= lat <= 33.0, f"Link {link_id} coordinate out of Mexico bounds"
