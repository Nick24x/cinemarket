import json
from peliculas.models import Pelicula
from django.core.files.base import ContentFile
import requests

# Cargar archivo JSON
with open("peliculas.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    titulo = item["titulo"]

    # Evitar duplicados
    if Pelicula.objects.filter(titulo=titulo).exists():
        print(f"Ya existe: {titulo}")
        continue

    # Crear película
    pelicula = Pelicula.objects.create(
        titulo=item["titulo"],
        genero=item["genero"],
        anio=item["anio"],
        calificacion=item["calificacion"],
        precio_arriendo=item["precio_arriendo"],
        descripcion=item["descripcion"]
    )

    # Descargar y guardar imagen
    if item.get("imagen"):
        try:
            resp = requests.get(item["imagen"])
            if resp.status_code == 200:
                pelicula.imagen.save(
                    f"{titulo.replace(' ', '_')}.jpg",
                    ContentFile(resp.content),
                    save=True
                )
        except Exception as e:
            print(f"Error imagen {titulo}: {e}")

    print(f"Película agregada: {titulo}")

print("Carga completada.")
