# arriendos/admin.py
from django.contrib import admin
from .models import Transaccion

@admin.register(Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'pelicula', 'tipo', 'precio', 'estado', 'fecha', 'fecha_devolucion')
    list_filter  = ('tipo', 'estado', 'fecha')
    search_fields = ('pelicula__titulo', 'usuario__username')
