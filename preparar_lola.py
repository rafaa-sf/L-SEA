"""
Recorta un mapa LOLA (GeoTIFF del polo sur) y lo guarda listo para la app.

Uso (ejemplo):
  python preparar_lola.py LDEM_80S_20MPP_ADJ.TIF --nombre shackleton --lat -89.9 --lon 129.8 --km 30

Genera mapas/<nombre>.npy y mapas/<nombre>.json (mismo formato que generar_dem.py).
Calcula SOLO el 'rumbo' (cuánto está girado el mapa respecto al norte local),
así que no hay que pensar en proyecciones.

Opciones útiles:
  --paso 2   reduce la resolución a la mitad (mapas más ligeros)
"""
import argparse
import json
from pathlib import Path

import numpy as np
import rasterio
from rasterio.warp import transform
from rasterio.windows import Window

R_LUNA = 1737400.0
GEO_LUNA = f"+proj=longlat +R={R_LUNA} +no_defs"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("tif")
    p.add_argument("--nombre", required=True)
    p.add_argument("--lat", type=float, required=True, help="latitud del centro (negativa en el sur)")
    p.add_argument("--lon", type=float, required=True, help="longitud Este del centro, 0..360 o -180..180")
    p.add_argument("--km", type=float, default=30, help="lado del recorte en km")
    p.add_argument("--paso", type=int, default=1, help="1 = resolución original, 2 = mitad...")
    a = p.parse_args()

    with rasterio.open(a.tif) as ds:
        # 1) centro del recorte en coordenadas del mapa (metros)
        (x,), (y,) = transform(GEO_LUNA, ds.crs, [a.lon], [a.lat])
        # 2) hacia dónde cae el NORTE LOCAL en el mapa -> rumbo
        (x2,), (y2,) = transform(GEO_LUNA, ds.crs, [a.lon], [a.lat + 0.05])
        giro_norte = np.degrees(np.arctan2(x2 - x, y2 - y))   # grados horarios desde "arriba"
        rumbo = float(-giro_norte)

        # 3) recorte cuadrado alrededor del centro
        res = abs(ds.res[0])                                   # metros por píxel
        n = int(round(a.km * 1000 / res))
        fila, col = ds.index(x, y)
        ventana = Window(col - n // 2, fila - n // 2, n, n)
        dem = ds.read(1, window=ventana, boundless=True, fill_value=np.nan).astype("float64")
        if ds.scales[0] != 1 or ds.offsets[0] != 0:
            dem = dem * ds.scales[0] + ds.offsets[0]

    dem = dem[::-1, :]                       # fila 0 = sur, última = norte (convención de la app)
    dem = dem[::a.paso, ::a.paso]
    huecos = np.isnan(dem)
    if huecos.any():
        print(f"Aviso: {huecos.mean():.1%} de celdas sin datos (fuera del mapa); se rellenan con la media")
        dem[huecos] = np.nanmean(dem)

    carpeta = Path(__file__).parent / "mapas"
    carpeta.mkdir(exist_ok=True)
    np.save(carpeta / f"{a.nombre}.npy", dem.astype("float32"))
    meta = dict(km=a.km, mpc=a.km * 1000 / (dem.shape[1] - 1),
                lat=a.lat, lon=a.lon, rumbo=round(rumbo, 3), fuente=Path(a.tif).name)
    (carpeta / f"{a.nombre}.json").write_text(json.dumps(meta, indent=2))
    print(f"{a.nombre}: {dem.shape}, {meta['mpc']:.1f} m/celda, rumbo {rumbo:.1f}°, alturas {dem.min():.0f}..{dem.max():.0f} m")


if __name__ == "__main__":
    main()
