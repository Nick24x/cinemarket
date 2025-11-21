from django.contrib import admin
from .models import Pelicula

@admin.register(Pelicula)
class PeliculaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'genero', 'anio', 'precio_arriendo', 'disponible')
    search_fields = ('titulo', 'genero')
    list_filter = ('genero', 'anio', 'disponible')
