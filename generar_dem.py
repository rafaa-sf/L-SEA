"""
Genera mapas de elevación SINTÉTICOS pero con ESCALA REAL (alturas en metros).
Ejecuta una vez:  python generar_dem.py
Crea en la carpeta mapas/ un par de archivos por sitio:
  <sitio>.npy  -> matriz de alturas en metros (rápido de cargar, a diferencia del CSV)
  <sitio>.json -> metadatos: km del mapa, metros por celda, lat, lon y rumbo

Los mapas reales de LOLA se preparan con preparar_lola.py y generan EXACTAMENTE
el mismo formato, así que app.py no distingue entre sintético y real.
"""
import json
from pathlib import Path

import numpy as np

N = 200   # celdas por lado
KM = 30   # kilómetros por lado -> ~150 m por celda


def malla():
    x = np.linspace(-KM / 2, KM / 2, N)
    return np.meshgrid(x, x)  # X, Y en km


def relieve_suave(rng, amplitud_m, n_ondas=14):
    """Suma de ondas senoidales de baja frecuencia = relieve ondulado natural."""
    X, Y = malla()
    z = np.zeros_like(X)
    for _ in range(n_ondas):
        k = rng.uniform(0.15, 1.2)                 # ondas por km
        ang = rng.uniform(0, 2 * np.pi)
        fase = rng.uniform(0, 2 * np.pi)
        z += rng.uniform(0.3, 1.0) * np.sin(2 * np.pi * k * (X * np.cos(ang) + Y * np.sin(ang)) + fase)
    return amplitud_m * z / z.std()


def shackleton(rng):
    X, Y = malla()
    r = np.hypot(X - 1, Y + 1)                      # centro algo desplazado
    R, D = 10.5, 4200                               # radio (km) y profundidad (m)
    cuenco = -D * np.clip(1 - (r / R) ** 2, 0, None) ** 0.6
    borde = 450 * np.exp(-((r - R) / 1.8) ** 2)     # el reborde elevado
    return cuenco + borde + relieve_suave(rng, 80)


def malapert(rng):
    X, Y = malla()
    macizo = 5000 * np.exp(-(np.hypot(X + 3, Y - 2) / 6) ** 2)           # la montaña
    crater = -600 * np.exp(-(np.hypot(X - 8, Y + 7) / 2.5) ** 2)         # cráter pequeño
    return macizo + crater + relieve_suave(rng, 120)


SITIOS = [
    # nombre, función, latitud, longitud (centro del mapa; solo afectan a Sol/Tierra)
    ("shackleton", shackleton, -89.9, 129.8),
    ("malapert", malapert, -86.0, 0.1),
]

if __name__ == "__main__":
    carpeta = Path(__file__).parent / "mapas"
    carpeta.mkdir(exist_ok=True)
    rng = np.random.default_rng(42)
    for nombre, f, lat, lon in SITIOS:
        z = f(rng).astype("float32")
        np.save(carpeta / f"{nombre}.npy", z)
        meta = dict(km=KM, mpc=KM * 1000 / (N - 1), lat=lat, lon=lon, rumbo=0.0, fuente="sintético")
        (carpeta / f"{nombre}.json").write_text(json.dumps(meta, indent=2))
        print(nombre, z.shape, f"{z.min():.0f} a {z.max():.0f} m")
