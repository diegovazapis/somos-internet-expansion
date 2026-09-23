# Guía de Demostración Ejecutiva — SOMOS Internet

**Proyecto**: Expansión Nacional de Red de Fibra Óptica (México)  
**Empresa**: SOMOS Internet  
**Arquitectura**: SOMOS Internet Mexico Expansion Network Architecture (featuring SOMOS Colombia-Style Decentralized MicroPOP Model)  
**Rol del Entrevistado**: Arquitecto de Expansión Nacional de Fibra Óptica  
**Entregable**: `executive_demo_guide.md` (Sprint 6)  

---

## 🎭 Estructura de la Demostración para la Entrevista (Paso a Paso)

### Paso 1: Introducción Ejecutiva & Branding SOMOS Internet (1 - 2 min)
1. Abrir la aplicación web ejecutiva ejecutando `streamlit run app.py`.
2. Destacar en la barra lateral el branding corporativo con el archivo [`Logo.gif`](file:///c:/Users/diego/OneDrive/Documentos/Somos_Internet/Logo.gif) y el distintivo del rol: **Arquitecto de Expansión Nacional de Fibra Óptica**.
3. Explicar al entrevistador que la solución combina ingeniería de telecomunicaciones de 3 capas con modelos financieros formales (**VAN**, **TIR**, **ROI** y **Payback**) en las 5 ciudades estratégicas de México (**CDMX, Monterrey, Guadalajara, Tijuana y Mérida**).

---

### Paso 2: Recorrido por Módulos y Preguntas Clave del Examen

#### 📍 Módulo 01: Arquitectura & Topología Nacional (Pregunta 1)
- Seleccionar **🇲🇽 Red Nacional México** en el desplegable.
- Mostrar el mapa 3D en PyDeck con las primitivas `ColumnLayer` (Nodos POP y Hubs) y `PathLayer` (Malla Backbone DWDM 400G en Amarillo Neón).
- Explicar la disponibilidad del **99.999%** y el uso de la postería CFE bajo la norma **CFE-PROT-2024**.

#### 🎯 Módulo 02: Estrategia de Expansión & Trade-offs (Pregunta 10)
- Presentar la comparativa entre la **Opción A (Tier 1)**, **Opción B (Tier 2)** y **Opción C (Optimización de Red Existente)**.
- Mover los sliders de ponderación (Demanda, CPHP y CFE) y la tasa WACC de descuento del **VAN** ($5.0\% - 12.0\%$) para demostrar cómo el modelo recalcula los valores instantáneamente.

#### 🏗️ Módulo 03: Modelo Operativo & Permisos CFE (Pregunta 3)
- Mostrar las **5 Fases del Despliegue** (Planeación, Permisos CFE, Construcción, Empalme OTDR y Operación).
- Detallar la división entre decisiones centralizadas (Headquarters) y ejecución regional en campo.

#### 📈 Módulo 04: Capacidad & Protocolo de Crisis (Preguntas 5 y 6)
- Cambiar a la pestaña **🚨 Simulador de Crisis Backbone (2 Horas)**.
- Explicar la respuesta inmediata ante un corte de fibra en el tramo CDMX-GDL:
  - *0-15 min*: Alarma DWDM/OTDR y conmutación automática a ruta 1+1 disjunta en **$< 50\text{ ms}$**.
  - *15-45 min*: Despacho de cuadrilla de empalme e integración al War Room.
  - *45-90 min*: Reparación física en campo y fusión de hilos prioritarios.
  - *90-120 min*: Prueba OTDR confirmada y reporte formal al IFT y clientes Enterprise.

#### 🛡️ Módulo 05: Gobernanza & Matriz de Riesgos (Preguntas 4, 7, 8 y 9)
- Demostrar el **Evaluador de Gate CAPEX**: Ingresar $\$18,000,000\text{ MXN}$ para mostrar cómo escala automáticamente a aprobación del **Comité Ejecutivo de Junta Directiva (STRATEGIC)**.

#### 💼 Módulo 07: Simulador CEO & Boardroom Mode (Simulador Interactivo)
- Mover los sliders en vivo durante las preguntas difíciles del entrevistador:
  - *¿Qué pasa si la inflación sube y la tasa de descuento cambia al 10%?* $\rightarrow$ Ajustar slider WACC.
  - *¿Qué pasa si el CAPEX de fibra se incrementa 20%?* $\rightarrow$ Ajustar slider de CAPEX a 120%.
- Mostrar que la regla inviolable de eficiencia de última milla se mantiene: **Costo por Casa Pasada ($CPHP < \$500\text{ MXN}$)** en todos los escenarios.
