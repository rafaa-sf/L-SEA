# 🌔 L-SEA · Lunar Site Evaluation Algorithm

**🇬🇧 [English](#-english) · 🇪🇸 [Español](#-español)**

> **NASA Space Apps Challenge 2026 (Málaga)** · Challenge / Reto: *CLPS Lunar Mission Browser*
>
> **Version / Versión:** EVO 2.6 (L-SEA) · **License / Licencia:** [MIT](LICENSE)
>
> 🚀 **Demo:** https://lunar-horizon-clps-browser.streamlit.app/

---

# 🇬🇧 English

## The problem

Choosing where and when to land near the lunar south pole is hard. The Sun skims the horizon at about 1°, mountains cast kilometre-long shadows, and the Earth (needed for Direct-to-Earth communication) bobs in and out of view because of libration. A site that looks perfect on one day can be dark or out of contact on the next.

## Our solution

**L-SEA (Lunar Site Evaluation Algorithm)** is a web tool that lets mission planners **compare landing sites and dates** and see, for any point on a real lunar elevation map, whether it is **safe, sunlit and in line of sight with Earth**, and then **finds the best sites automatically**.

### What you can do

| Question | How the app answers it |
|---|---|
| Is it safe to land? | Real terrain slope in degrees with a traffic light: optimal < 5°, caution ≤ 10°, danger > 10° |
| Is there sunlight? | The Sun is checked against the **terrain horizon** at its azimuth, not a flat horizon |
| Is there a line of sight to Earth? | Same method for the Earth (Direct-to-Earth window) |
| How does the month evolve? | 30-day timeline with lunar phases 🌑🌓🌕 and % of days with Sun, with Earth link, and with both |
| **Where should we land?** | **L-SEA Autopilot:** ranks the Top 5 safest, best-lit sites on the map and jumps to any of them in one click |

### New in EVO 2.6: L-SEA Autopilot & Tactical Site Ranker

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