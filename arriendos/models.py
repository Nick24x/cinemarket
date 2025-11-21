from django.db import models
from django.contrib.auth.models import User
from peliculas.models import Pelicula

class Transaccion(models.Model):
    TIPO_CHOICES = (
        ('arriendo', 'Arriendo'),
        ('compra', 'Compra'),
    )
    ESTADO_CHOICES = (
        ('completada', 'Completada'),
        ('devuelta', 'Devuelta'),
    )

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transacciones')
    pelicula = models.ForeignKey(Pelicula, on_delete=models.PROTECT, related_name='transacciones')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    precio = models.DecimalField(max_digits=9, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='completada')
    motivo_devolucion = models.TextField(blank=True)
    devuelta_por = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='devoluciones')
    fecha_devolucion = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.usuario} - {self.tipo} - {self.pelicula} - {self.estado}'
