from django.urls import path
from . import views

app_name = "pagos"

urlpatterns = [
    path("iniciar/<int:pelicula_id>/<str:tipo>/", views.iniciar_pago, name="iniciar_pago"),
    path("success/", views.pago_success, name="pago_success"),
    path("failure/", views.pago_failure, name="pago_failure"),
    path("pending/", views.pago_pending, name="pago_pending"),
    path("webhook/", views.mp_webhook, name="mp_webhook"),
]
