from django.urls import path
from . import views
from .views import ver_pelicula

# URLs para la app de arriendos
app_name = 'arriendos' 
urlpatterns = [
    path('historial/', views.historial, name='historial'),
    path('comprar/<int:pelicula_id>/', views.comprar_pelicula, name='comprar_pelicula'),
    path('transacciones/<int:pk>/devolver/', views.devolver_transaccion, name='devolver_transaccion'),
    path('ver/<str:token>/', ver_pelicula, name='ver_pelicula'),
]