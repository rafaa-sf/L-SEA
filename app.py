# ==============================================================================
# RUTA DEL FICHERO: app.py
# VERSIÓN: EVO 2.6 - ARTEMIS IV AUTOPILOT & TACTICAL SITE RANKER
# ==============================================================================

import json
from datetime import date, datetime, time, timedelta
from pathlib import Path

import numpy as np
import plotly.graph_objects as go
import streamlit as st

import lunar

st.set_page_config(page_title="Artemis IV / CLPS Mission Browser", layout="wide")

# ==============================================================================
# ESTILOS: ARTEMIS IV GLASS COCKPIT HUD
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
        font-size: 1.6rem !important;
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
        letter-spacing: 0.05em;
        box-shadow: 0 0 8px rgba(16, 185, 129, 0.3);
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
        letter-spacing: 0.05em;
        box-shadow: 0 0 8px rgba(239, 68, 68, 0.3);
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
        letter-spacing: 0.05em;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        background-color: #070d1c;
        border-bottom: 1px solid rgba(0, 240, 255, 0.25);
        border-radius: 4px 4px 0 0;
    }
    .stTabs [data-baseweb="tab"] {
        color: #64748b;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
    }
    .stTabs [aria-selected="true"] {
        color: #00f0ff !important;
        border-bottom-color: #00f0ff !important;
    }
</style>
""", unsafe_allow_html=True)


# ------------------------------------------------------------------ CONFIG
CARPETA_MAPAS = Path(__file__).parent / "mapas"
NOMBRES = {
    "shackleton": "Cráter Shackleton (Polo Sur Lunar)",
    "malapert": "Macizo Malapert (Cresta Artemis)",
}
LIMITE_OPTIMO = 5       # Límite nominal de pendiente en grados
LIMITE_PRECAUCION = 10
MAX_CELDAS_3D = 250     # Resolución máxima para renderizado interactivo
DIAS = 30

TEMA_TACTICO = dict(
    paper_bgcolor="#040711",
    plot_bgcolor="#080e1d",
    font=dict(family="JetBrains Mono, monospace", color="#94a3b8"),
)

ESCALA_REGOLITO = [
    [0.0, "#03060c"],      # Región de sombra permanente (PSR)
    [0.15, "#141d2b"],     # Penumbra fría
    [0.45, "#475569"],     # Regolito basáltico medio
    [0.75, "#94a3b8"],     # Anortosita tierras altas
    [1.0, "#fffbeb"]       # Cresta iluminada por Sol rasante
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
def horizonte(dem, fila, col, mpc):
    return lunar.perfil_horizonte(dem, fila, col, mpc)


@st.cache_data
def cielo(fecha_ini, lat, lon, rumbo):
    fechas = [datetime.combine(fecha_ini, time(12)) + timedelta(days=i) for i in range(DIAS)]
    return lunar.efemerides(fechas, lat, lon, rumbo)


@st.cache_data
def iluminacion(dem_vis, mpc_vis, sol_az, sol_el):
    luz = lunar.sombreado(dem_vis, mpc_vis, sol_az, sol_el)
    sombra = lunar.sombras_proyectadas(dem_vis, mpc_vis, sol_az, sol_el)
    return np.where(sombra, 0.02, luz)


# ----------------------------------------------------------------- SIDEBAR & AUTOPILOT
stems = sorted(p.stem for p in CARPETA_MAPAS.glob("*.json"))
st.sidebar.markdown("### 🛰️ TELEMETRÍA ARTEMIS IV")
stem = st.sidebar.selectbox("Sitio Candidato (LOLA DEM)", stems, format_func=lambda s: NOMBRES.get(s, s))
fecha_ini = st.sidebar.date_input(
    "Inicio de Ventana Operativa", 
    date(2026, 10, 10),
    min_value=date(2000, 1, 1), 
    max_value=date(2049, 12, 31)
)
dia = st.sidebar.slider("Día de Misión (T+Días)", 1, DIAS, 10)

dem, meta = cargar_mapa(stem)
filas, columnas = dem.shape
km, mpc = meta["km"], meta["mpc"]
paso = max(1, max(dem.shape) // MAX_CELDAS_3D)

# Cálculos para la malla reducida e Idoneidad Multicriterio
pend = mapa_pendientes(dem, mpc)
dem_vis, pend_vis = dem[::paso, ::paso], pend[::paso, ::paso]

ef = cielo(fecha_ini, meta["lat"], meta["lon"], meta["rumbo"])
i = dia - 1
sol_az, sol_el = float(ef["sol_az"][i]), float(ef["sol_el"][i])
tierra_az, tierra_el = float(ef["tierra_az"][i]), float(ef["tierra_el"][i])

brillo = iluminacion(dem_vis, mpc * paso, round(sol_az, 1), round(sol_el, 2))
idoneidad_mapa = lunar.mapa_idoneidad(pend_vis, brillo, LIMITE_PRECAUCION)

# Detección de las mejores mesetas seguras Top 5 con Deadzone Anti-Glitch
top5 = lunar.top_sitios_aterrizaje(idoneidad_mapa, pend_vis, dem_vis, max_pend=LIMITE_PRECAUCION, n_sitios=5)

# Inicialización de Session State para coordenadas del módulo
if "coord_col" not in st.session_state or "coord_fila" not in st.session_state:
    st.session_state.coord_col = columnas // 2
    st.session_state.coord_fila = filas // 2

st.sidebar.markdown("---")
st.sidebar.markdown("### 🤖 AUTOPILOT (DETECCIÓN DE MESETAS)")

# Panel de control de Autopilot
if top5:
    if st.sidebar.button("🚀 FIJAR MEJOR SITIO (#1 GLOBAL)", use_container_width=True):
        st.session_state.coord_col = min(top5[0]["col"] * paso, columnas - 1)
        st.session_state.coord_fila = min(top5[0]["fila"] * paso, filas - 1)
        st.rerun()

    opciones_top = {f"#{s['rank']} · Score {s['score']}% (Pend: {s['pendiente']}°)": s for s in top5}
    seleccion_top = st.sidebar.selectbox("🎯 Alternativas Top 5 Seguras", list(opciones_top.keys()))
    if st.sidebar.button("📍 NAVEGAR A ESTA COORDENADA", use_container_width=True):
        sitio_elegido = opciones_top[seleccion_top]
        st.session_state.coord_col = min(sitio_elegido["col"] * paso, columnas - 1)
        st.session_state.coord_fila = min(sitio_elegido["fila"] * paso, filas - 1)
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎯 AJUSTE MANUAL HLS")

# Sliders sincronizados con el Session State
col = st.sidebar.slider("Eje X (Este →)", 0, columnas - 1, st.session_state.coord_col)
fila = st.sidebar.slider("Eje Y (Norte ↑)", 0, filas - 1, st.session_state.coord_fila)

# Actualizar el estado si el usuario arrastra los sliders a mano
st.session_state.coord_col = col
st.session_state.coord_fila = fila

st.sidebar.caption(f"DEM LOLA: {km:g} km · {mpc:.0f} m/px · Malla {filas}x{columnas}")
st.sidebar.caption("Anti-Glitch: Buffer 3x3 celdas + Deadzone perimetral 8%.")

# ----------------------------------------------------------------- CÁLCULOS DEL PUNTO SELECCIONADO
pendiente = float(pend[fila, col])
altura = float(dem[fila, col])
horiz = horizonte(dem, fila, col, mpc)

sol_ok = bool(lunar.visible(sol_el, sol_az, horiz, radio=lunar.RADIO_SOL))
tierra_ok = bool(lunar.visible(tierra_el, tierra_az, horiz))
fecha_dia = datetime.combine(fecha_ini, time(12)) + timedelta(days=i)
score_actual = float(idoneidad_mapa[min(fila // paso, idoneidad_mapa.shape[0] - 1), 
                                    min(col // paso, idoneidad_mapa.shape[1] - 1)])

xs = np.linspace(-km / 2, km / 2, dem_vis.shape[1])
ys = np.linspace(-km / 2, km / 2, dem_vis.shape[0])
px, py = -km / 2 + km * col / (columnas - 1), -km / 2 + km * fila / (filas - 1)

# Coordenadas geográficas métricas de los Top 5 para dibujarlos en las figuras
top_xs = [-km / 2 + km * (s["col"] * paso) / (columnas - 1) for s in top5]
top_ys = [-km / 2 + km * (s["fila"] * paso) / (filas - 1) for s in top5]

# ------------------------------------------------------------ INTERFAZ
st.title("🌔 ARTEMIS IV · TACTICAL LUNAR BROWSER")

# HUD Telemetría de Vuelo en tiempo real
st.markdown(f"""
<div style="background:rgba(8, 14, 29, 0.85); border:1px solid rgba(0, 240, 255, 0.3); padding:14px 20px; border-radius:6px; margin-bottom:20px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; box-shadow: 0 0 20px rgba(0, 240, 255, 0.08);">
    <div>
        <span style="color:#64748b; font-family:'JetBrains Mono'; font-size:0.7rem; letter-spacing:0.05em;">OBJETIVO TÁCTICO</span><br>
        <b style="color:#00f0ff; font-family:'Orbitron'; font-size:1.05rem;">{NOMBRES.get(stem, stem).upper()}</b>
    </div>
    <div>
        <span style="color:#64748b; font-family:'JetBrains Mono'; font-size:0.7rem; letter-spacing:0.05em;">TIMESTAMP UTC</span><br>
        <span style="font-family:'JetBrains Mono'; color:#f8fafc; font-size:0.95rem;">{fecha_dia:%d/%m/%Y} · T+{dia:02d}D</span>
    </div>
    <div>
        <span style="color:#64748b; font-family:'JetBrains Mono'; font-size:0.7rem; letter-spacing:0.05em;">ENLACE DIRECTO TIERRA (DTE)</span><br>
        {'<span class="tag-go">● AOS CARRIER LOCK</span>' if tierra_ok else '<span class="tag-nogo">○ LOS OCCLUDED</span>'}
    </div>
    <div>
        <span style="color:#64748b; font-family:'JetBrains Mono'; font-size:0.7rem; letter-spacing:0.05em;">GENERACIÓN FOTOVOLTAICA</span><br>
        {'<span class="tag-go">● SOLAR ILLUMINATED</span>' if sol_ok else '<span class="tag-nogo">○ SHADOW / BATTERY</span>'}
    </div>
    <div>
        <span style="color:#64748b; font-family:'JetBrains Mono'; font-size:0.7rem; letter-spacing:0.05em;">SEGURIDAD TREN ATERRIZAJE</span><br>
        {'<span class="tag-go">NOMINAL (&lt;5°)</span>' if pendiente < LIMITE_OPTIMO else ('<span class="tag-warn">CAUTION (&le;10°)</span>' if pendiente <= LIMITE_PRECAUCION else '<span class="tag-nogo">CRITICAL HAZARD</span>')}
    </div>
</div>
""", unsafe_allow_html=True)

tab3d, tabluz, tabpend, tabscore = st.tabs([
    "🏔️ Topografía 3D (Artemis Shader)", 
    "🌗 Mapa de Iluminación", 
    "📐 Análisis de Pendientes", 
    "🎯 Matriz de Idoneidad (Landing Ranker)"
])

with tab3d:
    fig3d = go.Figure([
        go.Surface(
            x=xs, 
            y=ys, 
            z=dem_vis / 1000, 
            surfacecolor=brillo, 
            colorscale=ESCALA_REGOLITO,
            cmin=0, 
            cmax=1, 
            showscale=False,
            lighting=dict(ambient=0.9, diffuse=0.1, specular=0.1, fresnel=0.1),
            customdata=dem_vis,
            hovertemplate=(
                "<b>🏔️ Relieve Lunar Artemis</b><br>"
                "Este: %{x:+.2f} km<br>"
                "Norte: %{y:+.2f} km<br>"
                "Cota real: <b>%{customdata:,.0f} m</b>"
                "<extra></extra>"
            )
        ),
        go.Scatter3d(
            x=[px], 
            y=[py], 
            z=[altura / 1000 + 0.12], 
            mode="markers",
            marker=dict(size=9, color="#00f0ff", symbol="diamond", line=dict(color="#ffffff", width=2)), 
            name="Módulo HLS",
            hovertemplate=(
                "<b>🚀 Módulo de Aterrizaje HLS</b><br>"
                "Este: %{x:+.2f} km<br>"
                "Norte: %{y:+.2f} km<br>"
                f"Elevación base: <b>{altura:,.0f} m</b>"
                "<extra></extra>"
            )
        ),
    ])
    fig3d.update_layout(
        **TEMA_TACTICO,
        height=540, 
        margin=dict(l=0, r=0, t=0, b=0),
        scene=dict(
            xaxis=dict(title="Distancia Este (km)", gridcolor="#162238", backgroundcolor="#040711"),
            yaxis=dict(title="Distancia Norte (km)", gridcolor="#162238", backgroundcolor="#040711"),
            zaxis=dict(title="Cota (km)", gridcolor="#162238", backgroundcolor="#040711"),
            aspectmode="data"
        )
    )
    st.plotly_chart(fig3d, width="stretch")
    st.caption("Shader Artemis: sombras frías en regiones PSR y crestas de luz en oro solar.")

with tabluz:
    figl = go.Figure([
        go.Heatmap(
            x=xs, y=ys, z=brillo, colorscale="gray", zmin=0, zmax=1, showscale=False,
            hovertemplate=(
                "<b>🛰️ Iluminación Rasante</b><br>"
                "Este: %{x:+.2f} km<br>"
                "Norte: %{y:+.2f} km<br>"
                "Factor Luz: <b>%{z:.1%}</b>"
                "<extra></extra>"
            )
        ),
        go.Scatter(
            x=[px], y=[py], mode="markers", name="HLS",
            marker=dict(size=13, color="#00f0ff", line=dict(width=2, color="white")),
            hovertemplate="<b>🎯 Posición HLS</b><br>Este: %{x:+.2f} km<br>Norte: %{y:+.2f} km<extra></extra>"
        ),
    ])
    figl.update_layout(
        **TEMA_TACTICO,
        height=520, margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(title="Distancia Este (km)", gridcolor="#162238"), 
        yaxis=dict(title="Distancia Norte (km)", gridcolor="#162238", scaleanchor="x")
    )
    st.plotly_chart(figl, width="stretch")

with tabpend:
    figp = go.Figure([
        go.Heatmap(
            x=xs, y=ys, z=pend_vis, colorscale="RdYlGn_r", zmin=0, zmax=30,
            colorbar=dict(title="Pendiente (°)", tickfont=dict(color="#00f0ff")),
            hovertemplate=(
                "<b>📐 Topografía Mecánica</b><br>"
                "Este: %{x:+.2f} km<br>"
                "Norte: %{y:+.2f} km<br>"
                "Inclinación: <b>%{z:.1f}°</b>"
                "<extra></extra>"
            )
        ),
        go.Scatter(
            x=[px], y=[py], mode="markers", name="HLS",
            marker=dict(size=13, color="white", line=dict(width=2, color="black")),
            hovertemplate="<b>🎯 Posición HLS</b><br>Este: %{x:+.2f} km<br>Norte: %{y:+.2f} km<extra></extra>"
        ),
    ])
    figp.update_layout(
        **TEMA_TACTICO,
        height=520, margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(title="Distancia Este (km)", gridcolor="#162238"), 
        yaxis=dict(title="Distancia Norte (km)", gridcolor="#162238", scaleanchor="x")
    )
    st.plotly_chart(figp, width="stretch")

with tabscore:
    fig_score = go.Figure([
        go.Heatmap(
            x=xs, y=ys, z=idoneidad_mapa, colorscale="Plasma", zmin=0, zmax=100,
            colorbar=dict(title="Score (%)", tickfont=dict(color="#00f0ff")),
            hovertemplate=(
                "<b>🎯 Matriz Táctica Artemis IV</b><br>"
                "Este: %{x:+.2f} km<br>"
                "Norte: %{y:+.2f} km<br>"
                "Idoneidad: <b>%{z:.1f}%</b>"
                "<extra></extra>"
            )
        ),
        # Marcadores visuales de las 5 mejores zonas seguras encontradas
        go.Scatter(
            x=top_xs, y=top_ys, mode="markers+text", name="Top 5 Sitios",
            text=[f"#{s['rank']}" for s in top5],
            textposition="top center",
            textfont=dict(family="Orbitron", color="#ffb81c", size=11),
            marker=dict(size=11, color="#ffb81c", symbol="star", line=dict(width=1, color="black")),
            hovertemplate="<b>⭐ Zona Segura %{text}</b><br>Este: %{x:+.2f} km<br>Norte: %{y:+.2f} km<extra></extra>"
        ),
        # Posición actual del módulo
        go.Scatter(
            x=[px], y=[py], mode="markers", name="Posición HLS",
            marker=dict(size=14, color="#00f0ff", symbol="diamond", line=dict(width=2, color="white")),
            hovertemplate="<b>🎯 Módulo Actual HLS</b><br>Este: %{x:+.2f} km<br>Norte: %{y:+.2f} km<extra></extra>"
        ),
    ])
    fig_score.update_layout(
        **TEMA_TACTICO,
        height=520, margin=dict(l=0, r=0, t=10, b=0),
        xaxis=dict(title="Distancia Este (km)", gridcolor="#162238"), 
        yaxis=dict(title="Distancia Norte (km)", gridcolor="#162238", scaleanchor="x")
    )
    st.plotly_chart(fig_score, width="stretch")
    st.caption("Matriz Multicriterio con estrellas doradas indicando los 5 mejores sitios candidatos libres de pendientes críticas.")

st.markdown("### 📡 TELEMETRÍA DETALLADA DEL PUNTO SELECCIONADO")
a, b, c, d = st.columns(4)

with a:
    st.markdown("#### ⛰️ COTA Y RELIEVE")
    st.metric("Elevación local", f"{altura:,.0f} m")
    if pendiente < LIMITE_OPTIMO:
        st.success(f"Pendiente {pendiente:.1f}° — **Óptimo**")
    elif pendiente <= LIMITE_PRECAUCION:
        st.warning(f"Pendiente {pendiente:.1f}° — **Precaución**")
    else:
        st.error(f"Pendiente {pendiente:.1f}° — **Peligro**")

with b:
    st.markdown("#### 🌍 ENLACE TIERRA (DTE)")
    st.metric("Elevación Tierra", f"{tierra_el:.1f}°")
    if tierra_ok:
        st.success("**Línea de visión NOMINAL**")
    else:
        st.error("**BLOQUEADO por relieve**")

with c:
    st.markdown("#### ☀️ FLUJO SOLAR")
    st.metric("Elevación Solar", f"{sol_el:.2f}°")
    if sol_ok:
        st.success("**Generación activa**")
    else:
        st.error("**En eclipse (batería)**")

with d:
    st.markdown("#### 🎯 SCORE ARTEMIS")
    st.metric("Índice Idoneidad", f"{score_actual:.1f}%")
    if score_actual >= 75:
        st.success("**Sitio Prioritario (Tier 1)**")
    elif score_actual >= 50:
        st.warning("**Sitio Marginal (Tier 2)**")
    else:
        st.error("**Sitio Descartado (No-Go)**")

# --- Horizonte con Sol y Tierra
st.markdown("### 🧭 PERFIL DE HORIZONTE RADIAL 360° (Mástil HLS 2m)")
figh = go.Figure([
    go.Scatter(x=np.arange(360), y=horiz, fill="tozeroy", name="Relieve Local",
               line=dict(color="#475569", width=2), fillcolor="rgba(30, 41, 59, 0.6)"),
    go.Scatter(x=[sol_az], y=[sol_el], mode="markers", name="Sol",
               marker=dict(size=18, color="#ffb81c", line=dict(width=2, color="#ffffff"))),
    go.Scatter(x=[tierra_az], y=[tierra_el], mode="markers", name="Tierra",
               marker=dict(size=18, color="#00f0ff", line=dict(width=2, color="#ffffff"))),
])
figh.update_layout(
    **TEMA_TACTICO,
    height=320, 
    margin=dict(l=0, r=0, t=10, b=0),
    xaxis=dict(title="Azimut Local (0° = Norte Selenográfico, 90° = Este)", range=[0, 360], dtick=45, gridcolor="#162238"),
    yaxis=dict(title="Ángulo Elevación (°)", range=[-8, max(horiz.max() + 2, 10)], gridcolor="#162238")
)
st.plotly_chart(figh, width="stretch")

# --- Línea de tiempo de 30 días con fases lunares
st.markdown("### 📅 VENTANA OPERATIVA (30 DÍAS)")
vis_sol = lunar.visible(ef["sol_el"], ef["sol_az"], horiz, radio=lunar.RADIO_SOL)
vis_tierra = lunar.visible(ef["tierra_el"], ef["tierra_az"], horiz)
vis = np.array([vis_sol, vis_tierra]).astype(int)

texto_estado = np.array([
    ["ILUMINADO (Generación OK)" if s else "EN SOMBRA (Solo batería)" for s in vis_sol],
    ["ENLACE DTE ACTIVO" if t else "BLOQUEADO POR RELIEVE" for t in vis_tierra]
])

dias = list(range(1, DIAS + 1))
etiquetas = [f"{lunar.icono_fase(f)}<br>{d}" for f, d in zip(ef["fase"], dias)]

figt = go.Figure(go.Heatmap(
    z=vis, 
    x=dias, 
    y=["☀️ Sol", "🌍 Tierra"],
    customdata=texto_estado,
    colorscale=[[0, "#991b1b"], [1, "#059669"]],
    showscale=False, 
    xgap=2, 
    ygap=2,
    hovertemplate=(
        "<b>📅 Día %{x} de Misión</b><br>"
        "Canal: %{y}<br>"
        "Telemetría: <b>%{customdata}</b>"
        "<extra></extra>"
    )
))

figt.add_vline(x=dia, line_dash="dot", line_color="#00f0ff", line_width=2)
figt.update_layout(
    **TEMA_TACTICO,
    height=230, 
    margin=dict(l=0, r=0, t=10, b=0),
    xaxis=dict(
        title="Día de misión relativo a T0 (Fases Lunares IAU)", 
        tickmode="array", 
        tickvals=dias, 
        ticktext=etiquetas, 
        side="bottom", 
        gridcolor="#162238"
    ),
    yaxis=dict(gridcolor="#162238")
)
st.plotly_chart(figt, width="stretch")

m1, m2, m3 = st.columns(3)
m1.metric("Ventana Solar Útil", f"{vis[0].mean():.0%}")
m2.metric("Ventana Enlace DTE", f"{vis[1].mean():.0%}")
m3.metric("Simultaneidad Operativa", f"{(vis[0] & vis[1]).mean():.0%}")
st.caption("Efemérides solares y terrestres resueltas para 12:00 UTC con núcleo de navegación JPL DE421.")