# 🌔 CLPS Lunar Mission Browser · Artemis IV Autopilot

**🇬🇧 [English](#-english) · 🇪🇸 [Español](#-español)**

> **NASA Space Apps Challenge 2026 (Málaga)** · Challenge / Reto: *CLPS Lunar Mission Browser*
>
> **Version / Versión:** EVO 2.6 · **License / Licencia:** [MIT](LICENSE)
>
> 🚀 **Demo:** https://lunar-horizon-clps-browser.streamlit.app/

---

# 🇬🇧 English

## The problem

Choosing where and when to land near the lunar south pole is hard. The Sun skims the horizon at about 1°, mountains cast kilometre-long shadows, and the Earth (needed for Direct-to-Earth communication) bobs in and out of view because of libration. A site that looks perfect on one day can be dark or out of contact on the next.

## Our solution

A web tool that lets mission planners **compare landing sites and dates** and see, for any point on a real lunar elevation map, whether it is **safe, sunlit and in line of sight with Earth**, and then **finds the best sites automatically**.

### What you can do

| Question | How the app answers it |
|---|---|
| Is it safe to land? | Real terrain slope in degrees with a traffic light: optimal < 5°, caution ≤ 10°, danger > 10° |
| Is there sunlight? | The Sun is checked against the **terrain horizon** at its azimuth, not a flat horizon |
| Is there a line of sight to Earth? | Same method for the Earth (Direct-to-Earth window) |
| How does the month evolve? | 30-day timeline with lunar phases 🌑🌓🌕 and % of days with Sun, with Earth link, and with both |
| **Where should we land?** | **Autopilot:** ranks the Top 5 safest, best-lit sites on the map and jumps to any of them in one click |

### New in EVO 2.6: Autopilot & Tactical Site Ranker

- **Suitability index (0–100 %)** that combines **60 % topographic safety** (quadratic penalty as slope approaches the limit) and **40 % solar exposure**.
- **Top 5 site finder** with three safeguards:
  1. **Perimeter dead-zone (8 %)** to discard artefacts at the map edge.
  2. **Anti-glitch 3×3 filter:** a flat pixel next to a cliff is penalised because its neighbours drag its score down.
  3. **Non-maximum suppression:** the five sites are physically separated, so you never get the same hill five times.
- **Mission cockpit interface:** 3D relief, illumination map, slope map, suitability map, full 360° radial horizon profile (lander mast 2 m) and per-point telemetry.

### Visualisations

3D relief with **hillshade and cast shadows** for the chosen day · illumination map · slope map · suitability map with Top-5 markers · horizon profile with Sun and Earth overlaid · 30-day timeline.

## How it works

- **Terrain:** elevation models (DEM) from **NASA LRO/LOLA**, stored as `.npy` arrays in metres plus a `.json` with the real scale (metres per cell).
- **Slope:** `arctan(dz/dx)` using the real map scale.
- **Horizon:** from the lander, a ray is traced along each of the 360° of azimuth, keeping the highest angle at which terrain blocks the sky.
- **Sun, Earth and phases:** computed with **Skyfield** and the **JPL DE421** ephemerides (valid 1900–2050), combined with the **IAU** lunar rotation and libration model. Sanity-checked against known ranges: Earth libration ≈ ±6.8° (latitude) and ±7.9° (longitude), sub-solar inclination ≈ ±1.5°.
- **Illumination:** hillshade with an exposure curve (the Sun is ~1° above the horizon) plus cast shadows by ray tracing toward the Sun.
- **Performance:** calculations use the full-resolution map; only drawing is reduced to ≤ 250×250 cells. Tested with 1,500×1,500 maps.
- **Architecture:** the physics (`lunar.py`) is fully separated from the interface (`app.py`), so it can later power a desktop tool with higher-resolution maps and GPU-accelerated 3D.

## Install and run

Requires Python 3.10+ (developed on 3.14, also tested on 3.12).

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Opens at `http://localhost:8501`. The file `datos/de421.bsp` (17 MB) is included, so **no internet is needed** for the ephemerides.

> On Windows, if `streamlit` is not recognised, always use `python -m streamlit ...`.

## Project structure

```
app.py                 Interface (Streamlit): controls, charts and texts
lunar.py               All the physics: slope, horizon, shadows, Sun/Earth/phases, suitability, Top-N sites
preparar_lola.py       Crops a real LOLA map and prepares it for the app
generar_dem.py         Generates synthetic maps with real scale (for testing)
requirements.txt       App dependencies (also used by the cloud)
requirements-mapas.txt Extra dependencies, only to prepare maps (rasterio)
mapas/                 <site>.npy (heights in m) + <site>.json (metadata)
datos/de421.bsp        JPL DE421 ephemerides
```

## Adding or updating a real LOLA map

1. Download the south-pole elevation model from NASA's [PGDA](https://pgda.gsfc.nasa.gov/products/90): files `LDEM_80S_<res>MPP_ADJ` (heights in metres): 80 m/px (181 MB), 40 m/px (685 MB), 20 m/px (2.6 GB). **Do not push them to GitHub** (over 100 MB; `.gitignore` already excludes them).
2. Install the map tools: `python -m pip install -r requirements-mapas.txt`
3. Crop a site (example: Shackleton, 30 km wide):

```bash
python preparar_lola.py LDEM_80S_40MPP_ADJ.tiff --nombre shackleton --lat -89.9 --lon 129.8 --km 30
```

The script writes `mapas/shackleton.npy` and `.json` and computes the map's **heading** (rotation relative to local north) automatically. The app detects any new map in `mapas/` without code changes.

### Map status

| Site | Source | Resolution | Status |
|---|---|---|---|
| Shackleton crater | Real LOLA (`LDEM_80S_40MPP_ADJ`) | 750×750 at ~40 m/cell (30 km) | ✅ Real data |
| Malapert massif | Real LOLA (`LDEM_80S_40MPP_ADJ`) | 750×750 at ~40 m/cell (30 km) | ✅ Real data |

## Known limitations

We state them openly because they are part of the project's rigour:

- **One evaluation per day (12:00 UTC).** Real visibility changes during the day; hourly windows are on the roadmap.
- **Sun visible = its upper limb peeks out** (solar radius 0.267°); **Earth visible = its centre peeks out.** A modelling decision.
- **The horizon assumes flat ground = 0°** and ignores lunar curvature. Terrain outside the map is not considered, so results near the edge are optimistic.
- **The Autopilot ranks using the illumination of the selected day**, not the whole month (a month-long illumination map is on the roadmap).
- **Slope thresholds (5° and 10°) are configurable, not official** for any specific mission.
- **No indirect illumination** (terrain bounce, earthshine) and no penumbra: the Sun is a point.
- **Fixed lander height** (2 m).
- **IAU rotation model**, not NASA's principal-axes frame: the error is small compared with the ~1.5° Sun variation, but it is not a flight-grade calculation.
- **Malapert's centre (lat −86.0°, lon 0.1°) was set by hand**; its position should be checked against the real map.

## Roadmap

- **Hourly** visibility windows instead of daily.
- **Month-long illumination map** and a multi-day Autopilot.
- **Side-by-side site comparison.**
- **Two-level maps:** regional (30 km) and local zoom (2–5 km at 5–10 m/px).
- Sun and Earth tracks on the horizon profile, and link with **DSN** stations.
- More candidate sites on real LOLA data.
- **Long-term vision:** web today so anyone can use it with zero install; tomorrow a desktop tool with higher-resolution maps.

## Credits and data

- Topography: **NASA LRO / LOLA** (Lunar Orbiter Laser Altimeter), [PGDA](https://pgda.gsfc.nasa.gov/).
- Ephemerides: **JPL DE421** via [Skyfield](https://rhodesmill.org/skyfield/).
- Lunar orientation: **IAU** rotation model (Archinal et al.).
- Interface and charts: [Streamlit](https://streamlit.io/) and [Plotly](https://plotly.com/python/).
- Fonts: Orbitron, JetBrains Mono, Inter (Google Fonts).

## Team

**Team Lunar Horizon**

| Name | Role |
|---|---|
| Rafael Enrique Guil Aranda | Lead Developer |
| Marcos Medina Gómez | Product Manager & Data Specialist |

## License

Released under the [MIT License](LICENSE). Free to use, study and build upon.

---

# 🇪🇸 Español

## El problema

Elegir dónde y cuándo aterrizar cerca del polo sur lunar es difícil. El Sol roza el horizonte a ~1°, las montañas proyectan sombras de kilómetros y la Tierra (necesaria para la comunicación directa, Direct-to-Earth) entra y sale de la vista por la libración. Un sitio perfecto un día puede estar a oscuras o sin enlace al siguiente.

## Nuestra solución

Una herramienta web que permite **comparar sitios de aterrizaje y fechas** y comprobar, en cualquier punto de un mapa lunar real, si es **seguro, tiene Sol y tiene línea de visión con la Tierra**, y que además **encuentra automáticamente los mejores sitios**.

### Qué puedes hacer

| Pregunta | Cómo se responde |
|---|---|
| ¿Es seguro aterrizar? | Pendiente real del terreno (grados) con semáforo: óptimo < 5°, precaución ≤ 10°, peligro > 10° |
| ¿Hay Sol? | El Sol se comprueba contra el **horizonte del terreno** en su azimut, no un horizonte plano |
| ¿Hay línea de visión con la Tierra? | Igual, para la Tierra (ventana Direct-to-Earth) |
| ¿Cómo evoluciona el mes? | Línea de tiempo de 30 días con fases lunares 🌑🌓🌕 y % de días con Sol, con enlace y con ambos |
| **¿Dónde aterrizamos?** | **Autopilot:** clasifica los 5 mejores sitios (seguros y con más luz) del mapa y salta a cualquiera con un clic |

### Novedad de EVO 2.6: Autopilot y Tactical Site Ranker

- **Índice de idoneidad (0–100 %)** que combina **60 % seguridad topográfica** (penalización cuadrática al acercarse al límite de pendiente) y **40 % exposición solar**.
- **Buscador del Top 5** con tres salvaguardas:
  1. **Zona muerta perimetral (8 %)** para descartar artefactos del borde del mapa.
  2. **Filtro anti-glitch 3×3:** un píxel plano junto a un precipicio se penaliza porque sus vecinos bajan su nota.
  3. **Supresión de no máximos:** los cinco sitios quedan físicamente separados, así que no sale la misma colina cinco veces.
- **Interfaz tipo cabina de misión:** relieve 3D, mapa de iluminación, mapa de pendientes, mapa de idoneidad, perfil de horizonte radial de 360° (mástil del módulo 2 m) y telemetría del punto.

### Visualizaciones

Relieve 3D con **sombreado y sombras proyectadas** del día elegido · mapa de iluminación · mapa de pendientes · mapa de idoneidad con marcadores del Top 5 · perfil del horizonte con Sol y Tierra superpuestos · línea temporal de 30 días.

## Cómo funciona

- **Terreno:** modelos de elevación (DEM) de **NASA LRO/LOLA**, guardados como matrices `.npy` en metros, con su escala real (metros por celda) en un `.json`.
- **Pendiente:** `arctan(dz/dx)` usando la escala real del mapa.
- **Horizonte:** desde el módulo se traza un rayo en cada uno de los 360° de azimut y se guarda el ángulo máximo con el que el relieve tapa el cielo.
- **Sol, Tierra y fases:** calculados con **Skyfield** y las efemérides **JPL DE421** (válidas 1900–2050), combinadas con el modelo de rotación y libración de la Luna de la **IAU**. Comprobado contra rangos conocidos: libración de la Tierra ≈ ±6,8° (latitud) y ±7,9° (longitud), inclinación subsolar ≈ ±1,5°.
- **Iluminación:** hillshade con curva de exposición (el Sol está a ~1° del horizonte) más sombras proyectadas por trazado de rayos hacia el Sol.
- **Rendimiento:** los cálculos usan el mapa completo; solo el dibujado se reduce a ≤ 250×250 celdas. Probado con mapas de 1.500×1.500.
- **Arquitectura:** la física (`lunar.py`) está separada de la interfaz (`app.py`), para poder llevarla después a una herramienta de escritorio con mapas de mayor resolución y 3D acelerado por GPU.

## Instalación y uso

Requiere Python 3.10 o superior (desarrollado en 3.14, probado también en 3.12).

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Se abre en `http://localhost:8501`. El archivo `datos/de421.bsp` (17 MB) va incluido, así que **no hace falta internet** para las efemérides.

> En Windows, si `streamlit` no se reconoce como comando, usa siempre `python -m streamlit ...`.

## Estructura del proyecto

```
app.py                 Interfaz (Streamlit): controles, gráficos y textos
lunar.py               Toda la física: pendiente, horizonte, sombras, Sol/Tierra/fases, idoneidad, Top-N sitios
preparar_lola.py       Recorta un mapa real de LOLA y lo deja listo para la app
generar_dem.py         Genera mapas sintéticos con escala real (para pruebas)
requirements.txt       Dependencias de la app (también las usa la nube)
requirements-mapas.txt Dependencias extra, solo para preparar mapas (rasterio)
mapas/                 <sitio>.npy (alturas en m) + <sitio>.json (metadatos)
datos/de421.bsp        Efemérides JPL DE421
```

## Añadir o actualizar un mapa con datos reales de LOLA

1. Descarga el modelo de elevación del polo sur desde el [PGDA de la NASA](https://pgda.gsfc.nasa.gov/products/90): archivos `LDEM_80S_<res>MPP_ADJ` (alturas en metros): 80 m/px (181 MB), 40 m/px (685 MB), 20 m/px (2,6 GB). **No los subas a GitHub** (superan los 100 MB; el `.gitignore` ya los excluye).
2. Instala lo necesario para preparar mapas: `python -m pip install -r requirements-mapas.txt`
3. Recorta el sitio (ejemplo para Shackleton, 30 km de lado):

```bash
python preparar_lola.py LDEM_80S_40MPP_ADJ.tiff --nombre shackleton --lat -89.9 --lon 129.8 --km 30
```

El script guarda `mapas/shackleton.npy` y `.json` y calcula solo el **rumbo** (el giro del mapa respecto al norte local). La app detecta cualquier mapa nuevo de `mapas/` sin tocar código.

### Estado de los mapas

| Sitio | Fuente | Resolución | Estado |
|---|---|---|---|
| Cráter Shackleton | LOLA real (`LDEM_80S_40MPP_ADJ`) | 750×750 a ~40 m/celda (30 km) | ✅ Datos reales |
| Macizo Malapert | LOLA real (`LDEM_80S_40MPP_ADJ`) | 750×750 a ~40 m/celda (30 km) | ✅ Datos reales |

## Limitaciones conocidas

Las dejamos explícitas porque forman parte del rigor del proyecto:

- **Una evaluación por día (12:00 UTC).** La visibilidad real cambia a lo largo del día; las ventanas horarias están en la hoja de ruta.
- **Sol visible = su borde superior asoma** (radio solar 0,267°); **Tierra visible = su centro asoma.** Es una decisión de modelo.
- **El horizonte asume suelo llano = 0°** y no incluye la curvatura lunar. El terreno fuera del mapa no se considera, así que cerca del borde el resultado es optimista.
- **El Autopilot clasifica con la iluminación del día elegido**, no del mes completo (el mapa de iluminación mensual está en la hoja de ruta).
- **Los umbrales de pendiente (5° y 10°) son configurables, no oficiales** de ninguna misión concreta.
- **Sin iluminación indirecta** (reflejo del terreno, luz terrestre) ni penumbra: el Sol se trata como un punto.
- **Altura del módulo fija** (2 m).
- **Rotación lunar con el modelo IAU**, no con el marco de ejes principales de la NASA: el error es pequeño frente a la variación de ~1,5° del Sol, pero no es un cálculo de grado misión.
- **El centro de Malapert (lat −86,0°, lon 0,1°) se puso a mano**; su posición debe verificarse con el mapa real.

## Hoja de ruta

- Ventanas **horarias** de visibilidad en lugar de una evaluación diaria.
- **Mapa de iluminación del mes** y Autopilot multi-día.
- **Comparador de sitios** lado a lado.
- Mapas en **dos niveles**: regional (30 km) y zoom local (2-5 km a 5-10 m/px).
- Trayectoria del Sol y la Tierra en el perfil del horizonte, y enlace con las estaciones de la **DSN**.
- Más sitios candidatos con datos LOLA reales.
- **Visión a largo plazo:** hoy es web para que cualquiera la use sin instalar nada; mañana, una herramienta de escritorio con mapas de mayor resolución.

## Créditos y datos

- Topografía: **NASA LRO / LOLA** (Lunar Orbiter Laser Altimeter), [PGDA](https://pgda.gsfc.nasa.gov/).
- Efemérides: **JPL DE421** vía [Skyfield](https://rhodesmill.org/skyfield/).
- Orientación lunar: modelo de rotación de la **IAU** (Archinal et al.).
- Interfaz y gráficos: [Streamlit](https://streamlit.io/) y [Plotly](https://plotly.com/python/).
- Tipografías: Orbitron, JetBrains Mono, Inter (Google Fonts).

## Equipo

**Equipo Lunar Horizon**

| Nombre | Función |
|---|---|
| Rafael Enrique Guil Aranda | Desarrollador principal (Lead Developer) |
| Marcos Medina Gómez | Product Manager y Especialista de Datos |

## Licencia

Publicado bajo [licencia MIT](LICENSE). Libre para usar, estudiar y ampliar.
