# ==============================================================================
# RUTA DEL FICHERO: lunar.py
# VERSIÓN: L-SEA v2.9 - WINDOW FINDER, EPS, DSN Y ASTRODINÁMICA JPL
# ==============================================================================

"""
Motor físico y astrodinámico de L-SEA:
- Trazado de rayos topográficos para horizonte 360°.
- Modelo de Potencia Eléctrica (EPS) con paneles GaAs.
- Red DSN con telemetría angular.
- Buscador vectorizado de ventanas de aterrizaje anuales (365 días) con perfiles Artemis/CLPS.
"""
from datetime import datetime, timezone, timedelta
from functools import lru_cache
from pathlib import Path

import numpy as np
from skyfield import almanac
from skyfield.api import Loader, wgs84

CARPETA_DATOS = Path(__file__).parent / "datos"
RADIO_SOL = 0.267
CONSTANTE_SOLAR = 1361.0


# =========================================================== TERRENO
def pendiente_grados(dem, metros_por_celda):
    dzdy, dzdx = np.gradient(dem, metros_por_celda)
    return np.degrees(np.arctan(np.hypot(dzdx, dzdy)))


def perfil_horizonte(dem, fila, col, metros_por_celda, altura_mastil=2.0):
    n_filas, n_cols = dem.shape
    z0 = dem[fila, col] + altura_mastil
    dist = np.arange(1, int(np.hypot(n_filas, n_cols)))
    az = np.radians(np.arange(360))[:, None]

    f = np.rint(fila + np.cos(az) * dist).astype(int)
    c = np.rint(col + np.sin(az) * dist).astype(int)
    dentro = (f >= 0) & (f < n_filas) & (c >= 0) & (c < n_cols)
    f, c = np.clip(f, 0, n_filas - 1), np.clip(c, 0, n_cols - 1)

    angulo = np.degrees(np.arctan2(dem[f, c] - z0, dist * metros_por_celda))
    angulo = np.where(dentro, angulo, -90.0)
    return np.maximum(angulo.max(axis=1), 0.0)


# =========================================================== ILUMINACIÓN Y OCLUSIÓN
def sombreado(dem, metros_por_celda, sol_az, sol_el, ambiente=0.06):
    if sol_el <= 0:
        return np.full(dem.shape, ambiente, dtype=np.float32)
    dzdy, dzdx = np.gradient(dem, metros_por_celda)
    az, el = np.radians(sol_az), np.radians(sol_el)
    s = np.array([np.sin(az) * np.cos(el), np.cos(az) * np.cos(el), np.sin(el)])
    luz = (-dzdx * s[0] - dzdy * s[1] + s[2]) / np.sqrt(1 + dzdx**2 + dzdy**2)
    luz = np.clip(luz, 0, 1)
    return ambiente + (1 - ambiente) * (1 - np.exp(-25 * luz))


def sombras_proyectadas(dem, metros_por_celda, azimut, elevacion, stride=2):
    if elevacion <= 0:
        return np.ones(dem.shape, dtype=bool)
    
    n_f, n_c = dem.shape
    ii, jj = np.mgrid[0:n_f, 0:n_c]
    dy, dx = np.cos(np.radians(azimut)), np.sin(np.radians(azimut))
    tan_el = np.tan(np.radians(elevacion))
    bloqueado = np.zeros(dem.shape, dtype=bool)
    
    limite = max(n_f, n_c)
    for k in range(1, limite, stride):
        f = np.rint(ii + dy * k).astype(int)
        c = np.rint(jj + dx * k).astype(int)
        dentro = (f >= 0) & (f < n_f) & (c >= 0) & (c < n_c)
        if not dentro.any():
            break
        tapa = (dem[np.clip(f, 0, n_f - 1), np.clip(c, 0, n_c - 1)] - dem) / (k * metros_por_celda)
        bloqueado |= dentro & (tapa > tan_el)
        
    return bloqueado


# =========================================================== MODELO EPS
def calcular_potencia_electrica(sol_visible, sol_el, area_m2=2.0, eficiencia=0.29, carga_base_w=100.0):
    if not sol_visible or sol_el <= 0:
        return 0.0, -carga_base_w, 0.0
    angulo_incidencia = np.cos(np.radians(sol_el))
    potencia_bruta = CONSTANTE_SOLAR * area_m2 * eficiencia * angulo_incidencia
    potencia_neta = potencia_bruta - carga_base_w
    return round(potencia_bruta, 0), round(potencia_neta, 0), CONSTANTE_SOLAR


# ========================================== ASTRODINÁMICA (JPL DE421)
@lru_cache(maxsize=1)
def _skyfield():
    cargador = Loader(str(CARPETA_DATOS), verbose=False)
    return cargador.timescale(), cargador("de421.bsp")


def _R1(a):
    c, s, o, z = np.cos(a), np.sin(a), np.ones_like(a), np.zeros_like(a)
    return np.stack([np.stack([o, z, z], -1), np.stack([z, c, s], -1), np.stack([z, -s, c], -1)], -2)


def _R3(a):
    c, s, o, z = np.cos(a), np.sin(a), np.ones_like(a), np.zeros_like(a)
    return np.stack([np.stack([c, s, z], -1), np.stack([-s, c, z], -1), np.stack([z, z, o], -1)], -2)


def _matriz_icrf_a_luna(d):
    T = d / 36525.0
    E = np.radians(np.array([
        125.045 - 0.0529921 * d, 250.089 - 0.1059842 * d, 260.008 + 13.0120009 * d,
        176.625 + 13.3407154 * d, 357.529 + 0.9856003 * d, 311.589 + 26.4057084 * d,
        134.963 + 13.0649930 * d, 276.617 + 0.3287146 * d, 34.226 + 1.7484877 * d,
        15.134 - 0.1589763 * d, 119.743 + 0.0036096 * d, 239.961 + 0.1643573 * d,
        25.053 + 12.9590088 * d]))
    s, c = np.sin(E), np.cos(E)
    ra = (269.9949 + 0.0031 * T - 3.8787 * s[0] - 0.1204 * s[1] + 0.0700 * s[2]
          - 0.0172 * s[3] + 0.0072 * s[5] - 0.0052 * s[9] + 0.0043 * s[12])
    dec = (66.5392 + 0.0130 * T + 1.5419 * c[0] + 0.0239 * c[1] - 0.0278 * c[2]
           + 0.0068 * c[3] - 0.0029 * c[5] + 0.0009 * c[6] + 0.0008 * c[9] - 0.0009 * c[12])
    W = (38.3213 + 13.17635815 * d - 1.4e-12 * d**2 + 3.5610 * s[0] + 0.1208 * s[1]
         - 0.0642 * s[2] + 0.0158 * s[3] + 0.0252 * s[4] - 0.0066 * s[5] - 0.0047 * s[6]
         - 0.0046 * s[7] + 0.0028 * s[8] + 0.0052 * s[9] + 0.0040 * s[10]
         + 0.019 * s[11] - 0.0044 * s[12])
    ra, dec, W = np.radians(ra), np.radians(dec), np.radians(W)
    return _R3(W) @ _R1(np.pi / 2 - dec) @ _R3(ra + np.pi / 2)


def _base_local(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    este = np.array([-np.sin(lo), np.cos(lo), 0.0])
    norte = np.array([-np.sin(la) * np.cos(lo), -np.sin(la) * np.sin(lo), np.cos(la)])
    arriba = np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
    return este, norte, arriba


def efemerides(fechas, lat, lon, rumbo=0.0):
    ts, eph = _skyfield()
    t = ts.from_datetimes([f.replace(tzinfo=timezone.utc) for f in fechas])
    R = _matriz_icrf_a_luna(np.atleast_1d(t.tdb - 2451545.0))
    este, norte, arriba = _base_local(lat, lon)

    def en_el_cielo(cuerpo):
        v_icrf = (eph[cuerpo] - eph["moon"]).at(t).position.km.reshape(3, -1).T
        v = np.einsum("nij,nj->ni", R, v_icrf)
        el = np.degrees(np.arcsin((v @ arriba) / np.linalg.norm(v, axis=1)))
        az = np.degrees(np.arctan2(v @ este, v @ norte))
        return (az - rumbo) % 360, el

    sol_az, sol_el = en_el_cielo("sun")
    tierra_az, tierra_el = en_el_cielo("earth")
    fase = np.atleast_1d(almanac.moon_phase(eph, t).degrees)
    return dict(sol_az=sol_az, sol_el=sol_el, tierra_az=tierra_az, tierra_el=tierra_el, fase=fase)


def visible(elevacion, azimut, horizonte, radio=0.0):
    idx = np.rint(azimut).astype(int) % 360
    return (np.asarray(elevacion) + radio) > horizonte[idx]


def icono_fase(grados):
    return "🌑🌒🌓🌔🌕🌖🌗🌘"[int((grados + 22.5) // 45) % 8]


# =========================================================== EVALUACIÓN MULTIDÍA
def evaluar_mision_multidia(dem, mpc, fechas_mision, lat, lon, rumbo, ponderacion_comms=0.50, max_pendiente=10.0):
    ef = efemerides(fechas_mision, lat, lon, rumbo)
    n_dias = len(fechas_mision)
    
    acum_sol = np.zeros(dem.shape, dtype=np.float32)
    acum_dte = np.zeros(dem.shape, dtype=np.float32)
    
    for k in range(n_dias):
        s_az, s_el = float(ef["sol_az"][k]), float(ef["sol_el"][k])
        t_az, t_el = float(ef["tierra_az"][k]), float(ef["tierra_el"][k])
        
        if s_el > 0:
            s_sombra = sombras_proyectadas(dem, mpc, s_az, s_el, stride=3)
            s_luz = sombreado(dem, mpc, s_az, s_el)
            acum_sol += np.where(s_sombra, 0.02, s_luz)
            
        if t_el > 0:
            t_sombra = sombras_proyectadas(dem, mpc, t_az, t_el, stride=3)
            acum_dte += np.where(t_sombra, 0.0, 1.0)
            
    pct_sol = (acum_sol / n_dias) * 100.0
    pct_dte = (acum_dte / n_dias) * 100.0
    
    dzdy, dzdx = np.gradient(dem, mpc)
    pend = np.degrees(np.arctan(np.hypot(dzdx, dzdy)))
    factor_seguridad = np.clip(1.0 - (pend / max_pendiente), 0.0, 1.0) ** 2
    
    peso_seguridad = 0.40
    peso_variable = 0.60
    peso_comms = peso_variable * ponderacion_comms
    peso_sol = peso_variable * (1.0 - ponderacion_comms)
    
    score = (
        peso_seguridad * (factor_seguridad * 100.0) +
        peso_sol * np.clip(pct_sol, 0.0, 100.0) +
        peso_comms * np.clip(pct_dte, 0.0, 100.0)
    )
    return np.round(score, 1), np.round(pct_sol, 1), np.round(pct_dte, 1)


def top_sitios_aterrizaje(idoneidad, pendientes, dem, max_pend=10.0, n_sitios=5, radio_exclusion_px=12, deadzone_borde_pct=0.08):
    filas, cols = idoneidad.shape
    
    pad = np.pad(idoneidad, 1, mode='edge')
    vecindad = (
        pad[:-2, :-2] + pad[:-2, 1:-1] + pad[:-2, 2:] +
        pad[1:-1, :-2] + pad[1:-1, 1:-1] + pad[1:-1, 2:] +
        pad[2:, :-2] + pad[2:, 1:-1] + pad[2:, 2:]
    ) / 9.0
    
    mar_f = int(filas * deadzone_borde_pct)
    mar_c = int(cols * deadzone_borde_pct)
    
    mascara_activa = np.zeros((filas, cols), dtype=bool)
    mascara_activa[mar_f:filas - mar_f, mar_c:cols - mar_c] = True
    mascara_activa &= (pendientes <= max_pend)
    
    puntuacion_filtrada = np.where(mascara_activa, vecindad, -1.0)
    sitios = []
    copia_score = puntuacion_filtrada.copy()
    
    for rank in range(1, n_sitios + 1):
        idx_max = np.argmax(copia_score)
        f_max, c_max = np.unravel_index(idx_max, copia_score.shape)
        score_val = float(copia_score[f_max, c_max])
        
        if score_val <= 0:
            break
            
        sitios.append({
            "rank": rank,
            "fila": int(f_max),
            "col": int(c_max),
            "score": round(score_val, 1),
            "pendiente": round(float(pendientes[f_max, c_max]), 1),
            "altura": round(float(dem[f_max, c_max]), 0)
        })
        
        y_grid, x_grid = np.ogrid[:filas, :cols]
        dist_sq = (y_grid - f_max)**2 + (x_grid - c_max)**2
        copia_score[dist_sq <= radio_exclusion_px**2] = -1.0
        
    return sitios


# =========================================================== TRACKING DSN
DSN_ESTACIONES = {
    "Madrid (CDSCC)": (40.427, -4.249),
    "Goldstone (GDSCC)": (35.426, -116.890),
    "Canberra (CDSCC)": (-35.401, 148.981),
}

def telemetria_dsn(fecha_utc):
    ts, eph = _skyfield()
    t = ts.from_datetime(fecha_utc.replace(tzinfo=timezone.utc))
    tierra = eph["earth"]
    luna = eph["moon"]
    
    resultado = {}
    for nombre, (lat, lon) in DSN_ESTACIONES.items():
        estacion = tierra + wgs84.latlon(lat, lon)
        astro = estacion.at(t).observe(luna).apparent()
        alt, _, _ = astro.altaz()
        resultado[nombre] = round(alt.degrees, 1)
    return resultado


# =========================================================== BUSCADOR DE VENTANAS (WINDOW FINDER)
def buscar_ventanas_anuales(dem, fila, col, mpc, lat, lon, rumbo, fecha_inicio, dias_busqueda=365,
                            duracion_estancia=7, min_sol_pct=80.0, min_dte_pct=50.0, mastil=2.0):
    """
    Algoritmo Sliding Window (365 días):
    Evalúa cada posible día de lanzamiento T0 contra la duración completa de estancia.
    Devuelve la máscara anual de viabilidad (0 o 1) y la lista de oportunidades óptimas.
    """
    horiz = perfil_horizonte(dem, fila, col, mpc, altura_mastil=mastil)
    fechas_anuales = [fecha_inicio + timedelta(days=i) for i in range(dias_busqueda)]
    ef = efemerides(fechas_anuales, lat, lon, rumbo)
    
    vis_sol = visible(ef["sol_el"], ef["sol_az"], horiz, radio=RADIO_SOL)
    vis_tierra = visible(ef["tierra_el"], ef["tierra_az"], horiz)
    
    mascara_anual = np.zeros(dias_busqueda, dtype=int)
    oportunidades = []
    
    limite = dias_busqueda - duracion_estancia
    for d in range(limite):
        sol_ventana = vis_sol[d:d + duracion_estancia]
        dte_ventana = vis_tierra[d:d + duracion_estancia]
        
        pct_sol = float(sol_ventana.mean() * 100.0)
        pct_dte = float(dte_ventana.mean() * 100.0)
        
        # Criterio de Touchdown: aterrizar obligatoriamente con sol y enlace directo
        condicion_touchdown = sol_ventana[0] and dte_ventana[0]
        
        if condicion_touchdown and pct_sol >= min_sol_pct and pct_dte >= min_dte_pct:
            mascara_anual[d] = 1
            score = round(0.6 * pct_sol + 0.4 * pct_dte, 1)
            oportunidades.append({
                "t0": fechas_anuales[d].strftime("%Y-%m-%d"),
                "cierre": fechas_anuales[d + duracion_estancia].strftime("%Y-%m-%d"),
                "sol_pct": round(pct_sol, 1),
                "dte_pct": round(pct_dte, 1),
                "score": score
            })
            
    # Agrupar días consecutivos en ventanas consolidadas
    ventanas_agrupadas = []
    if oportunidades:
        ventana_actual = dict(oportunidades[0])
        dias_consecutivos = 1
        mejor_score = ventana_actual["score"]
        mejor_t0 = ventana_actual["t0"]
        
        for op in oportunidades[1:]:
            d_ant = datetime.strptime(ventana_actual["t0"], "%Y-%m-%d")
            d_sig = datetime.strptime(op["t0"], "%Y-%m-%d")
            
            if (d_sig - d_ant).days == dias_consecutivos:
                dias_consecutivos += 1
                ventana_actual["cierre"] = op["cierre"]
                if op["score"] > mejor_score:
                    mejor_score = op["score"]
                    mejor_t0 = op["t0"]
            else:
                ventana_actual["dias_viables"] = dias_consecutivos
                ventana_actual["mejor_t0"] = mejor_t0
                ventana_actual["score"] = mejor_score
                ventanas_agrupadas.append(ventana_actual)
                
                ventana_actual = dict(op)
                dias_consecutivos = 1
                mejor_score = ventana_actual["score"]
                mejor_t0 = ventana_actual["t0"]
                
        ventana_actual["dias_viables"] = dias_consecutivos
        ventana_actual["mejor_t0"] = mejor_t0
        ventana_actual["score"] = mejor_score
        ventanas_agrupadas.append(ventana_actual)
        
    return mascara_anual, fechas_anuales, ventanas_agrupadas