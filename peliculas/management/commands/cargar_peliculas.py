import json
from django.core.management.base import BaseCommand
from django.conf import settings
from peliculas.models import Pelicula


class Command(BaseCommand):
    help = "Carga o actualiza las películas desde un JSON"

    def handle(self, *args, **kwargs):
        # JSON ubicado al lado de manage.py
        ruta_json = settings.BASE_DIR / "peliculas_con_compra.json"

        try:
            with open(ruta_json, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error leyendo el JSON: {e}"))
            return

        total = 0

        for item in data:
            Pelicula.objects.update_or_create(
                titulo=item["titulo"],
                defaults={
                    "genero": item.get("genero"),
                    "anio": item.get("anio"),
                    "calificacion": item.get("calificacion"),
                    "precio_arriendo": item.get("precio_arriendo"),
                    "precio_compra": item.get("precio_compra"),
                    "descripcion": item.get("descripcion"),
                    # 👉 si NO tienes este campo en el modelo, borra esta línea
                    "imagen_url_original": item.get("imagen"),
                },
            )
            total += 1

        self.stdout.write(
            self.style.SUCCESS(f"Películas cargadas/actualizadas: {total}")
        )
