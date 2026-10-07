# ==============================================================================
# RUTA DEL FICHERO: lunar.py
# FUNCIÓN: Motor físico, topografía, trazado de rayos y astrodinámica IAU/JPL
# ==============================================================================

"""
Toda la 'física' de la app vive aquí, separada de la interfaz (app.py).

Convención de ejes del MAPA: filas = eje Y (Norte = filas crecientes),
columnas = eje X (Este = columnas crecientes). Azimut: 0° = arriba del mapa,
90° = derecha. Si el mapa NO está orientado al norte local, el parámetro
`rumbo` corrige la diferencia (preparar_lola.py lo calcula solo).
"""
from datetime import timezone
from functools import lru_cache
from pathlib import Path

import numpy as np
from skyfield import almanac
from skyfield.api import Loader

CARPETA_DATOS = Path(__file__).parent / "datos"
RADIO_SOL = 0.267   # radio angular del Sol (°): "visible" = el borde superior asoma


# =========================================================== TERRENO
def pendiente_grados(dem, metros_por_celda):
    """Pendiente REAL en grados: arctan(dz/dx), usando la escala del mapa."""
    dzdy, dzdx = np.gradient(dem, metros_por_celda)
    return np.degrees(np.arctan(np.hypot(dzdx, dzdy)))


def perfil_horizonte(dem, fila, col, metros_por_celda, altura_mastil=2.0):
    """
    Para cada azimut (0..359°) devuelve la elevación del horizonte (grados)
    visto desde el módulo: sigue ese rayo y se queda con el mayor ángulo con
    el que el terreno 'tapa' el cielo.
    """
    n_filas, n_cols = dem.shape
    z0 = dem[fila, col] + altura_mastil
    dist = np.arange(1, int(np.hypot(n_filas, n_cols)))        # distancias en celdas
    az = np.radians(np.arange(360))[:, None]                   # (360, 1)

    f = np.rint(fila + np.cos(az) * dist).astype(int)          # (360, n_dist)
    c = np.rint(col + np.sin(az) * dist).astype(int)
    dentro = (f >= 0) & (f < n_filas) & (c >= 0) & (c < n_cols)
    f, c = np.clip(f, 0, n_filas - 1), np.clip(c, 0, n_cols - 1)

    angulo = np.degrees(np.arctan2(dem[f, c] - z0, dist * metros_por_celda))
    angulo = np.where(dentro, angulo, -90.0)                   # fuera del mapa: ignorar
    return np.maximum(angulo.max(axis=1), 0.0)                 # suelo llano = 0°


# =========================================================== ILUMINACIÓN
def sombreado(dem, metros_por_celda, sol_az, sol_el, ambiente=0.06):
    """
    Hillshade: cuánta luz recibe cada celda según hacia dónde mira su pendiente.
    Devuelve valores 0..1. Con el Sol tan bajo (~1°) el suelo llano recibe muy
    poca luz, así que se aplica una curva de exposición para que se vea bien.
    """
    if sol_el <= 0:
        return np.full(dem.shape, ambiente)
    dzdy, dzdx = np.gradient(dem, metros_por_celda)
    az, el = np.radians(sol_az), np.radians(sol_el)
    s = np.array([np.sin(az) * np.cos(el), np.cos(az) * np.cos(el), np.sin(el)])
    luz = (-dzdx * s[0] - dzdy * s[1] + s[2]) / np.sqrt(1 + dzdx**2 + dzdy**2)
    luz = np.clip(luz, 0, 1)
    return ambiente + (1 - ambiente) * (1 - np.exp(-25 * luz))


def sombras_proyectadas(dem, metros_por_celda, sol_az, sol_el, stride=2):
    """
    True donde una montaña tapa al Sol (sombra proyectada).
    Acelerado con stride dinámico para cálculo a 60 FPS.
    """
    if sol_el <= 0:
        return np.ones(dem.shape, dtype=bool)           # De noche todo es sombra
    
    n_f, n_c = dem.shape
    ii, jj = np.mgrid[0:n_f, 0:n_c]
    dy, dx = np.cos(np.radians(sol_az)), np.sin(np.radians(sol_az))
    tan_sol = np.tan(np.radians(sol_el))
    sombra = np.zeros(dem.shape, dtype=bool)
    
    limite = max(n_f, n_c)
    for k in range(1, limite, stride):
        f = np.rint(ii + dy * k).astype(int)
        c = np.rint(jj + dx * k).astype(int)
        dentro = (f >= 0) & (f < n_f) & (c >= 0) & (c < n_c)
        if not dentro.any():
            break
        tapa = (dem[np.clip(f, 0, n_f - 1), np.clip(c, 0, n_c - 1)] - dem) / (k * metros_por_celda)
        sombra |= dentro & (tapa > tan_sol)
        
    return sombra


# ========================================== SOL, TIERRA Y FASES (EFEMÉRIDES)
@lru_cache(maxsize=1)
def _skyfield():
    """Carga una sola vez la escala de tiempos y las efemérides JPL DE421."""
    cargador = Loader(str(CARPETA_DATOS), verbose=False)   # si falta de421.bsp lo descarga
    return cargador.timescale(), cargador("de421.bsp")


def _R1(a):
    c, s, o, z = np.cos(a), np.sin(a), np.ones_like(a), np.zeros_like(a)
    return np.stack([np.stack([o, z, z], -1), np.stack([z, c, s], -1), np.stack([z, -s, c], -1)], -2)


def _R3(a):
    c, s, o, z = np.cos(a), np.sin(a), np.ones_like(a), np.zeros_like(a)
    return np.stack([np.stack([c, s, z], -1), np.stack([-s, c, z], -1), np.stack([z, z, o], -1)], -2)


def _matriz_icrf_a_luna(d):
    """
    Matriz que pasa un vector del cielo (ICRF) a ejes fijos a la Luna.
    Usa el modelo de rotación de la Luna de la IAU (Archinal et al.), que ya
    incluye la libración; error ≲ 0,05° respecto a las efemérides de la NASA.
    d = días desde J2000 (TDB).
    """
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
    """Vectores Este, Norte y Arriba del punto (lat, lon) en ejes fijos a la Luna."""
    la, lo = np.radians(lat), np.radians(lon)
    este = np.array([-np.sin(lo), np.cos(lo), 0.0])
    norte = np.array([-np.sin(la) * np.cos(lo), -np.sin(la) * np.sin(lo), np.cos(la)])
    arriba = np.array([np.cos(la) * np.cos(lo), np.cos(la) * np.sin(lo), np.sin(la)])
    return este, norte, arriba


def efemerides(fechas, lat, lon, rumbo=0.0):
    """Posición REAL del Sol y la Tierra según efemérides JPL DE421."""
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
    """¿Asoma el astro por encima del horizonte del terreno?"""
    idx = np.rint(azimut).astype(int) % 360
    return (np.asarray(elevacion) + radio) > horizonte[idx]


def icono_fase(grados):
    """Emoji de la fase lunar (0=nueva ... 180=llena)."""
    return "🌑🌒🌓🌔🌕🌖🌗🌘"[int((grados + 22.5) // 45) % 8]


def mapa_idoneidad(pendientes, exposicion_luz, max_pendiente=10.0):
    """
    Índice de idoneidad multicriterio para aterrizaje lunar (0% a 100%).
    Combina:
      1. Seguridad topográfica: penalización cuadrática por exceso de pendiente.
      2. Factor energético: pondera positivamente las zonas con mayor captación solar.
    """
    factor_seguridad = np.clip(1.0 - (pendientes / max_pendiente), 0.0, 1.0) ** 2
    factor_luz = np.clip(exposicion_luz, 0.0, 1.0)
    
    score = (0.60 * factor_seguridad + 0.40 * factor_luz) * 100.0
    return np.round(score, 1)

def top_sitios_aterrizaje(idoneidad, pendientes, dem, max_pend=10.0, n_sitios=5, radio_exclusion_px=12, deadzone_borde_pct=0.08):
    """
    Algoritmo Autopilot Artemis IV:
    1. Deadzone: Elimina los bordes del mapa para evitar artefactos del recorte.
    2. Filtro Anti-Glitch (Meseta 3x3): Promedia la idoneidad con sus vecinos inmediatos.
       Si un píxel es plano pero está al borde de un abismo, su nota se desploma.
    3. Supresión No Máxima: Encuentra los N mejores puntos asegurando que estén 
       separados físicamente al menos 'radio_exclusion_px' celdas entre sí.
    """
    filas, cols = idoneidad.shape
    
    # 1. Filtro espacial de área (convolución 3x3 pura en NumPy, sin dependencias extra)
    pad = np.pad(idoneidad, 1, mode='edge')
    vecindad = (
        pad[:-2, :-2] + pad[:-2, 1:-1] + pad[:-2, 2:] +
        pad[1:-1, :-2] + pad[1:-1, 1:-1] + pad[1:-1, 2:] +
        pad[2:, :-2] + pad[2:, 1:-1] + pad[2:, 2:]
    ) / 9.0
    
    # 2. Deadzone de borde (máscara de exclusión de seguridad perimetral)
    mar_f = int(filas * deadzone_borde_pct)
    mar_c = int(cols * deadzone_borde_pct)
    
    mascara_activa = np.zeros((filas, cols), dtype=bool)
    mascara_activa[mar_f:filas - mar_f, mar_c:cols - mar_c] = True
    
    # Descartar cualquier zona cuya pendiente supere el límite crítico
    mascara_activa &= (pendientes <= max_pend)
    
    puntuacion_filtrada = np.where(mascara_activa, vecindad, -1.0)
    
    # 3. Supresión No Máxima para encontrar Top N sitios dispersos
    sitios = []
    copia_score = puntuacion_filtrada.copy()
    
    for rank in range(1, n_sitios + 1):
        idx_max = np.argmax(copia_score)
        f_max, c_max = np.unravel_index(idx_max, copia_score.shape)
        score_val = float(copia_score[f_max, c_max])
        
        if score_val <= 0:
            break  # No quedan más zonas seguras
            
        sitios.append({
            "rank": rank,
            "fila": int(f_max),
            "col": int(c_max),
            "score": round(score_val, 1),
            "pendiente": round(float(pendientes[f_max, c_max]), 1),
            "altura": round(float(dem[f_max, c_max]), 0)
        })
        
        # Máscara circular de exclusión para no repetir la misma colina
        y_grid, x_grid = np.ogrid[:filas, :cols]
        dist_sq = (y_grid - f_max)**2 + (x_grid - c_max)**2
        copia_score[dist_sq <= radio_exclusion_px**2] = -1.0
        
    return sitios