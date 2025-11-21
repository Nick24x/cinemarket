from django.urls import path
from . import views

app_name = 'peliculas'

urlpatterns = [
    # /peliculas/  (y también la usaremos como home del sitio)
    path("", views.home, name="home"),

    # catálogo alternativo si quieres usarlo
    path("catalogo/", views.catalogo_publico, name="catalogo"),

    # recomendaciones
    path("recomendaciones/", views.recomendaciones, name="recomendaciones"),
]
