# Historial del proyecto y mejoras a incluir

CLPS Lunar Mission Browser · NASA Space Apps Challenge Málaga 2026
Actualizado el **7 de octubre de 2026** (evento: en ~1 mes). Sustituye al backup del 5 de octubre.

> **Nota sobre los nombres EVO:** las únicas etiquetas confirmadas son **EVO 2.2** (Shackleton con LOLA real) y **EVO 2.6** (la que lleva ahora `app.py`). Las demás están ordenadas como propuesta a partir del código; cámbialas si usabas otra numeración, sobre todo **2.3 a 2.5**, de las que no hay registro.

---

## 1. Versiones

| Versión | Qué incluye |
|---|---|
| **EVO 1.0** _(propuesta)_ | App original hecha con Gemini: un CSV aleatorio de 100×100, selector de sitio que no cambiaba los datos, pendiente con un factor arbitrario (×15), visibilidad de Sol/Tierra decidida solo por la altura y el día |
| **EVO 2.0** _(propuesta)_ | Esqueleto reestructurado en `app.py` + `lunar.py` + `generar_dem.py`; escala real en km; pendiente con `arctan`; horizonte por trazado de rayos (360°); línea de tiempo de 30 días; mapa de pendientes; 3D con proporciones reales |
| **EVO 2.1** _(propuesta)_ | Fin del CSV (ahora `.npy` + `.json`); efemérides reales con Skyfield + DE421; rotación lunar IAU; hillshade y sombras proyectadas; fases lunares; pestaña de iluminación; `preparar_lola.py` |
| **EVO 2.2** | **Shackleton con datos reales de LOLA** (`LDEM_80S_40MPP_ADJ`): 750×750 celdas, 40,1 m/celda, alturas de −2.872 a +1.959 m, rumbo −129,8° |
| **EVO 2.3–2.5** _(propuesta, sin confirmar)_ | Pasos intermedios hasta 2.6. Por el código, aquí caen: interfaz «cockpit» (tema oscuro, fuentes Orbitron/JetBrains Mono, métricas con estilo HUD, etiquetas GO/NO-GO), paleta de regolito en 3D, pestañas 3D / luz / pendientes / score, telemetría por bloques (cota, enlace Tierra, flujo solar, score) y botón de ajuste manual del punto |
| **EVO 2.6** | **Artemis IV Autopilot & Tactical Site Ranker:** `mapa_idoneidad` (60 % seguridad por pendiente + 40 % exposición solar) y `top_sitios_aterrizaje` (zona muerta del 8 %, filtro anti-glitch 3×3, supresión de no máximos, Top 5). Barra lateral con «Fijar mejor sitio (#1)», alternativas Top 5 y navegación a coordenada. Licencia **MIT** añadida y README bilingüe EN/ES |

## 2. Cronología de decisiones

1. **¿Cuántos km por mapa?** Se decidió pensar en metros por celda, no solo en km. Propuesta: mapa regional de **30 km** (cabe Shackleton, ~21 km de diámetro, y Malapert) y, si da tiempo, un **zoom de ~2 km a ~10 m/px** para evaluar pendientes de aterrizaje.
2. **Fallos detectados en el código original:** el selector de sitio era decorativo; la pendiente no usaba escala; Sol y Tierra no dependían del horizonte real del terreno; X/Y en píxeles y Z en metros deformaban el 3D.
3. **Brainstorm de preparación** (`NASA.txt`): afinar y conocer el esqueleto de memoria, hacerlo más visual, simulacro con LOLA, límites del PC, predecir fases lunares a un mes, texturas, lista de herramientas, funciones del equipo, documento profesional, GitHub abierto, presentación con guion.
4. **Decisiones del 5 de octubre:** dejar el CSV, ir a LOLA (si el PC no aguanta, menos distancia), usar Skyfield en vez de la función simplificada, añadir hillshade, esqueleto lo más listo posible para el pitch.
5. **Aclaración clave:** predecir Sol, Tierra y fases a un mes vista **sí es posible y es determinista** (mecánica celeste), a diferencia del tiempo meteorológico.
6. **Límites de rendimiento (medidos):** un mapa de 1.500×1.500 se carga y calcula con fluidez; el 3D se dibuja reducido a ≤ 250×250.

7. **7 de octubre:** la app queda casi lista para lanzar; se decide ir más allá del visor y añadir un **buscador automático del mejor sitio** (el Autopilot de EVO 2.6). El repo original se borra de la cuenta principal y se mantiene privado en una cuenta secundaria, donde sigue el desarrollo y el despliegue. En el evento se usará un Mac prestado.
8. **Decisión de publicación:** código abierto con licencia **MIT** y README en inglés y español para que el jurado lo lea sin barreras.

## 3. Validación de la física (hecha)

- Libración de la Tierra vista desde la Luna: ±6,8° latitud, ±7,9° longitud (esperado ~±6,7° / ±7,9°).
- Latitud subsolar: −1,56° a +1,59° (esperado ±1,54°).
- Longitud subsolar ≈ 180° en luna nueva (10/10/2026) y ≈ 0° en luna llena (26/10/2026); la fase del 10/10/2026 sale como luna nueva.
- `preparar_lola.py` probado con un GeoTIFF sintético: orientación correcta y rumbo = −longitud, y con el archivo real da −129,8°, igual que el cálculo teórico.

## 4. Incidencias resueltas (para el README de equipo)

| Síntoma | Causa | Solución |
|---|---|---|
| `No module named 'rasterio'` | Faltaba instalarlo | `python -m pip install rasterio` |
| `FileNotFoundError` en Streamlit Cloud | La carpeta `mapas/` no estaba en el repo | Subir `mapas/` y `datos/`, y *Reboot app* |
| `No such file` al preparar el mapa | El LDEM no estaba en la carpeta; además la extensión era `.tiff`, no `.tif` | Pasar la ruta correcta y `.tiff` |
| `streamlit` no reconocido (Windows) | No está en el PATH | `python -m streamlit run app.py` |
| `No module named 'skyfield'` | Dependencia sin instalar | `python -m pip install -r requirements.txt` |
| GitHub Desktop: *Files too large* | El `.tiff` pesa 685 MB (límite 100 MB) | Cancelar, desmarcarlo y añadir `.gitignore` |

## 5. Mejoras a incluir (hoja de ruta)

### Inmediato — cerrar EVO 2.2
- [ ] **Verificar en la app el mapa real de Shackleton** (4 comprobaciones):
  1. El cráter sale centrado (3D y pendientes).
  2. Las paredes salen en rojo (> 20°) y el fondo y la cresta en verde.
  3. La Tierra aparece cerca de 0° / 360° (±8°) en el gráfico del horizonte.
  4. Las sombras cambian de lado al mover el día de la misión.
- [x] **Malapert real** preparado (mapa de 750×750 del 6 de octubre). Falta comprobar que la montaña sale centrada. Comando usado como referencia: `python preparar_lola.py LDEM_80S_40MPP_ADJ.tiff --nombre malapert --lat -86.0 --lon 0.1 --km 30` y comprobar que la montaña sale centrada (coordenadas puestas de memoria).
- [ ] Subir a GitHub: `mapas/*.npy`, `mapas/*.json`, `datos/de421.bsp`, `.gitignore`, `requirements.txt` y `requirements-mapas.txt`. **No** subir los `.tiff`.
- [ ] Desplegar en Streamlit Cloud y probar el enlace desde otro dispositivo.

### Autopilot (nuevo, a pulir)
- [ ] Probar el Top 5 en Shackleton real y comprobar que los sitios son coherentes (fuera de paredes y de la zona muerta del 8 %).
- [ ] Decidir y documentar los **pesos 60/40** y el límite de pendiente de 10° (son una decisión de modelo, no oficiales).
- [ ] Que el Autopilot puntúe con **varios días** o con el mes completo, no solo con el día elegido.
- [ ] Preparar una respuesta corta para el jurado: *«¿por qué ese sitio?»* (seguridad primero, luz después, sitios separados entre sí).

### Ciencia y datos
- [ ] Bajar el **LDEM de 20 m/px** (2,6 GB) para la versión final del mapa de 30 km (1.500×1.500).
- [ ] **Zoom de ~2 km a ~5–10 m/px**: existen DEMs de 5 m/px de zonas de aterrizaje del polo sur (PGDA, producto 78) y `LDEM_83S_10MPP_ADJ` (4,8 GB, cubre desde 83°S: Malapert queda fuera).
- [ ] **Ventanas horarias** en vez de una evaluación diaria a las 12:00 UTC, especialmente para las comunicaciones.
- [x] Buscador automático del mejor punto → **hecho en EVO 2.6 (Autopilot)**, pero puntúa solo con la iluminación del **día elegido**.
- [ ] **Mapa de % de iluminación** del mes, para que el Autopilot puntúe con el mes completo (calcular en mapa grueso y guardar).
- [ ] **Comparador de sitios** lado a lado (el reto pide comparar sitios y fechas).
- [ ] Estudiar el disco de la Tierra, la curvatura lunar y el efecto de borde de mapa en el horizonte.

### Visual y producto
- [ ] Pulir la interfaz: coherencia de colores, textos cortos, modo "presentación".
- [ ] Elegir el punto **haciendo clic en el mapa** en vez de con sliders (investigar compatibilidad en Streamlit).
- [ ] Textura/colores por altura o albedo además del hillshade.
- [x] Versión en inglés → **README bilingüe hecho**; falta, si se quiere, la interfaz de la app en inglés.
- [ ] Capturas y un GIF de la demo para el README.

### Equipo, documentación y pitch
- [ ] Conocer el esqueleto de memoria: leer `lunar.py` línea a línea, especialmente `perfil_horizonte`.
- [ ] Página de "qué hace cada archivo" con tus propias palabras.
- [ ] Reparto de funciones del equipo y lista de herramientas.
- [ ] Documento profesional (Docs) y GitHub abierto: ~~licencia~~ (MIT hecha), ~~README~~ (hecho), falta **capturas** y GIF; instrucciones de reproducción ya están en el README.
- [ ] Presentación con guion (~3 min: problema, demo, límites, siguiente paso) y diapositiva de **limitaciones** explicadas con honestidad.
- [ ] Fijar versiones en `requirements.txt` (con `pip freeze`) cuando todo funcione, para que la nube no se rompa por actualizaciones.
- [ ] Qué hacer durante los *cooldowns* de las IAs: leer y romper el código, escribir el documento, ensayar el pitch, descargar datos, anotar dudas para llevarlas juntas.

### Visión a largo plazo: de web a software de escritorio
Decisión: **para el hackatón se mantiene la web** (el jurado abre un enlace y lo ve al instante). La versión de escritorio se presenta como visión, y se justifica porque la física ya está separada de la interfaz (`lunar.py` frente a `app.py`), así que el "cerebro" se reutiliza.

| Fase | Qué es | Qué aporta | Estado |
|---|---|---|---|
| 0 | Web en Streamlit Cloud | Acceso inmediato, sin instalar | ✅ actual (EVO 2.6) |
| 1 | Streamlit en local con mapas grandes (LDEM 20 m / 5 m) | Más resolución sin límites de la nube | ⏳ fácil, ya posible |
| 2 | Empaquetar en `.exe` (PyInstaller u otro) | Instalable, sin internet | ❓ no probado; puede dar problemas con Skyfield / rasterio |
| 3 | App de escritorio con motor 3D (p. ej. PySide6 + PyVista, Godot o Unity) | 3D con millones de puntos y GPU | 🔮 proyecto nuevo de semanas |

- [ ] Redactar la diapositiva de visión: *"Hoy es web para que cualquiera la use; la física está separada para llevarla a escritorio con mapas de 5 m."*
- [ ] Después del hackatón: probar la fase 1 y decidir si merece la pena la 2.

### Trazados y análisis de Sol y Tierra (ideas pendientes)
- [ ] **Trayectoria del Sol y de la Tierra** dibujada en el gráfico del horizonte (ya hay sus posiciones de los 30 días; son pocas líneas de código).
- [ ] **Mapa de iluminación del mes:** promedio de las sombras de cada día = % de tiempo con Sol por zona (se guarda en caché).
- [ ] **Animación de sombras día a día** (extra de presentación).
- [ ] **Estaciones de la DSN** (Goldstone, Canberra, Madrid): comprobar que la Luna también esté sobre el horizonte en alguna estación, para un enlace Direct-to-Earth completo. La base de lanzamiento no influye en el cielo lunar.
- [ ] **Dos niveles de mapa por sitio:** regional (30 km a 20-40 m, para horizonte e iluminación) y zoom local (2-5 km a 5-10 m, para la pendiente de aterrizaje).

## 6. Enlaces útiles

- Archivos de LOLA del polo sur: <https://pgda.gsfc.nasa.gov/products/90>
- DEMs de 5 m/px de sitios de aterrizaje: <https://pgda.gsfc.nasa.gov/products/78>
- Archivos disponibles (80S): `LDEM_80S_80MPP_ADJ` 181 MB · `LDEM_80S_40MPP_ADJ` 685 MB · `LDEM_80S_20MPP_ADJ` 2,6 GB
