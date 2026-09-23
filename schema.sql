-- =====================================================================
-- SOMOS Internet — Expansión Nacional de Red de Fibra Óptica (México)
-- Schema DDL — Compatible con SQLite 3 y PostgreSQL / Supabase
-- Sprint 1: Data Foundation
-- =====================================================================

-- 1. Tabla de Ciudades Objetivo
CREATE TABLE IF NOT EXISTS cities (
    city_id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    state VARCHAR(50) NOT NULL,
    tier_category VARCHAR(20) NOT NULL CHECK (tier_category IN ('Tier 1', 'Tier 2', 'Optimización')),
    population INT NOT NULL,
    demand_index REAL NOT NULL CHECK (demand_index BETWEEN 0 AND 100),
    cfe_availability_ratio REAL NOT NULL CHECK (cfe_availability_ratio BETWEEN 0 AND 1),
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Tabla de Nodos de Red
CREATE TABLE IF NOT EXISTS network_nodes (
    node_id VARCHAR(20) PRIMARY KEY,
    city_id VARCHAR(10) NOT NULL REFERENCES cities(city_id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    node_type VARCHAR(30) NOT NULL CHECK (node_type IN ('NATIONAL_POP', 'METRO_CORE', 'DISTRIBUTION_HUB', 'MICRO_POP')),
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    total_capacity_gbps INT NOT NULL,
    used_capacity_gbps INT NOT NULL,
    redundancy_level VARCHAR(20) NOT NULL CHECK (redundancy_level IN ('2N', 'N+1', 'Unprotected')),
    status VARCHAR(20) DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'PLANNING', 'MAINTENANCE', 'DEGRADED'))
);

-- 3. Tabla de Tramos de Fibra Óptica (Backbone + Metro + Acceso)
CREATE TABLE IF NOT EXISTS fiber_links (
    link_id VARCHAR(30) PRIMARY KEY,
    city_id VARCHAR(10) REFERENCES cities(city_id) ON DELETE SET NULL,
    name VARCHAR(100) NOT NULL,
    origin_node_id VARCHAR(20) NOT NULL REFERENCES network_nodes(node_id),
    destination_node_id VARCHAR(20) NOT NULL REFERENCES network_nodes(node_id),
    link_type VARCHAR(30) NOT NULL CHECK (link_type IN ('BACKBONE_LONG_HAUL', 'METRO_RING', 'ACCESS_FEEDER')),
    distance_km REAL NOT NULL,
    strand_count INT NOT NULL,
    used_strand_count INT NOT NULL,
    cfe_pole_agreement VARCHAR(50) NOT NULL,
    deployment_cost_mxn REAL NOT NULL,
    geojson_geometry TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'OPERATIONAL' CHECK (status IN ('OPERATIONAL', 'CONSTRUCTION', 'FAULT', 'PLANNED'))
);

-- 4. Tabla de Bloques de Acceso (Casas Pasadas y Suscriptores)
CREATE TABLE IF NOT EXISTS access_clusters (
    cluster_id VARCHAR(20) PRIMARY KEY,
    city_id VARCHAR(10) NOT NULL REFERENCES cities(city_id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    homes_passed INT NOT NULL CHECK (homes_passed > 0),
    active_subscribers INT NOT NULL DEFAULT 0,
    arpu_monthly_mxn REAL NOT NULL DEFAULT 450.0,
    capex_access_mxn REAL NOT NULL,
    cost_per_home_passed REAL NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    status VARCHAR(20) DEFAULT 'ACTIVE'
);

-- 5. Tabla de Proyecciones Financieras Oficiales (VAN, TIR, ROI, Payback)
CREATE TABLE IF NOT EXISTS financial_projections (
    projection_id VARCHAR(30) PRIMARY KEY,
    city_id VARCHAR(10) NOT NULL REFERENCES cities(city_id) ON DELETE CASCADE,
    scenario_name VARCHAR(50) NOT NULL,
    capex_initial_mxn REAL NOT NULL,
    opex_annual_mxn REAL NOT NULL,
    arpu_monthly_mxn REAL NOT NULL,
    subscriber_growth_rate REAL NOT NULL,
    discount_rate REAL NOT NULL DEFAULT 0.075, -- 7.5% por defecto
    projection_years INT NOT NULL DEFAULT 5,
    van_mxn REAL NOT NULL, -- Valor Actual Neto (VAN)
    irr_percent REAL NOT NULL, -- Tasa Interna de Retorno (TIR)
    roi_percent REAL NOT NULL, -- Retorno de Inversión acumulado
    payback_months REAL NOT NULL, -- Período de recuperación en meses
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Tabla de Matriz de Riesgos
CREATE TABLE IF NOT EXISTS risk_events (
    risk_id VARCHAR(20) PRIMARY KEY,
    city_id VARCHAR(10) REFERENCES cities(city_id) ON DELETE SET NULL,
    category VARCHAR(30) NOT NULL CHECK (category IN ('REGULATORY', 'OPERATIONAL', 'TECHNICAL', 'FINANCIAL')),
    title VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
    probability VARCHAR(20) NOT NULL CHECK (probability IN ('HIGH', 'MEDIUM', 'LOW')),
    mitigation_strategy TEXT NOT NULL,
    impact_score INT NOT NULL CHECK (impact_score BETWEEN 1 AND 10)
);

-- 7. Tabla de Cadencias de Gobernanza del Proyecto
CREATE TABLE IF NOT EXISTS governance_cadences (
    cadence_id VARCHAR(20) PRIMARY KEY,
    level VARCHAR(20) NOT NULL CHECK (level IN ('STRATEGIC', 'OPERATIONAL', 'TACTICAL')),
    forum_name VARCHAR(100) NOT NULL,
    frequency VARCHAR(30) NOT NULL,
    participants TEXT NOT NULL,
    kpis_reviewed TEXT NOT NULL
);

-- Índices de Rendimiento Geoespacial y Consultas Frecuentes
CREATE INDEX IF NOT EXISTS idx_nodes_city ON network_nodes(city_id);
CREATE INDEX IF NOT EXISTS idx_links_city ON fiber_links(city_id);
CREATE INDEX IF NOT EXISTS idx_clusters_city ON access_clusters(city_id);
CREATE INDEX IF NOT EXISTS idx_financial_city ON financial_projections(city_id);
CREATE INDEX IF NOT EXISTS idx_links_nodes ON fiber_links(origin_node_id, destination_node_id);
