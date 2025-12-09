from django.db import models
from django.contrib.auth.models import User
from peliculas.models import Pelicula

# Clase de transacción para arriendos y compras de películas
from django.conf import settings
from django.db import models
from peliculas.models import Pelicula

class Transaccion(models.Model):
    TIPO_CHOICES = (
        ('arriendo', 'Arriendo'),
        ('compra', 'Compra'),
    )
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('completada', 'Completada'),
        ('devuelta', 'Devuelta'),
        ('rechazada', 'Rechazada'),
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transacciones'
    )
    pelicula = models.ForeignKey(Pelicula, on_delete=models.PROTECT, related_name='transacciones')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    precio = models.DecimalField(max_digits=9, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='pendiente')
    motivo_devolucion = models.TextField(blank=True)
    devuelta_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='devoluciones'
    )
    fecha_devolucion = models.DateTimeField(null=True, blank=True)

    # Campos MercadoPago
    mp_payment_id = models.CharField(max_length=50, null=True, blank=True)
    mp_status = models.CharField(max_length=20, null=True, blank=True)
    mp_preference_id = models.CharField(max_length=50, null=True, blank=True)

    # Campos de visualización
    ver_token = models.CharField(max_length=64, null=True, blank=True)
    ver_expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'{self.usuario} - {self.tipo} - {self.pelicula} - {self.estado}'
