from django.urls import path
from . import views

app_name = 'peliculas'

urlpatterns = [
    path("", views.home, name="home"),
    path("catalogo/", views.catalogo_publico, name="catalogo"),
    path("recomendaciones/", views.recomendaciones, name="recomendaciones"),
]
