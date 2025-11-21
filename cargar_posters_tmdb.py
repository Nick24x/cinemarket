import requests
from django.core.files.base import ContentFile
from peliculas.models import Pelicula

API_KEY = "4763b939ae8cedfea20c43165941ddf6"

SEARCH_URL = "https://api.themoviedb.org/3/search/movie"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"

def buscar_poster_tmdb(titulo, anio=None):
    params = {
        "api_key": API_KEY,
        "query": titulo,
        "language": "es-ES"
    }
    if anio:
        params["year"] = anio

    resp = requests.get(SEARCH_URL, params=params)
    if resp.status_code != 200:
        print(f"[TMDB] Error HTTP {resp.status_code} buscando {titulo}")
        return None

    results = resp.json().get("results") or []
    if not results:
        print(f"[TMDB] Sin resultados para {titulo}")
        return None

    poster_path = results[0].get("poster_path")
    if not poster_path:
        print(f"[TMDB] Sin poster_path para {titulo}")
        return None

    return IMAGE_BASE_URL + poster_path


def asignar_posters():
    for p in Pelicula.objects.all():
        print(f"Buscando poster para: {p.titulo} ({p.anio})")

        url_poster = buscar_poster_tmdb(p.titulo, p.anio)
        if not url_poster:
            url_poster = buscar_poster_tmdb(p.titulo)

        if not url_poster:
            print(f"No se pudo obtener poster para: {p.titulo}")
            continue

        try:
            img_resp = requests.get(url_poster)
            if img_resp.status_code != 200:
                print(f"Error HTTP {img_resp.status_code} descargando imagen de {p.titulo}")
                continue

            # Borro la imagen anterior para no dejar basura en el disco
            if p.imagen:
                p.imagen.delete(save=False)

            filename = f"{p.titulo.replace(' ', '_')}.jpg"
            p.imagen.save(filename, ContentFile(img_resp.content), save=True)
            print(f"Poster actualizado para: {p.titulo}")

        except Exception as e:
            print(f"Error descargando/guardando imagen de {p.titulo}: {e}")

    print("Proceso de asignación de posters terminado.")
