import json

RUTA_ORIG = "peliculas.json"          # tu JSON actual
RUTA_NUEVA = "peliculas_con_compra.json"  # salida

with open(RUTA_ORIG, "r", encoding="utf-8") as f:
    peliculas = json.load(f)

for p in peliculas:
    arriendo = p.get("precio_arriendo")
    if arriendo is not None:
        p["precio_compra"] = arriendo + 800  # 👈 aquí definimos el “un poco más caro”

with open(RUTA_NUEVA, "w", encoding="utf-8") as f:
    json.dump(peliculas, f, ensure_ascii=False, indent=2)

print("Listo. Archivo generado:", RUTA_NUEVA)
