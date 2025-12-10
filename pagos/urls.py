from django.urls import path
from . import views

# Definición del espacio de nombres para la aplicación de pagos
app_name = "pagos"

# urlpatterns para las vistas relacionadas con pagos
urlpatterns = [
    path("terminos/<int:pelicula_id>/<str:tipo>/", views.terminos_compra, name="terminos"),
    path("checkout_saldo/<int:pelicula_id>/<str:tipo>/", views.checkout_saldo, name="checkout_saldo"),
    path("iniciar/<int:pelicula_id>/<str:tipo>/", views.iniciar_pago, name="iniciar_pago"),
    path("success/", views.pago_success, name="pago_success"),
    path("failure/", views.pago_failure, name="pago_failure"),
    path("pending/", views.pago_pending, name="pago_pending"),
    path("webhook/", views.mp_webhook, name="mp_webhook"),
]
