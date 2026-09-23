# Architectural Decision Records (ADR) — SOMOS Internet

**Proyecto**: Expansión Nacional de Red de Fibra Óptica (México)  
**Empresa**: SOMOS Internet  
**Rol Ejecutivo**: Arquitecto de Expansión Nacional de Fibra Óptica  
**Estado**: Sprint 0 — En Revisión  

---

## ADR 001: Arquitectura de Red de Fibra Óptica Híbrida (Backbone + Metro + Acceso GPON/XGS-PON)

### Contexto
SOMOS Internet requiere una red de fibra óptica resiliente, escalable y eficiente en costo a nivel nacional en México, conectando inicialmente 5 ciudades clave: **CDMX, Monterrey, Guadalajara, Tijuana y Mérida**.

### Decisión
Se define una arquitectura jerárquica de 3 capas con topología redundante de doble anillo y mallas de transporte:
1. **Capa 1: Backbone Nacional (Long-Haul Transport)**
   - Topología en malla redundante conectando los POPs nacionales principales.
   - Tecnología: DWDM / ROADM con capacidad inicial de 400Gbps por lambda, escalable a Terabits.
   - Redundancia: Protección 1+1 en rutas ópticas físicamente disjuntas.
2. **Capa 2: Redes Metropolitanas (Metro Core & Distribution)**
   - Topología en anillos protectores autosuficientes (ERPS / G.8032) por ciudad.
   - Tecnología: IP/MPLS + Ethernet Metro 100G.
   - Integración con infraestructura existente: Compartición de infraestructura CFE (postería y canalizaciones) y ductos de terceros.
3. **Capa 3: Red de Acceso de Última Milla (FTTH / FTTB)**
   - Tecnología: GPON / XGS-PON simétrico.
   - Enfoque de eficiencia: Cobertura de bloques residenciales y empresariales con meta de costo de construcción por casa pasada (Cost per Home Passed) **menor a $500 MXN**.

### Consecuencias
- **Ventajas**: Disponibilidad de red de 99.999% (cinco nueves), convergencia en menos de 50ms ante cortes de fibra, bajo CAPEX por casa pasada.
- **Trade-offs**: Requiere contratos de compartición con CFE (permisos de uso de postes) y acuerdos de paso de vía locales.

---

## ADR 002: Estrategia de Persistencia de Datos Híbrida (SQLite Local + Schema Supabase PostgreSQL)

### Contexto
El MVP debe ejecutarse de forma rápida y autónoma en entornos de demostración u offline durante la entrevista ejecutiva, sin depender obligatoriamente de servicios en la nube activos, pero manteniendo compatibilidad con **Supabase PostgreSQL** e **INEGI / datos geoespaciales**.

### Decisión
- **Motor Principal MVP**: Base de datos relacional en **SQLite local** pre-cargada con datos semilla enriquecidos.
- **Compatibilidad Supabase**: Creación de archivo de script estándar `schema.sql` (PostgreSQL / PostGIS compatible) listo para ejecutarse en Supabase cuando se requiera migrar a producción o conectar datos reales de INEGI.
- **Rendimiento Geoespacial**: GeoJSON estandarizado con indexación espacial local en Python (`Shapely`, `pydeck`) para renderizado dinámico instantáneo en Streamlit.

---

## ADR 003: Estándar de Motores Financieros (VAN, TIR, ROI, Payback)

### Contexto
Es obligatorio mantener rigor técnico-financiero sustituyendo cualquier mención errónea de VPN por **VAN** (Valor Actual Neto) / **NPV**.

### Decisión
Todas las proyecciones financieras a **5 años** utilizarán las siguientes fórmulas oficiales:
1. **VAN (Valor Actual Neto)**:
   $$VAN = \sum_{t=1}^{5} \frac{CF_t}{(1 + r)^t} - CAPEX_0$$
   Donde la tasa de descuento ($r$) predeterminada se establece en **7.5%** (alineada a la inflación proyectada y costo de capital dinámico ajustable entre 5% y 12% mediante sliders).
2. **TIR / IRR (Tasa Interna de Retorno)**:
   Tasa $r$ donde $VAN = 0$.
3. **ROI (Retorno de Inversión)**:
   $$ROI = \frac{\text{Ganancia Neta Acumulada a 5 Años}}{\text{CAPEX Inicial Total}} \times 100\%$$
4. **Payback Period**:
   Tiempo exacto (en meses/años) necesario para recuperar la inversión inicial de CAPEX.
5. **Costo por Casa Pasada (Cost per Home Passed)**:
   $$CPHP = \frac{CAPEX_{\text{Acceso Última Milla}}}{\text{Total Casas Pasadas}} \le \$500 \text{ MXN}$$

---

## ADR 004: Cobertura Geográfica Estratégica en México (5 Ciudades Clave)

### Contexto
Se requiere enfocar la expansión inicial del MVP en mercados representativos de México que cubran Tier 1, Tier 2 y alta demanda industrial/turística.

### Decisión
Las 5 ciudades seleccionadas para el MVP son:
1. **CDMX**: Mercado Tier 1 de ultra alta densidad, alta competencia, costos de despliegue elevados.
2. **Monterrey**: Mercado Tier 1 industrial/corporativo, demanda en conectividad empresarial de alta disponibilidad.
3. **Guadalajara**: Mercado Tier 1 tecnológico, crecimiento acelerado en polos de desarrollo.
4. **Tijuana**: Mercado Tier 2 de frontera norte, demanda fronteriza y alta rentabilidad.
5. **Mérida**: Mercado Tier 2 de alto crecimiento regional y menor competencia actual.

---

## ADR 005: Gobernanza y Sistema de Evaluación mediante Subagentes Nativos

### Contexto
Garantizar que ningún desarrollo avance sin pasar por auditorías automatizadas de código, rendimiento, experiencia de usuario y cumplimiento de negocio.

### Decisión
Se integran 4 subagentes nativos de Antigravity en cada puerta de Sprint:
- **`po_agent`**: Valida alineación estratégica con las 10 preguntas ejecutivas y emite únicamente `RECOMMEND APPROVAL` o `REWORK REQUIRED`.
- **`qa_agent`**: Ejecuta `pytest` y evalúa `session_state`.
- **`performance_agent`**: Audita `st.cache_data`, `st.cache_resource` y tiempos de respuesta.
- **`ux_ui_agent`**: Audita la presencia de `Logo.gif` y el cumplimiento de la guía de branding de SOMOS Internet.
