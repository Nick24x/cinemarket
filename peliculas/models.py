from django.db import models

class Pelicula(models.Model):
    titulo = models.CharField(max_length=100)
    genero = models.CharField(max_length=50)
    anio = models.IntegerField()
    precio_arriendo = models.DecimalField(max_digits=7, decimal_places=0, default=0 )
    precio_compra = models.DecimalField(max_digits=7, decimal_places=0, default=0)
    disponible = models.BooleanField(default=True)
    calificacion = models.DecimalField(max_digits=2, decimal_places=1, default=0)  # 0.0–5.0
    imagen = models.ImageField(upload_to='peliculas/', null=True, blank=True)
    descripcion = models.TextField(blank=True)  # 👈 para el textarea opcional

    def __str__(self):
        return self.titulo
