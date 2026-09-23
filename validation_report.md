# Reporte de Validación de Base de Datos — Sprint 1: Data Foundation

**Proyecto**: Expansión Nacional de Red de Fibra Óptica (México)  
**Empresa**: SOMOS Internet  
**Base de Datos**: `somos_network.db` (SQLite 3 Local) + `schema.sql` (Supabase PostgreSQL Ready)  
**Estado**: Sprint 1 — Completado / En Evaluación  

---

## 1. Resumen de Tablas e Integridad Referencial

| Tabla | Registros | Clave Primaria | Claves Foráneas | Estado Integridad |
| :--- | :---: | :--- | :--- | :---: |
| `cities` | 5 | `city_id` | N/A | ✅ Valido |
| `network_nodes` | 11 | `node_id` | `city_id` -> `cities` | ✅ Valido |
| `fiber_links` | 10 | `link_id` | `origin_node_id`, `destination_node_id` | ✅ Valido |
| `access_clusters` | 11 | `cluster_id` | `city_id` -> `cities` | ✅ Valido |
| `financial_projections` | 5 | `projection_id` | `city_id` -> `cities` | ✅ Valido |
| `risk_events` | 4 | `risk_id` | `city_id` -> `cities` | ✅ Valido |
| `governance_cadences` | 3 | `cadence_id` | N/A | ✅ Valido |

---

## 2. Validación de Reglas Invariantes de Negocio

### 2.1 Verificación de Costo por Casa Pasada ($CPHP$)
- **Regla**: El costo por casa pasada ($CPHP = \frac{\text{CAPEX Acceso}}{\text{Casas Pasadas}}$) debe ser **menor o igual a $500 MXN**.
- **Resultado de Consulta SQL**:
  - `CLUS_CDMX_POLANCO`: $420.00 MXN ✅
  - `CLUS_CDMX_CONDESA`: $430.00 MXN ✅
  - `CLUS_CDMX_SANTAFE`: $460.00 MXN ✅
  - `CLUS_MTY_SANPEDRO`: $440.00 MXN ✅
  - `CLUS_MTY_CUMBRES`: $410.00 MXN ✅
  - `CLUS_GDL_ZAPOPAN`: $420.00 MXN ✅
  - `CLUS_GDL_PROVIDENCIA`: $430.00 MXN ✅
  - `CLUS_TIJ_OTAY`: $450.00 MXN ✅
  - `CLUS_TIJ_CABAÑAS`: $460.00 MXN ✅
  - `CLUS_MID_ALTABRISA`: $390.00 MXN ✅
  - `CLUS_MID_TEMOZON`: $410.00 MXN ✅
- **Veredicto**: 100% de los clusters cumplen con el estándar $CPHP \le \$500 \text{ MXN}$.

### 2.2 Verificación de Nomenclatura Financiera (Uso Exclusivo de VAN)
- **Búsqueda en Código y Esquema**: Nomenclatura VAN (Valor Actual Neto) verificada en el 100% de tablas y archivos.
- **Métricas Registradas**: **VAN** (Valor Actual Neto), **TIR / IRR** (Tasa Interna de Retorno), **ROI** (Retorno de Inversión) y **Payback** (recuperación en meses).
- **Parámetros**: Tasa de descuento $r = 7.5\%$ anual; Proyección $t = 5$ años.

---

## 3. Instrucciones de Migración a Supabase (PostgreSQL / INEGI Ready)

Si durante las siguientes fases o en producción se requiere migrar de la base de datos SQLite local a **Supabase (PostgreSQL / PostGIS)**:

1. Crear un proyecto nuevo en [Supabase Console](https://supabase.com).
2. Abrir el **SQL Editor** de Supabase.
3. Copiar y ejecutar las sentencias DDL contenidas en [`schema.sql`](file:///c:/Users/diego/OneDrive/Documentos/Somos_Internet/schema.sql).
4. Opcional: Para activar soporte espacial nativo en Supabase, ejecutar previamente `CREATE EXTENSION IF NOT EXISTS postgis;` y reemplazar la columna `geojson_geometry TEXT` por `geometry(LineString, 4326)`.
5. Ejecutar `python seed_data.py` cambiando la cadena de conexión mediante `psycopg2` o la API de Supabase.
