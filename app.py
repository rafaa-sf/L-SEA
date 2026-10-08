# ==============================================================================
# RUTA DEL FICHERO: app.py
# VERSIÓN: L-SEA v3.2 - EXECUTIVE COCKPIT, AUTO-OPTIMIZER & BENCHMARK MATRIX
# ==============================================================================

import json
from datetime import date, datetime, time, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import lunar

st.set_page_config(
    page_title="L-SEA · Lunar Site Evaluation Algorithm", 
    page_icon="🌔",
    layout="wide"
)

# ==============================================================================
# CATÁLOGO OFICIAL DE REGIONES NASA ARTEMIS III
# ==============================================================================
CATALOGO_NASA = {
    "shackleton": {
        "categoria": "Artemis III Candidate",
        "nombre_es": "Connecting Ridge (Borde Shackleton)",
        "nombre_en": "Connecting Ridge (Shackleton Rim)"
    },
    "malapert": {
        "categoria": "Artemis III Candidate",
        "nombre_es": "Macizo Malapert (Cresta Artemis)",
        "nombre_en": "Malapert Massif (Artemis Ridge)"
    }
}

# ==============================================================================
# SISTEMA DE TRADUCCIÓN (I18N)
# ==============================================================================
DICCIONARIO = {
    "ES": {
        "telemetria_sidebar": "🛰️ PARÁMETROS EJECUTIVOS",
        "sitio_label": "Región Candidata (LOLA DEM)",
        "inicio_label": "Fecha T0 (Touchdown Lunar)",
        "perfil_label": "Perfil de Misión Operativa",
        "mastil_label": "Altura Mástil de Antena/Paneles (m)",
        "prioridad_label": "Ponderación: Batería vs. Comunicaciones",
        "prioridad_help": "0% = Prioridad total a captación solar (baterías). 100% = Prioridad total a enlace directo con la Tierra (DTE).",
        "btn_auto_opt": "⚡ AUTO-OPTIMIZAR MISIÓN",
        "autopilot_expander": "🤖 Autopilot & Alternativas Top 5",
        "btn_top1": "🚀 FIJAR MEJOR SITIO (#1 GLOBAL)",
        "select_top": "🎯 Alternativas Top 5 Seguras",
        "btn_nav": "📍 NAVEGAR A COORDENADA",
        "manual_expander": "🛠️ Calibración de Ingeniería / Manual Trim",
        "eje_x": "Eje X (Este →)",
        "eje_y": "Eje Y (Norte ↑)",
        "hud_target": "OBJETIVO TÁCTICO",
        "hud_time": "TIMESTAMP UTC",
        "hud_dte": "ENLACE DIRECTO TIERRA (DTE)",
        "hud_solar": "GENERACIÓN FOTOVOLTAICA",
        "hud_safety": "SEGURIDAD TREN ATERRIZAJE",
        "tag_nominal": "NOMINAL (<5°)",
        "tag_caution": "PRECAUCIÓN (≤10°)",
        "tag_hazard": "PELIGRO CRÍTICO",
        "tab_3d": "🏔️ Topografía 3D (L-SEA Engine)",
        "tab_sol": "🌗 Mapa de Iluminación",
        "tab_pend": "📐 Análisis de Pendientes",
        "tab_score": "🎯 Matriz Idoneidad Multidía",
        "tab_windows": "🚀 Buscador de Ventanas (Window Finder)",
        "tab_benchmark": "⚖️ Benchmark Comparativo (Site Compare)",
        "shader_mode": "Modo de Renderizado 3D:",
        "shader_opt1": "⚡ Luz Solar Cinemática (Raytraced Shadows)",
        "shader_opt2": "☀️ Insolación Acumulada (Picos de Luz Eterna)",
        "z_exag": "Exageración Vertical Z",
        "sec_telemetria": "📡 TELEMETRÍA DETALLADA DEL PUNTO SELECCIONADO",
        "met_elev": "Elevación Local",
        "met_tierra": "Elevación Tierra",
        "met_sol": "Elevación Solar",
        "met_score": "Índice L-SEA Multidía",
        "graf_horiz": "🧭 PERFIL DE HORIZONTE RADIAL 360°",
        "graf_timeline": "📅 VENTANA OPERATIVA Y FASES LUNARES",
        "util_solar": "Ventana Solar Útil",
        "util_dte": "Ventana Enlace DTE",
        "util_ambos": "Simultaneidad Operativa",
        "tier1": "Sitio Prioritario (Tier 1)",
        "tier2": "Sitio Marginal (Tier 2)",
        "tier3": "Sitio Descartado (No-Go)",
    },
    "EN": {
        "telemetria_sidebar": "🛰️ EXECUTIVE PARAMETERS",
        "sitio_label": "Candidate Region (LOLA DEM)",
        "inicio_label": "T0 Date (Lunar Touchdown)",
        "perfil_label": "Operational Mission Profile",
        "mastil_label": "Antenna / Solar Mast (m)",
        "prioridad_label": "Tactical Weight: Power vs. Communications",
        "prioridad_help": "0% = Solar thermal survival. 100% = Uninterrupted Direct-to-Earth link.",
        "btn_auto_opt": "⚡ AUTO-OPTIMIZE MISSION",
        "autopilot_expander": "🤖 Autopilot & Top 5 Alternatives",
        "btn_top1": "🚀 ENGAGE OPTIMAL SITE (#1 GLOBAL)",
        "select_top": "🎯 Top 5 Safe Alternatives",
        "btn_nav": "📍 JUMP TO COORDINATE",
        "manual_expander": "🛠️ Engineering Calibration / Manual Trim",
        "eje_x": "East Axis (X →)",
        "eje_y": "North Axis (Y ↑)",
        "hud_target": "TACTICAL TARGET",
        "hud_time": "UTC TIMESTAMP",
        "hud_dte": "DIRECT-TO-EARTH LINK (DTE)",
        "hud_solar": "SOLAR HARVESTING",
        "hud_safety": "LANDING GEAR SAFETY",
        "tag_nominal": "NOMINAL (<5°)",
        "tag_caution": "CAUTION (≤10°)",
        "tag_hazard": "CRITICAL HAZARD",
        "tab_3d": "🏔️ 3D Terrain (L-SEA Engine)",
        "tab_sol": "🌗 Solar Illumination Map",
        "tab_pend": "📐 Terrain Slope Analysis",
        "tab_score": "🎯 Multi-Day Suitability Matrix",
        "tab_windows": "🚀 Landing Window Finder",
        "tab_benchmark": "⚖️ Site Benchmark Comparison",
        "shader_mode": "3D Shader Engine Mode:",
        "shader_opt1": "⚡ Cinematic Day Light (Raytraced Shadows)",
        "shader_opt2": "☀️ Mission Cumulative Sunlight (Peaks of Eternal Light)",
        "z_exag": "Z-Axis Vertical Exaggeration",
        "sec_telemetria": "📡 DETAILED POINT TELEMETRY",
        "met_elev": "Local Elevation",
        "met_tierra": "Earth Elevation",
        "met_sol": "Solar Elevation",
        "met_score": "Multi-Day L-SEA Index",
        "graf_horiz": "🧭 360° RADIAL TERRAIN HORIZON PROFILE",
        "graf_timeline": "📅 OPERATIONAL TIMELINE & IAU PHASES",
        "util_solar": "Solar Window Yield",
        "util_dte": "DTE Comms Window",
        "util_ambos": "Operational Concurrency",
        "tier1": "Priority Site (Tier 1)",
        "tier2": "Marginal Site (Tier 2)",
        "tier3": "Discarded Site (No-Go)",
    }
}

# ==============================================================================
# ESTILOS: L-SEA GLASS COCKPIT HUD
# ==============================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;800&family=Orbitron:wght@600;900&family=Inter:wght@300;400;600&display=swap');
    
    .stApp {
        background-color: #040711 !important;
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
    }
    h1, h2, h3 {
        font-family: 'Orbitron', sans-serif !important;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }
    code, [data-testid="stMetricValue"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 1.5rem !important;
        font-weight: 800 !important;
        color: #00f0ff !important;
        text-shadow: 0 0 10px rgba(0, 240, 255, 0.3);
    }
    [data-testid="stMetric"] {
        background: rgba(10, 18, 36, 0.75) !important;
        backdrop-filter: blur(8px);
        border: 1px solid rgba(0, 240, 255, 0.2) !important;
        border-left: 4px solid #00f0ff !important;
        padding: 12px 16px;
        border-radius: 4px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.6);
    }
    .tag-go {
        background: rgba(16, 185, 129, 0.2);
        color: #10b981;
        border: 1px solid #10b981;
        padding: 3px 9px;
        border-radius: 3px;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 800;
        font-size: 0.75rem;
    }
    .tag-nogo {
        background: rgba(239, 68, 68, 0.2);
        color: #ef4444;
        border: 1px solid #ef4444;
        padding: 3px 9px;
        border-radius: 3px;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 800;
        font-size: 0.75rem;
    }
    .tag-warn {
        background: rgba(245, 158, 11, 0.2);
        color: #f59e0b;
        border: 1px solid #f59e0b;
        padding: 3px 9px;
        border-radius: 3px;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 800;
        font-size: 0.75rem;
    }
    .dsn-pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 12px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        font-weight: 700;
        margin-right: 8px;
    }
    .dsn-on {
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid #10b981;
    }
    .dsn-off {
        background: rgba(100, 116, 139, 0.15);
        color: #64748b;
        border: 1px solid #475569;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------ IDIOMA
if "idioma" not in st.session_state:
    st.session_state.idioma = "ES"

lang_choice = st.sidebar.radio("🌐 LANGUAGE / IDIOMA", ["🇪🇸 Español", "🇬🇧 English"], horizontal=True)
st.session_state.idioma = "ES" if "Español" in lang_choice else "EN"
TXT = DICCIONARIO[st.session_state.idioma]

# ------------------------------------------------------------------ CONFIG
CARPETA_MAPAS = Path(__file__).parent / "mapas"
LIMITE_OPTIMO = 5
LIMITE_PRECAUCION = 10
MAX_CELDAS_3D = 220

TEMA_TACTICO = dict(
    paper_bgcolor="#040711",
    plot_bgcolor="#080e1d",
    font=dict(family="JetBrains Mono, monospace", color="#94a3b8"),
)

ESCALA_REGOLITO = [
    [0.0, "#03060c"],
    [0.15, "#141d2b"],
    [0.45, "#475569"],
    [0.75, "#94a3b8"],
    [1.0, "#fffbeb"]
]

# ------------------------------------------------------------------- DATOS
@st.cache_data
def cargar_mapa(stem):
    dem = np.load(CARPETA_MAPAS / f"{stem}.npy")
    meta = json.loads((CARPETA_MAPAS / f"{stem}.json").read_text())
    return dem, meta

@st.cache_data
def mapa_pendientes(dem, mpc):
    return lunar.pendiente_grados(dem, mpc)

@st.cache_data
def horizonte(dem, fila, col, mpc, mastil):
    return lunar.perfil_horizonte(dem, fila, col, mpc, altura_mastil=mastil)

@st.cache_data
def resolver_cielo(fechas, lat, lon, rumbo):
    return lunar.efemerides(fechas, lat, lon, rumbo)

@st.cache_data
def resolver_evaluacion_multidia(dem_vis, mpc_vis, fechas_mision, lat, lon, rumbo, sesgo_comms):
    return lunar.evaluar_mision_multidia(dem_vis, mpc_vis, fechas_mision, lat, lon, rumbo, ponderacion_comms=sesgo_comms)

@st.cache_data
def resolver_ventanas_anuales(dem, fila, col, mpc, lat, lon, rumbo, f_ini, dur_estancia, p_sol, p_dte, mastil):
    return lunar.buscar_ventanas_anuales(
        dem, fila, col, mpc, lat, lon, rumbo, f_ini, 
        dias_busqueda=365, duracion_estancia=dur_estancia, 
        min_sol_pct=p_sol, min_dte_pct=p_dte, mastil=mastil
    )

# ----------------------------------------------------------------- SIDEBAR EJECUTIVO LIMPIO
stems = sorted(p.stem for p in CARPETA_MAPAS.glob("*.json"))
st.sidebar.markdown(f"### {TXT['telemetria_sidebar']}")

def formatear_sitio(s):
    item = CATALOGO_NASA.get(s, {})
    cat = item.get("categoria", "LOLA DEM")
    nom = item.get("nombre_es" if st.session_state.idioma == "ES" else "nombre_en", s)
    return f"[{cat}] {nom}"

stem = st.sidebar.selectbox(TXT["sitio_label"], stems, format_func=formatear_sitio)

PERFILES_DURACION = {
    "🚀 Artemis III Crewed (7 d / 150 h)": 7,
    "🤖 CLPS Commercial Lander (14 d / 1 Lunar Day)": 14,
    "🛰️ Long-Duration Polar Rover (28 d)": 28
}
perfil_elegido = st.sidebar.selectbox(TXT["perfil_label"], list(PERFILES_DURACION.keys()), index=0)
duracion_mision = PERFILES_DURACION[perfil_elegido]

# Aplicar fecha pendiente de forma segura
if "fecha_pendiente" in st.session_state:
    st.session_state.fecha_picker = st.session_state.pop("fecha_pendiente")

if "fecha_picker" not in st.session_state:
    st.session_state.fecha_picker = date(2026, 10, 10)

fecha_ini = st.sidebar.date_input(
    TXT["inicio_label"], 
    min_value=date(2000, 1, 1), 
    max_value=date(2049, 12, 31),
    key="fecha_picker"
)

sesgo_tactico = st.sidebar.slider(
    TXT["prioridad_label"],
    min_value=0.0,
    max_value=1.0,
    value=0.5,
    step=0.05,
    help=TXT["prioridad_help"]
)

# Carga de DEM LOLA
dem, meta = cargar_mapa(stem)
filas, columnas = dem.shape
km, mpc = meta["km"], meta["mpc"]
paso = max(1, max(dem.shape) // MAX_CELDAS_3D)

dem_vis = dem[::paso, ::paso]
pend = mapa_pendientes(dem, mpc)
pend_vis = pend[::paso, ::paso]

# Ventana temporal de misión
fechas_ventana = [datetime.combine(fecha_ini, time(12)) + timedelta(days=i) for i in range(duracion_mision)]
ef_ventana = resolver_cielo(fechas_ventana, meta["lat"], meta["lon"], meta["rumbo"])

# Evaluación Multidía
idoneidad_matriz, sol_acum_matriz, dte_acum_matriz = resolver_evaluacion_multidia(
    dem_vis, mpc * paso, fechas_ventana, meta["lat"], meta["lon"], meta["rumbo"], sesgo_tactico
)
top5 = lunar.top_sitios_aterrizaje(idoneidad_matriz, pend_vis, dem_vis, max_pend=LIMITE_PRECAUCION, n_sitios=5)

# ------------------------------------------------------------- BOTÓN DE AUTO-OPTIMIZACIÓN
if st.sidebar.button(TXT["btn_auto_opt"], use_container_width=True, type="primary"):
    if top5:
        f_top1, c_top1 = top5[0]["fila"] * paso, top5[0]["col"] * paso
        st.session_state.coord_col = min(c_top1, columnas - 1)
        st.session_state.coord_fila = min(f_top1, filas - 1)
        
        _, _, vent_opt = lunar.buscar_ventanas_anuales(
            dem, st.session_state.coord_fila, st.session_state.coord_col, mpc,
            meta["lat"], meta["lon"], meta["rumbo"],
            datetime.combine(fecha_ini, time(12)), dias_busqueda=365,
            duracion_estancia=duracion_mision, min_sol_pct=80.0, min_dte_pct=50.0, mastil=2.0
        )
        if vent_opt:
            mejor_v = max(vent_opt, key=lambda x: x["score"])
            st.session_state.fecha_pendiente = datetime.strptime(mejor_v["t0"], "%Y-%m-%d").date()
        st.session_state.dia_cursor_val = 1
        st.session_state.auto_opt_ok = True
        st.rerun()

# ------------------------------------------------------------- DESPLEGABLES SECUNDARIOS (EXPANDERS)
with st.sidebar.expander(TXT["autopilot_expander"], expanded=False):
    if top5:
        if st.button(TXT["btn_top1"], use_container_width=True):
            st.session_state.coord_col = min(top5[0]["col"] * paso, columnas - 1)
            st.session_state.coord_fila = min(top5[0]["fila"] * paso, filas - 1)
            st.rerun()

        opciones_top = {f"#{s['rank']} · Score {s['score']}% (Pend: {s['pendiente']}°)": s for s in top5}
        seleccion_top = st.selectbox(TXT["select_top"], list(opciones_top.keys()))
        if st.button(TXT["btn_nav"], use_container_width=True):
            sitio_elegido = opciones_top[seleccion_top]
            st.session_state.coord_col = min(sitio_elegido["col"] * paso, columnas - 1)
            st.session_state.coord_fila = min(sitio_elegido["fila"] * paso, filas - 1)
            st.rerun()

with st.sidebar.expander(TXT["manual_expander"], expanded=False):
    altura_mastil = st.slider(
        TXT["mastil_label"], 
        1.0, 15.0, 2.0, 0.5,
        help="1-2m: Micro-Rover / CLPS | 10m+: Starship HLS / Blue Moon"
    )
    col = st.slider(TXT["eje_x"], 0, columnas - 1, st.session_state.get("coord_col", columnas // 2))
    fila = st.slider(TXT["eje_y"], 0, filas - 1, st.session_state.get("coord_fila", filas // 2))
    st.session_state.coord_col = col
    st.session_state.coord_fila = fila

# ------------------------------------------------------------- INICIALIZACIÓN DE COORDENADAS Y DÍA
if "coord_col" not in st.session_state or "coord_fila" not in st.session_state:
    if top5:
        st.session_state.coord_col = min(top5[0]["col"] * paso, columnas - 1)
        st.session_state.coord_fila = min(top5[0]["fila"] * paso, filas - 1)
    else:
        st.session_state.coord_col = columnas // 2
        st.session_state.coord_fila = filas // 2

if "dia_cursor_val" not in st.session_state:
    dias_buenos = [i + 1 for i, el in enumerate(ef_ventana["sol_el"]) if el > 0.4]
    st.session_state.dia_cursor_val = dias_buenos[0] if dias_buenos else 1

st.session_state.dia_cursor_val = max(1, min(st.session_state.dia_cursor_val, duracion_mision))
dia_cursor = st.session_state.dia_cursor_val

fila = st.session_state.coord_fila
col = st.session_state.coord_col

# ----------------------------------------------------------------- CÁLCULOS DEL PUNTO SELECCIONADO
idx_dia = dia_cursor - 1
sol_az, sol_el = float(ef_ventana["sol_az"][idx_dia]), float(ef_ventana["sol_el"][idx_dia])
tierra_az, tierra_el = float(ef_ventana["tierra_az"][idx_dia]), float(ef_ventana["tierra_el"][idx_dia])

pendiente = float(pend[fila, col])
altura = float(dem[fila, col])
horiz = horizonte(dem, fila, col, mpc, altura_mastil)

sol_ok = bool(lunar.visible(sol_el, sol_az, horiz, radio=lunar.RADIO_SOL))
tierra_ok = bool(lunar.visible(tierra_el, tierra_az, horiz))
fecha_activa = datetime.combine(fecha_ini, time(12)) + timedelta(days=idx_dia)

p_bruta, p_neta, solar_flux = lunar.calcular_potencia_electrica(sol_ok, sol_el, area_m2=2.0)
dsn_angulos = lunar.telemetria_dsn(fecha_activa)
dsn_lock = any(ang > 10.0 for ang in dsn_angulos.values())

f_vis, c_vis = min(fila // paso, dem_vis.shape[0] - 1), min(col // paso, dem_vis.shape[1] - 1)
score_local = float(idoneidad_matriz[f_vis, c_vis])
sol_acum_local = float(sol_acum_matriz[f_vis, c_vis])
dte_acum_local = float(dte_acum_matriz[f_vis, c_vis])

xs = np.linspace(-km / 2, km / 2, dem_vis.shape[1])
ys = np.linspace(-km / 2, km / 2, dem_vis.shape[0])
px, py = -km / 2 + km * col / (columnas - 1), -km / 2 + km * fila / (filas - 1)

top_xs = [-km / 2 + km * (s["col"] * paso) / (columnas - 1) for s in top5]
top_ys = [-km / 2 + km * (s["fila"] * paso) / (filas - 1) for s in top5]

luz_dia = lunar.sombreado(dem_vis, mpc * paso, sol_az, sol_el)
sombra_dia = lunar.sombras_proyectadas(dem_vis, mpc * paso, sol_az, sol_el)
brillo_dia = np.where(sombra_dia, 0.02, luz_dia)

if st.session_state.idioma == "ES":
    h_este, h_norte = "Este", "Norte"
    h_luz_t, h_luz_v = "🛰️ Iluminación Rasante", "Factor Luz"
    h_pend_t, h_pend_v = "📐 Topografía Mecánica", "Inclinación"
    h_score_t, h_score_v = "🎯 Matriz Táctica L-SEA", "Idoneidad Multidía"
    h_pos = "🎯 Módulo Lunar HLS"
else:
    h_este, h_norte = "East", "North"
    h_luz_t, h_luz_v = "🛰️ Solar Illumination", "Light Factor"
    h_pend_t, h_pend_v = "📐 Mechanical Topography", "Slope Angle"
    h_score_t, h_score_v = "🎯 L-SEA Tactical Matrix", "Multi-Day Score"
    h_pos = "🎯 HLS Lunar Lander"

# ------------------------------------------------------------ INTERFAZ
st.title("🌔 L-SEA · LUNAR SITE EVALUATION ALGORITHM")

# Banner de éxito tras Auto-Optimización
if st.session_state.get("auto_opt_ok", False):
    st.success(
        f"⚡ **MISIÓN AUTO-OPTIMIZADA CON ÉXITO:** Sitio Top #1 seleccionado · "
        f"Lanzamiento fijado para {fecha_ini:%d/%m/%Y} · Ventana de {duracion_mision} días · Score: {score_local:.1f}%"
    )
    st.session_state.auto_opt_ok = False

# HUD Telemetría de Vuelo en tiempo real
st.markdown(f"""
<div style="background:rgba(8, 14, 29, 0.85); border:1px solid rgba(0, 240, 255, 0.3); padding:14px 20px; border-radius:6px; margin-bottom:20px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; box-shadow: 0 0 20px rgba(0, 240, 255, 0.08);">
    <div>
        <span style="color:#64748b; font-family:'JetBrains Mono'; font-size:0.7rem;">{TXT['hud_target']}</span><br>
        <b style="color:#00f0ff; font-family:'Orbitron'; font-size:1.05rem;">{CATALOGO_NASA.get(stem, {}).get('nombre_es' if st.session_state.idioma=='ES' else 'nombre_en', stem).upper()}</b>
    </div>
    <div>
        <span style="color:#64748b; font-family:'JetBrains Mono'; font-size:0.7rem;">{TXT['hud_time']}</span><br>
        <span style="font-family:'JetBrains Mono'; color:#f8fafc; font-size:0.95rem;">{fecha_activa:%d/%m/%Y} · T+{dia_cursor:02d}D / {duracion_mision}D</span>
    </div>
    <div>
        <span style="color:#64748b; font-family:'JetBrains Mono'; font-size:0.7rem;">{TXT['hud_dte']}</span><br>
        {f'<span class="tag-go">● AOS DTE LOCK</span>' if (tierra_ok and dsn_lock) else ('<span class="tag-warn">⚠ VISIBLE / DSN GAP</span>' if tierra_ok else '<span class="tag-nogo">○ LOS OCCLUDED</span>')}
    </div>
    <div>
        <span style="color:#64748b; font-family:'JetBrains Mono'; font-size:0.7rem;">POTENCIA EPS ({altura_mastil:.1f}m)</span><br>
        {f'<span class="tag-go">● {p_bruta:.0f} W (NETO: {p_neta:+.0f} W)</span>' if sol_ok else '<span class="tag-nogo">○ ECLIPSE / BATERÍA (-100 W)</span>'}
    </div>
    <div>
        <span style="color:#64748b; font-family:'JetBrains Mono'; font-size:0.7rem;">{TXT['hud_safety']}</span><br>
        {f'<span class="tag-go">{TXT["tag_nominal"]}</span>' if pendiente < LIMITE_OPTIMO else (f'<span class="tag-warn">{TXT["tag_caution"]}</span>' if pendiente <= LIMITE_PRECAUCION else f'<span class="tag-nogo">{TXT["tag_hazard"]}</span>')}
    </div>
</div>
""", unsafe_allow_html=True)

tab3d, tabluz, tabpend, tabscore, tabwindows, tabbmrk = st.tabs([
    TXT["tab_3d"], TXT["tab_sol"], TXT["tab_pend"], TXT["tab_score"], TXT["tab_windows"], TXT["tab_benchmark"]
])

with tab3d:
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        modo_shader = st.radio(TXT["shader_mode"], [TXT["shader_opt1"], TXT["shader_opt2"]], horizontal=True)
    with col_t2:
        relieve_exag = st.slider(TXT["z_exag"], 1.0, 3.0, 1.3, 0.1)

    rad_az, rad_el = np.radians(sol_az), np.radians(max(sol_el, 0.1))
    sun_x = float(np.sin(rad_az) * np.cos(rad_el)) * 1000.0
    sun_y = float(np.cos(rad_az) * np.cos(rad_el)) * 1000.0
    sun_z = float(np.sin(rad_el)) * 1000.0

    if modo_shader == TXT["shader_opt1"]:
        color_superficie = brillo_dia
        escala_color = ESCALA_REGOLITO
        c_min, c_max = 0.0, 1.0
    else:
        color_superficie = sol_acum_matriz
        escala_color = [
            [0.0, "#010409"],
            [0.15, "#0d2b45"],
            [0.40, "#203c56"],
            [0.65, "#f39c12"],
            [0.85, "#f1c40f"],
            [1.0, "#ffffff"]
        ]
        c_min, c_max = 0.0, 100.0

    z_render = (dem_vis / 1000.0) * relieve_exag
    altura_hls_render = (altura / 1000.0 + (altura_mastil / 1000.0) + 0.08) * relieve_exag

    fig3d = go.Figure([
        go.Surface(
            x=xs, y=ys, z=z_render,
            surfacecolor=color_superficie,
            colorscale=escala_color,
            cmin=c_min, cmax=c_max,
            showscale=True if modo_shader == TXT["shader_opt2"] else False,
            lighting=dict(ambient=0.25, diffuse=0.85, specular=0.4, roughness=0.9, fresnel=0.3),
            lightposition=dict(x=sun_x, y=sun_y, z=sun_z),
            customdata=dem_vis,
            hovertemplate=(
                f"<b>{h_luz_t}</b><br>"
                f"{h_este}: %{{x:+.2f}} km<br>"
                f"{h_norte}: %{{y:+.2f}} km<br>"
                "Cota: <b>%{{customdata:,.0f}} m</b>"
                "<extra></extra>"
            )
        ),
        go.Scatter3d(
            x=[px + 3.0, px], y=[py + 3.0, py], z=[altura_hls_render + 1.2, altura_hls_render],
            mode="lines", line=dict(color="#00f0ff", width=4, dash="dash"),
            name="Approach Vector", hoverinfo="none"
        ),
        go.Scatter3d(
            x=[px], y=[py], z=[altura_hls_render],
            mode="markers+text", text=["HLS TOUCHDOWN"], textposition="top center",
            textfont=dict(family="Orbitron", color="#00f0ff", size=10),
            marker=dict(size=8, color="#00f0ff", symbol="diamond", line=dict(color="#ffffff", width=2)),
            name=f"HLS ({altura_mastil:.1f}m)",
            hovertemplate=(
                f"<b>{h_pos}</b><br>"
                f"{h_este}: %{{x:+.2f}} km<br>"
                f"{h_norte}: %{{y:+.2f}} km<br>"
                f"Cota: <b>{altura:,.0f} m</b>"
                "<extra></extra>"
            )
        ),
    ])
    fig3d.update_layout(
        **TEMA_TACTICO, height=560, margin=dict(l=0, r=0, t=0, b=0),
        scene=dict(
            xaxis=dict(title=f"{h_este} (km)", gridcolor="#162238", backgroundcolor="#040711"),
            yaxis=dict(title=f"{h_norte} (km)", gridcolor="#162238", backgroundcolor="#040711"),
            zaxis=dict(title="Elevación Relativa", gridcolor="#162238", backgroundcolor="#040711"),
            aspectmode="data",
            camera=dict(eye=dict(x=-1.4, y=-1.4, z=1.2), center=dict(x=0, y=0, z=-0.1))
        )
    )
    st.plotly_chart(fig3d, use_container_width=True)

with tabluz:
    figl = go.Figure([
        go.Heatmap(
            x=xs, y=ys, z=brillo_dia, colorscale="gray", zmin=0, zmax=1, showscale=False,
            hovertemplate=f"<b>{h_luz_t}</b><br>{h_este}: %{{x:+.2f}} km<br>{h_norte}: %{{y:+.2f}} km<br>{h_luz_v}: <b>%{{z:.1%}}</b><extra></extra>"
        ),
        go.Scatter(
            x=[px], y=[py], mode="markers", name="HLS",
            marker=dict(size=13, color="#00f0ff", line=dict(width=2, color="white")),
            hovertemplate=f"<b>{h_pos}</b><br>{h_este}: %{{x:+.2f}} km<br>{h_norte}: %{{y:+.2f}} km<extra></extra>"
        )
    ])
    figl.update_layout(
        **TEMA_TACTICO, height=520, margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(title=f"{h_este} (km)", gridcolor="#162238"), 
        yaxis=dict(title=f"{h_norte} (km)", gridcolor="#162238", scaleanchor="x")
    )
    st.plotly_chart(figl, use_container_width=True)

with tabpend:
    figp = go.Figure([
        go.Heatmap(
            x=xs, y=ys, z=pend_vis, colorscale="RdYlGn_r", zmin=0, zmax=30, 
            colorbar=dict(title="Pendiente (°)" if st.session_state.idioma == "ES" else "Slope (°)", tickfont=dict(color="#00f0ff")),
            hovertemplate=f"<b>{h_pend_t}</b><br>{h_este}: %{{x:+.2f}} km<br>{h_norte}: %{{y:+.2f}} km<br>{h_pend_v}: <b>%{{z:.1f}}°</b><extra></extra>"
        ),
        go.Scatter(
            x=[px], y=[py], mode="markers", name="HLS",
            marker=dict(size=13, color="white", line=dict(width=2, color="black")),
            hovertemplate=f"<b>{h_pos}</b><br>{h_este}: %{{x:+.2f}} km<br>{h_norte}: %{{y:+.2f}} km<extra></extra>"
        )
    ])
    figp.update_layout(
        **TEMA_TACTICO, height=520, margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(title=f"{h_este} (km)", gridcolor="#162238"), 
        yaxis=dict(title=f"{h_norte} (km)", gridcolor="#162238", scaleanchor="x")
    )
    st.plotly_chart(figp, use_container_width=True)

with tabscore:
    fig_score = go.Figure([
        go.Heatmap(
            x=xs, y=ys, z=idoneidad_matriz, colorscale="Plasma", zmin=0, zmax=100, 
            colorbar=dict(title="Score (%)", tickfont=dict(color="#00f0ff")),
            hovertemplate=f"<b>{h_score_t}</b><br>{h_este}: %{{x:+.2f}} km<br>{h_norte}: %{{y:+.2f}} km<br>{h_score_v}: <b>%{{z:.1f}}%</b><extra></extra>"
        ),
        go.Scatter(
            x=top_xs, y=top_ys, mode="markers+text", 
            text=[f"#{s['rank']}" for s in top5], 
            textposition="top center",
            textfont=dict(family="Orbitron", color="#ffb81c", size=11),
            marker=dict(size=11, color="#ffb81c", symbol="star", line=dict(width=1, color="black")),
            hovertemplate=f"<b>⭐ Zona Segura %{{text}}</b><br>{h_este}: %{{x:+.2f}} km<br>{h_norte}: %{{y:+.2f}} km<extra></extra>"
        ),
        go.Scatter(
            x=[px], y=[py], mode="markers", name="HLS",
            marker=dict(size=14, color="#00f0ff", symbol="diamond", line=dict(width=2, color="white")),
            hovertemplate=f"<b>{h_pos}</b><br>{h_este}: %{{x:+.2f}} km<br>{h_norte}: %{{y:+.2f}} km<extra></extra>"
        )
    ])
    fig_score.update_layout(
        **TEMA_TACTICO, height=520, margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(title=f"{h_este} (km)", gridcolor="#162238"), 
        yaxis=dict(title=f"{h_norte} (km)", gridcolor="#162238", scaleanchor="x")
    )
    st.plotly_chart(fig_score, use_container_width=True)

# ----------------------------------------------------------------- PESTAÑA 5: WINDOW FINDER
with tabwindows:
    st.markdown("### 🚀 BUSCADOR DE VENTANAS OPERATIVAS ANUALES (365 DÍAS)")
    st.caption("Filtro orbital de viabilidad de vuelo: simula todas las ventanas de aterrizaje posibles del año para el punto seleccionado.")

    c_wf1, c_wf2, c_wf3 = st.columns(3)
    with c_wf1:
        st.markdown(f"**Perfil Vinculado:** `{perfil_elegido}`")
        dur_dias_wf = duracion_mision
    with c_wf2:
        min_sol_wf = st.slider("Mínimo Sol Requerido (%)", 50, 100, 80, 5)
    with c_wf3:
        min_dte_wf = st.slider("Mínimo Enlace DTE Requerido (%)", 20, 100, 50, 5)

    f_inicio_dt = datetime.combine(fecha_ini, time(12))
    mascara_anual, fechas_anuales, ventanas_encontradas = resolver_ventanas_anuales(
        dem, fila, col, mpc, meta["lat"], meta["lon"], meta["rumbo"],
        f_inicio_dt, dur_dias_wf, min_sol_wf, min_dte_wf, altura_mastil
    )

    dias_viables_total = int(mascara_anual.sum())
    st.markdown(f"""
    <div style="background: rgba(10, 18, 36, 0.7); border-left: 4px solid #00f0ff; padding: 12px 18px; border-radius: 4px; margin-bottom: 15px;">
        <span style="font-family:'Orbitron'; font-size: 1.1rem; color:#00f0ff;">RESUMEN DE MANIFIESTO DE VUELO: {dias_viables_total} de 365 días viables</span><br>
        <span style="font-family:'JetBrains Mono'; font-size: 0.85rem; color:#94a3b8;">
            Oportunidades óptimas detectadas: <b>{len(ventanas_encontradas)}</b> · Primera ventana abierta: <b>{ventanas_encontradas[0]['t0'] if ventanas_encontradas else 'Ninguna en rango'}</b>
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### 📅 CALENDARIO DE VIABILIDAD OPERACIONAL (FEASIBILITY CALENDAR)")
    dias_eje = [f.strftime("%d/%m") for f in fechas_anuales]
    
    fig_cal = go.Figure(go.Heatmap(
        z=[mascara_anual],
        x=dias_eje,
        y=["Viabilidad"],
        colorscale=[[0, "#162238"], [1, "#10b981"]],
        showscale=False,
        hovertemplate="<b>Día: %{x}</b><br>Estado: %{z}<extra></extra>"
    ))
    fig_cal.update_layout(
        **TEMA_TACTICO, height=130, margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(title="Línea Temporal Anual (365 Días)", nticks=12, gridcolor="#080e1d"),
        yaxis=dict(showticklabels=False)
    )
    st.plotly_chart(fig_cal, use_container_width=True)

    st.markdown("#### 📋 MANIFIESTO DE VENTANAS DE ATERRIZAJE ÓPTIMAS")

    if ventanas_encontradas:
        opciones_ventanas = {
            f"🎯 Ventana #{i+1} · T0: {v['t0']} (Score: {v['score']}%) · Sol: {v['sol_pct']}% · DTE: {v['dte_pct']}%": v
            for i, v in enumerate(ventanas_encontradas)
        }
        
        c_v1, c_v2 = st.columns([3, 1])
        with c_v1:
            sel_txt = st.selectbox(
                "Seleccionar Ventana Óptima", 
                list(opciones_ventanas.keys()), 
                label_visibility="collapsed"
            )
        with c_v2:
            if st.button("🚀 CARGAR FECHA T0", use_container_width=True):
                v_elegida = opciones_ventanas[sel_txt]
                nueva_f = datetime.strptime(v_elegida["t0"], "%Y-%m-%d").date()
                st.session_state.fecha_pendiente = nueva_f
                st.session_state.dia_cursor_val = 1
                st.toast(f"🚀 Ventana Cargada: {nueva_f.strftime('%d/%m/%Y')}", icon="🌔")
                st.rerun()

        df_ventanas = pd.DataFrame(ventanas_encontradas)
        df_ventanas.columns = ["Apertura T0", "Cierre Ventana", "Sol Promedio (%)", "DTE Promedio (%)", "Score L-SEA", "Días Viables", "Mejor T0"]
        
        evento_tabla = st.dataframe(
            df_ventanas[["Mejor T0", "Apertura T0", "Cierre Ventana", "Días Viables", "Sol Promedio (%)", "DTE Promedio (%)", "Score L-SEA"]],
            use_container_width=True,
            on_select="rerun",
            selection_mode="single-row"
        )
        
        filas_sel = []
        if hasattr(evento_tabla, "selection") and evento_tabla.selection:
            filas_sel = getattr(evento_tabla.selection, "rows", [])
        elif isinstance(evento_tabla, dict) and "selection" in evento_tabla:
            filas_sel = evento_tabla["selection"].get("rows", [])
            
        if len(filas_sel) > 0:
            idx = filas_sel[0]
            fecha_str = df_ventanas.iloc[idx]["Mejor T0"]
            nueva_f = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            if nueva_f != st.session_state.fecha_picker:
                st.session_state.fecha_pendiente = nueva_f
                st.session_state.dia_cursor_val = 1
                st.toast(f"🚀 Ventana Cargada: {nueva_f.strftime('%d/%m/%Y')}", icon="🌔")
                st.rerun()

        csv_data = df_ventanas.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Manifiesto de Vuelo (CSV)",
            data=csv_data,
            file_name=f"L-SEA_Flight_Windows_{stem}.csv",
            mime="text/csv",
        )
    else:
        st.warning("No se encontraron ventanas operativas que cumplan con los umbrales exigidos para este punto.")

# ----------------------------------------------------------------- PESTAÑA 6: BENCHMARK COMPARATIVO
with tabbmrk:
    st.markdown("### ⚖️ BENCHMARK COMPARATIVO DIRECTO (NASA SITE BENCHMARK)")
    st.caption("Comparativa multicriterio lado a lado para la ventana operativa seleccionada (Cumple el reto oficial de evaluación).")

    dem_sh, meta_sh = cargar_mapa("shackleton")
    dem_ml, meta_ml = cargar_mapa("malapert")
    
    paso_bm = max(1, max(dem_sh.shape) // 150)
    pend_sh = lunar.pendiente_grados(dem_sh, meta_sh["mpc"])
    pend_ml = lunar.pendiente_grados(dem_ml, meta_ml["mpc"])

    score_sh_mat, sol_sh_mat, dte_sh_mat = lunar.evaluar_mision_multidia(
        dem_sh[::paso_bm, ::paso_bm], meta_sh["mpc"] * paso_bm, fechas_ventana,
        meta_sh["lat"], meta_sh["lon"], meta_sh["rumbo"], sesgo_tactico
    )
    score_ml_mat, sol_ml_mat, dte_ml_mat = lunar.evaluar_mision_multidia(
        dem_ml[::paso_bm, ::paso_bm], meta_ml["mpc"] * paso_bm, fechas_ventana,
        meta_ml["lat"], meta_ml["lon"], meta_ml["rumbo"], sesgo_tactico
    )

    score_sh_top = float(score_sh_mat.max())
    score_ml_top = float(score_ml_mat.max())
    sol_sh_med = float(sol_sh_mat.mean())
    sol_ml_med = float(sol_ml_mat.mean())
    dte_sh_med = float(dte_sh_mat.mean())
    dte_ml_med = float(dte_ml_mat.mean())

    df_benchmark = pd.DataFrame({
        "Parámetro Operacional": [
            "Coordenadas Centroides",
            "Elevación Media Terreno",
            "Pendiente Típica de Aterrizaje",
            "Insolación Media en Misión",
            "Visibilidad Directa DTE",
            "Score Multicriterio L-SEA (Top)",
            "Veredicto Táctico"
        ],
        "Cráter Shackleton (Connecting Ridge)": [
            f"{meta_sh['lat']}° S, {meta_sh['lon']}° E",
            f"{dem_sh.mean():,.0f} m",
            f"{pend_sh[filas//2, columnas//2]:.1f}° (Zona Meseta)",
            f"{sol_sh_med:.1f}%",
            f"{dte_sh_med:.1f}%",
            f"<b>{score_sh_top:.1f}%</b>",
            "🏆 RECOMENDADO" if score_sh_top >= score_ml_top else "SEGUNDA OPCIÓN"
        ],
        "Macizo Malapert (Cresta Artemis)": [
            f"{meta_ml['lat']}° S, {meta_ml['lon']}° E",
            f"{dem_ml.mean():,.0f} m",
            f"{pend_ml[filas//2, columnas//2]:.1f}° (Cresta Alta)",
            f"{sol_ml_med:.1f}%",
            f"{dte_ml_med:.1f}%",
            f"<b>{score_ml_top:.1f}%</b>",
            "🏆 RECOMENDADO" if score_ml_top > score_sh_top else "SEGUNDA OPCIÓN"
        ]
    })

    st.markdown(df_benchmark.to_html(escape=False, index=False), unsafe_allow_html=True)
    st.caption("Evaluación calculada con el modelo IAU/JPL y coeficientes de seguridad de tren de aterrizaje Artemis.")

# ----------------------------------------------------------------- TELEMETRÍA DETALLADA
st.markdown(f"### {TXT['sec_telemetria']}")
a, b, c, d = st.columns(4)

with a:
    st.markdown(f"#### ⛰️ {TXT['met_elev']}")
    st.metric("Elevación", f"{altura:,.0f} m")
    if pendiente < LIMITE_OPTIMO:
        st.success(f"Pendiente {pendiente:.1f}° — Óptimo")
    elif pendiente <= LIMITE_PRECAUCION:
        st.warning(f"Pendiente {pendiente:.1f}° — Precaución")
    else:
        st.error(f"Pendiente {pendiente:.1f}° — Crítico")

with b:
    st.markdown(f"#### 🌍 {TXT['met_tierra']}")
    st.metric(f"Elev. ({duracion_mision}D)", f"{tierra_el:.1f}° · DTE {dte_acum_local:.0f}%")
    if tierra_ok and dsn_lock:
        st.success("AOS DTE Lock Activo")
    elif tierra_ok:
        st.warning("LOS Tierra OK (Gap DSN)")
    else:
        st.error("Bloqueado por relieve")

with c:
    st.markdown(f"#### ☀️ POTENCIA SOLAR (EPS)")
    st.metric("Generación / Neto", f"{p_bruta:.0f} W / {p_neta:+.0f} W")
    if sol_ok:
        st.success(f"Flujo: {solar_flux:.0f} W/m² (GaAs 29%)")
    else:
        st.error("Eclipse lunar (Batería -100W)")

with d:
    st.markdown(f"#### 🎯 {TXT['met_score']}")
    st.metric("Índice Multidía", f"{score_local:.1f}%")
    if score_local >= 75:
        st.success(TXT["tier1"])
    elif score_local >= 50:
        st.warning(TXT["tier2"])
    else:
        st.error(TXT["tier3"])

# Tarjetas DSN
st.markdown("#### 📡 ESTADO DE LA RED DE ESPACIO PROFUNDO (NASA DSN)")
dsn_html = ""
for nombre, ang in dsn_angulos.items():
    clase = "dsn-on" if ang > 10.0 else "dsn-off"
    icono = "●" if ang > 10.0 else "○"
    dsn_html += f'<span class="dsn-pill {clase}">{icono} {nombre}: {ang:+.1f}°</span>'
st.markdown(dsn_html, unsafe_allow_html=True)

# Horizonte con trayectorias continuas
st.markdown(f"### {TXT['graf_horiz']} (Mástil {altura_mastil:.1f}m)")
figh = go.Figure([
    go.Scatter(x=np.arange(360), y=horiz, fill="tozeroy", name="Relieve Local", line=dict(color="#475569", width=2), fillcolor="rgba(30, 41, 59, 0.6)"),
    go.Scatter(x=ef_ventana["sol_az"], y=ef_ventana["sol_el"], mode="lines", name="Órbita Solar (Track)", line=dict(color="#ffb81c", width=1.5, dash="dot")),
    go.Scatter(x=ef_ventana["tierra_az"], y=ef_ventana["tierra_el"], mode="lines", name="Libración Tierra (Track)", line=dict(color="#00f0ff", width=1.5, dash="dot")),
    go.Scatter(x=[sol_az], y=[sol_el], mode="markers", name="Sol Activo", marker=dict(size=18, color="#ffb81c", line=dict(width=2, color="#ffffff"))),
    go.Scatter(x=[tierra_az], y=[tierra_el], mode="markers", name="Tierra Activa", marker=dict(size=18, color="#00f0ff", line=dict(width=2, color="#ffffff"))),
])
figh.update_layout(
    **TEMA_TACTICO, height=340, margin=dict(l=0, r=0, t=10, b=0),
    xaxis=dict(title="Azimut Local (0°=N, 90°=Este, 180°=Sur, 270°=Oeste)", range=[0, 360], dtick=45, gridcolor="#162238"),
    yaxis=dict(title="Elevación (°)", range=[-8, max(horiz.max() + 4, 12)], gridcolor="#162238")
)
st.plotly_chart(figh, use_container_width=True)

# ==============================================================================
# LÍNEA DE TIEMPO INTERACTIVA Y CLICABLE (TOUCH CONTROL SURFACE)
# ==============================================================================
st.markdown(f"### {TXT['graf_timeline']} ({duracion_mision} DÍAS)")

c_nav1, c_nav2, c_nav3 = st.columns([1, 4, 1])
with c_nav1:
    if st.button("◀ T-1", use_container_width=True, disabled=(st.session_state.dia_cursor_val <= 1)):
        st.session_state.dia_cursor_val -= 1
        st.rerun()
with c_nav2:
    st.markdown(
        f"<div style='text-align:center; font-family:Orbitron; color:#00f0ff; font-size:1.05rem; padding-top:6px;'>"
        f"INSPECCIONANDO DÍA: <b>T+{dia_cursor}</b> ({fecha_activa:%d/%m/%Y}) · <span style='font-size:0.8rem; color:#94a3b8; font-family:JetBrains Mono;'>CLIC EN CUALQUIER COLUMNA PARA SALTAR</span>"
        f"</div>",
        unsafe_allow_html=True
    )
with c_nav3:
    if st.button("T+1 ▶", use_container_width=True, disabled=(st.session_state.dia_cursor_val >= duracion_mision)):
        st.session_state.dia_cursor_val += 1
        st.rerun()

vis_sol = lunar.visible(ef_ventana["sol_el"], ef_ventana["sol_az"], horiz, radio=lunar.RADIO_SOL)
vis_tierra = lunar.visible(ef_ventana["tierra_el"], ef_ventana["tierra_az"], horiz)
vis = np.array([vis_sol, vis_tierra]).astype(int)

if st.session_state.idioma == "ES":
    texto_estado = np.array([
        ["ILUMINADO (Generación OK)" if s else "EN SOMBRA (Batería)" for s in vis_sol],
        ["ENLACE DTE ACTIVO" if t else "BLOQUEADO POR RELIEVE" for t in vis_tierra]
    ])
    lbl_dia, lbl_estado = "Día", "Telemetría"
else:
    texto_estado = np.array([
        ["SUNLIT (Power OK)" if s else "IN SHADOW (Battery)" for s in vis_sol],
        ["DTE LINK ACTIVE" if t else "TERRAIN OCCLUDED" for t in vis_tierra]
    ])
    lbl_dia, lbl_estado = "Day", "Telemetry"

dias_list = list(range(1, duracion_mision + 1))
etiquetas = [f"{lunar.icono_fase(f)}<br>T+{d}" for f, d in zip(ef_ventana["fase"], dias_list)]

hover_matrix = np.empty((2, len(dias_list)), dtype=object)
for r, nombre in enumerate(["☀️ Sol", "🌍 Tierra"]):
    for c, d in enumerate(dias_list):
        st_txt = texto_estado[r, c]
        hover_matrix[r, c] = f"<b>{nombre}</b> · {lbl_dia} T+{d}<br>{lbl_estado}: <b>{st_txt}</b>"

figt = go.Figure()

figt.add_trace(go.Heatmap(
    z=vis, 
    x=dias_list, 
    y=["☀️ Sol", "🌍 Tierra"],
    text=hover_matrix,
    hovertemplate="%{text}<extra></extra>",
    colorscale=[
        [0.0, "#3f1010"],
        [0.5, "#3f1010"],
        [0.501, "#10b981"],
        [1.0, "#10b981"]
    ],
    zmin=0,
    zmax=1,
    showscale=False, 
    xgap=4, 
    ygap=4
))

figt.add_trace(go.Scatter(
    x=dias_list * 2,
    y=["☀️ Sol"] * len(dias_list) + ["🌍 Tierra"] * len(dias_list),
    mode="markers",
    marker=dict(size=42, opacity=0.001, color="#00f0ff"),
    hoverinfo="skip",
    showlegend=False
))

figt.add_vline(x=dia_cursor, line_dash="dot", line_color="#00f0ff", line_width=3)

figt.update_layout(
    **TEMA_TACTICO, 
    height=210, 
    margin=dict(l=0, r=0, t=10, b=0),
    dragmode=False,
    clickmode="event+select",
    xaxis=dict(
        title="",
        tickmode="array", 
        tickvals=dias_list, 
        ticktext=etiquetas, 
        gridcolor="#162238",
        fixedrange=True
    ),
    yaxis=dict(gridcolor="#162238", fixedrange=True)
)

evento_timeline = st.plotly_chart(
    figt, 
    use_container_width=True, 
    on_select="rerun", 
    selection_mode="points",
    config={"displayModeBar": False}
)

if evento_timeline:
    sel = getattr(evento_timeline, "selection", None) or evento_timeline.get("selection", {})
    pts = getattr(sel, "points", None) or (sel.get("points") if isinstance(sel, dict) else [])
    if pts:
        p0 = pts[0]
        dia_clicado = getattr(p0, "x", None) if not isinstance(p0, dict) else p0.get("x")
        if dia_clicado is not None:
            try:
                dia_num = int(dia_clicado)
                if dia_num != st.session_state.dia_cursor_val:
                    st.session_state.dia_cursor_val = dia_num
                    st.rerun()
            except (ValueError, TypeError):
                pass

m1, m2, m3 = st.columns(3)
m1.metric(TXT["util_solar"], f"{vis[0].mean():.0%}")
m2.metric(TXT["util_dte"], f"{vis[1].mean():.0%}")
m3.metric(TXT["util_ambos"], f"{(vis[0] & vis[1]).mean():.0%}")
st.caption("Efemérides JPL DE421 + Tracking DSN de NASA resueltas dinámicamente.")