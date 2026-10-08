# 🌔 L-SEA · Lunar Site Evaluation Algorithm

**🇬🇧 [English](#-english) · 🇪🇸 [Español](#-español)**

> **NASA Space Apps Challenge 2026 (Málaga)** · Challenge / Reto: *CLPS Lunar Mission Browser*
>
> **Version / Versión:** EVO 3.2 (L-SEA Autonomous Suite) · **License / Licencia:** [MIT](LICENSE)
>
> 🚀 **Demo:** https://lunar-horizon-clps-browser.streamlit.app/

---

# 🇬🇧 English

## The problem

Choosing where and when to land near the lunar south pole is one of the most perilous challenges in modern spaceflight. The Sun skims the horizon at grazing angles (~1.5°), mountain massifs cast multi-kilometre shadows, and the Earth (essential for Direct-to-Earth telemetry) oscillates in and out of sight due to lunar libration. 

Most existing lunar browsers are **passive visualizers**: they present raw maps and leave human planners to spend dozens of hours sifting through dense ephemeris graphs. When an Artemis Human Landing System (HLS) or a commercial CLPS lander is descending, mission controllers need **actionable decisions, not passive charts**.

## Our solution: L-SEA

**L-SEA (Lunar Site Evaluation Algorithm)** is an autonomous mission planning and tactical landing evaluation engine. It takes NASA LRO/LOLA elevation data, combines it with high-precision JPL DE421 ephemeris and IAU lunar orientation models, and autonomously resolves:
1. **WHERE to land:** Spatial multi-criteria optimization that isolates safe plateaus and eliminates cliff-edge hazards.
2. **WHEN to land:** A 365-day annual sliding-window flight manifest generator that determines optimal launch and landing windows.
3. **HOW to survive:** Multi-day electrical power subsystem (EPS) modeling, battery-bridging analysis, and Deep Space Network (DSN) ground station tracking.

---

### What you can do

| Operational Question | L-SEA Answer Engine |
|---|---|
| **Where is it safe to touch down?** | High-precision slope tensor with Artemis safety thresholds: Optimal (<5°), Caution (≤10°), Critical Hazard (>10°). |
| **Where are the top landing sites?** | **L-SEA Autopilot:** 3×3 spatial anti-glitch filter + 8% perimeter deadzone + non-maximum suppression to extract the Top 5 safest plateaus. |
| **Is there sunlight and power?** | Raytraced 360° terrain horizon occlusion + **Electrical Power Subsystem (EPS)** model (GaAs 29% space cells, 1361 W/m² solar flux, hotel load & net wattage). |
| **Can we talk to Earth?** | True line-of-sight line + real-time **NASA Deep Space Network (DSN)** tracking (Madrid CDSCC, Goldstone GDSCC, Canberra CDSCC with >10° elevation masks). |
| **When can we launch during the year?** | **365-Day Landing Window Finder:** Evaluates mission profiles (Artemis III 7d, CLPS 14d, Rover 28d) against 365 days, generates a Feasibility Calendar, and exports a CSV flight manifest. |
| **Can we automate the entire decision?** | **⚡ Auto-Optimize Mission Button:** Automatically locks the Top #1 landing site, scans the 365-day window, sets optimal T0, and configures the 3D cockpit in 0.2 seconds. |
| **Which lunar region is superior?** | **Site Benchmark Matrix:** Direct side-by-side evaluation (e.g. Shackleton Connecting Ridge vs. Malapert Massif) comparing slopes, solar yield, DTE windows, and overall L-SEA score. |

---

### Key Innovations in EVO 3.2

* **365-Day Window Finder & Feasibility Calendar:** Sliding window algorithm evaluating 365 consecutive days. Generates an annual GO/NO-GO ribbon, extracts consolidated flight windows, and allows **1-click loading of any window directly into the 3D simulation**.
* **Deep Space Network (DSN) Topocentric Tracking:** Computes real elevation angles of the Moon over Madrid (+21.4°), Goldstone (+32.1°), and Canberra (-44.2°) to detect ground station handovers and communication gaps.
* **Electrical Power Subsystem (EPS) Modeling:** Calculates gross solar harvesting, lander baseline hotel loads (-100 W), and net power balance in real time.
* **Cinematic 3D PBR Shader Engine:** Directional 3D solar lighting linked vectorially to real solar azimuth/elevation, raytraced cast shadows, orbital approach corridors, and dual shader modes: **Instantaneous Sun** vs. **Cumulative Sunlight (Peaks of Eternal Light)**.
* **Clickable Interactive Timeline:** Touch-control surface where clicking any column immediately jumps the entire 3D simulation, HUD, and power models to that exact mission day.
* **Bilingual Executive Interface:** Real-time 1-click toggle between 🇪🇸 Spanish and 🇬🇧 English across the entire UI.

---

## How it works

NASA LRO / LOLA DEM (.npy + .json) -> Mechanical Topography + 360° Raytracing + JPL DE421 Ephemeris + NASA DSN Tracking -> Multi-Day Suitability Matrix + Autopilot Ranker -> Tactical Glass Cockpit HUD + Plotly PBR Interactive 3D.

---

## Install and run

Requires Python 3.10+ (tested on Python 3.12 and 3.14).

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Opens at `http://localhost:8501`. The repository includes `datos/de421.bsp` (17 MB), enabling **100% offline flight dynamics and ephemeris calculation**.

---

## Project structure

```
app.py                 Tactical cockpit UI (Streamlit): HUD, 3D engine, charts, Window Finder
lunar.py               Physics engine: slope tensor, raytracing, DSN, EPS, Autopilot, JPL DE421
preparar_lola.py       Crops raw NASA LOLA GeoTIFFs into scaled .npy arrays with heading calculation
generar_dem.py         Procedural synthetic DEM generator with true metric scale
requirements.txt       Production dependencies (Streamlit, NumPy, Plotly, Skyfield, Pandas)
requirements-mapas.txt Pipeline dependencies for raster processing (Rasterio)
mapas/                 <site>.npy (elevation matrix in metres) + <site>.json (metadata)
datos/de421.bsp        JPL DE421 planetary ephemeris kernel
```

---

## Candidate Sites (NASA Artemis III & CLPS)

| Site | Source | Resolution | Status |
|---|---|---|---|
| Cráter Shackleton (Connecting Ridge) | Real LOLA (`LDEM_80S_40MPP_ADJ`) | 750×750 @ ~40 m/px (30 km) | ✅ Flight Grade |
| Macizo Malapert (Artemis Ridge) | Real LOLA (`LDEM_80S_40MPP_ADJ`) | 750×750 @ ~40 m/px (30 km) | ✅ Flight Grade |

---

## Known limitations

- **12:00 UTC Daily Ephemeris Epoch:** Evaluates geometry daily at 12:00 UTC; sub-hourly DSN pass handovers are planned for future desktop builds.
- **Direct-to-Earth Line of Sight:** Relays in NRHO (Gateway) or Lunar Pathfinder are modeled via ground-segment line-of-sight margins.
- **Topographic Edge Limit:** Raytracing assumes terrain outside the 30 km local DEM is coplanar with the map boundary.

---

## Credits and data

* **Topography:** NASA Lunar Reconnaissance Orbiter (LRO) / LOLA Science Team, PGDA.
* **Ephemeris:** NASA JPL DE421 via Skyfield.
* **Lunar Orientation & Libration:** International Astronomical Union (IAU) Working Group on Cartographic Coordinates and Rotational Elements.
* **Ground Segment:** NASA Deep Space Network (DSN) operational coordinates.

---

## Team

**Team L-SEA**

| Name | Role |
|---|---|
| Rafael Enrique Guil Aranda | Lead Systems Developer & Astrodynamics Engineer |
| Marcos Medina Gómez | Product Manager, Data Specialist & Mission Architecture |

Licensed under the MIT License.

---

# 🇪🇸 Español

## El problema

Elegir dónde y cuándo aterrizar cerca del polo sur lunar es uno de los desafíos más complejos de la exploración espacial moderna. El Sol roza el horizonte en ángulos extremadamente rasantes (~1.5°), los macizos montañosos proyectan sombras kilométricas y la Tierra (indispensable para la comunicación directa Direct-to-Earth) entra y sale del campo de visión debido a la libración lunar.

La mayoría de herramientas existentes son **visores pasivos**: muestran mapas estáticos y obligan a los planificadores a pasar horas interpretando complejas gráficas de efemérides. Cuando un módulo Artemis HLS o un módulo comercial CLPS está en fase de descenso, los controladores necesitan **decisiones autónomas, no gráficas pasivas**.

## Nuestra solución: L-SEA

**L-SEA (Lunar Site Evaluation Algorithm)** es un motor autónomo de evaluación táctica y planificación de misiones lunares. Integra modelos digitales de elevación de NASA LRO/LOLA con efemérides de alta precisión JPL DE421 y el modelo de rotación lunar de la IAU, resolviendo de forma autónoma:
1. **DÓNDE aterrizar:** Optimización espacial multicriterio que detecta mesetas seguras y elimina zonas de precipicio.
2. **CUÁNDO aterrizar:** Algoritmo deslizante sobre 365 días que extrae las ventanas de lanzamiento y descenso más viables del año.
3. **CÓMO sobrevivir:** Modelo del subsistema de energía eléctrica (EPS), consumo de batería y seguimiento de las estaciones de la Deep Space Network (DSN).

---

### Qué puedes hacer

| Pregunta de Misión | Motor de Respuesta L-SEA |
|---|---|
| **¿Es seguro tocar suelo?** | Tensor de pendientes con umbrales Artemis: Óptimo (<5°), Precaución (≤10°), Peligro Crítico (>10°). |
| **¿Cuáles son los mejores sitios?** | **Autopilot L-SEA:** Convolución espacial 3×3 anti-glitch + zona muerta perimetral del 8% + supresión de no máximos para extraer el Top 5 de mesetas seguras. |
| **¿Hay luz y energía fotovoltaica?** | Trazado de rayos topográficos en 360° + **Modelo Eléctrico EPS** (células espaciales GaAs 29%, 1361 W/m², consumo base hotelero y potencia neta). |
| **¿Podemos comunicarnos con la Tierra?** | Visibilidad geométrica directa + seguimiento en tiempo real de la **Deep Space Network (DSN)** de NASA (Madrid CDSCC, Goldstone GDSCC, Canberra CDSCC con máscara >10°). |
| **¿Cuándo podemos volar durante el año?** | **Buscador de Ventanas (365 días):** Evalúa perfiles (Artemis III 7d, CLPS 14d, Rover 28d) a lo largo de 365 días, genera un Calendario de Viabilidad y exporta el manifiesto en CSV. |
| **¿Se puede automatizar toda la decisión?** | **⚡ Botón Auto-Optimizar Misión:** Fija el sitio seguro #1, escanea las ventanas del año, establece la fecha T0 óptima y orienta el 3D en 0.2 segundos. |
| **¿Qué región polar es superior?** | **Matriz Benchmark Comparativa:** Comparación directa cara a cara (Shackleton Connecting Ridge vs. Macizo Malapert) analizando pendientes, insolación, ventanas DTE y Score global. |

---

### Novedades Principales en EVO 3.2

* **Buscador de Ventanas (Window Finder) y Calendario de Viabilidad:** Algoritmo de ventana deslizante sobre 365 días que genera una cinta temporal GO/NO-GO anual y permite **cargar cualquier ventana directamente en la simulación 3D en 1 clic**.
* **Tracking Topocéntrico DSN (NASA JPL):** Calcula los ángulos de elevación reales de la Luna sobre Madrid (+21.4°), Goldstone (+32.1°) y Canberra (-44.2°) para detectar relevos y gaps de comunicación.
* **Modelo Eléctrico EPS:** Modela la generación solar bruta, el consumo hotelero del módulo (-100 W) y el balance de potencia neta en tiempo real.
* **Motor 3D Cinemático PBR:** Iluminación física vectorial vinculada al Sol, sombras raytraced proyectadas, corredores de aproximación orbital y selector dual: **Luz Instantánea** vs. **Luz Acumulada (Picos de Luz Eterna)**.
* **Línea de Tiempo Táctil Clicable:** Superficie de control donde hacer clic en cualquier día de la gráfica actualiza de inmediato el 3D, el HUD y la telemetría a ese momento exacto.
* **Interfaz Bilingüe en Vivo:** Conmutador instantáneo entre 🇪🇸 Español e 🇬🇧 English en toda la aplicación.

---

## Cómo funciona

DEM NASA LRO / LOLA (.npy + .json) -> Topografía Mecánica + Raytracing 360° + Efemérides JPL DE421 + Tracking DSN -> Matriz de Idoneidad + Autopilot de Descenso -> Cabina Táctica HUD + Plotly PBR 3D Interactivo.

---

## Instalación y uso

Requiere Python 3.10 o superior (probado en Python 3.12 y 3.14).

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Se abre en `http://localhost:8501`. El repositorio incluye el archivo `datos/de421.bsp` (17 MB), permitiendo una ejecución **100% offline sin necesidad de conexión a internet**.

---

## Estructura del proyecto

```
app.py                 Interfaz tipo Glass Cockpit (Streamlit): HUD, motor 3D, Window Finder, Benchmark
lunar.py               Física y astrodinámica: pendientes, raytracing, DSN, EPS, Autopilot, JPL DE421
preparar_lola.py       Recorta GeoTIFFs originales de LOLA y calcula el rumbo al norte selenográfico
generar_dem.py         Generador procedural de modelos sintéticos a escala métrica real
requirements.txt       Dependencias de ejecución (Streamlit, NumPy, Plotly, Skyfield, Pandas)
requirements-mapas.txt Herramientas para procesar mapas raster (Rasterio)
mapas/                 <sitio>.npy (alturas en metros) + <sitio>.json (metadatos de escala)
datos/de421.bsp        Kernel de efemérides planetarias JPL DE421
```

---

## Sitios Candidatos Incluidos

| Sitio | Fuente | Resolución | Estado |
|---|---|---|---|
| Cráter Shackleton (Connecting Ridge) | LOLA real (`LDEM_80S_40MPP_ADJ`) | 750×750 @ ~40 m/px (30 km) | ✅ Grado Misión |
| Macizo Malapert (Cresta Artemis) | LOLA real (`LDEM_80S_40MPP_ADJ`) | 750×750 @ ~40 m/px (30 km) | ✅ Grado Misión |

---

## Limitaciones conocidas

- **Paso de efemérides diario (12:00 UTC):** Evalúa la mecánica orbital día a día; el seguimiento sub-horario de pases DSN está planificado para la versión de escritorio.
- **Línea de visión directa a Tierra:** La simulación asume enlace directo DTE; satélites repetidores en NRHO (Gateway) o Lunar Pathfinder se modelan mediante márgenes de enlace visual.
- **Efecto de borde topográfico:** El trazado de rayos asume que el terreno fuera de los 30 km del DEM local continúa en la cota del perímetro.

---

## Créditos y datos

* **Topografía:** NASA Lunar Reconnaissance Orbiter (LRO) / Equipo científico de LOLA, PGDA.
* **Efemérides Planetarias:** NASA JPL DE421 mediante Skyfield.
* **Orientación y Libración Lunar:** Working Group on Cartographic Coordinates and Rotational Elements de la IAU.
* **Segmento Terrestre:** Coordenadas oficiales de las antenas de la Deep Space Network (DSN) de la NASA.

---

## Equipo

**Equipo L-SEA**

| Nombre | Función |
|---|---|
| Rafael Enrique Guil Aranda | Desarrollador Principal de Sistemas e Ingeniero de Astrodinámica |
| Marcos Medina Gómez | Product Manager, Especialista de Datos y Arquitectura de Misión |

Publicado bajo Licencia MIT. Libre para uso y estudio.