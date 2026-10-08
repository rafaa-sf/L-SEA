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
| **Where are the top landing sites?** | **L-SEA Autopilot:** 3×3 spatial anti-glitch filter + 8% pe