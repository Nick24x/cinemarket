from django.contrib.auth.models import User
from django.db import models

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil', default=1)
    saldo = models.DecimalField(max_digits=10, decimal_places=0, default=0)

    def __str__(self):
        return self.user.username
