from django.urls import path
from .views import devolver_transaccion
from . import views

app_name = 'arriendos' 
urlpatterns = [
    path('historial/', views.historial, name='historial'),
    path('comprar/<int:pelicula_id>/', views.comprar_pelicula, name='comprar_pelicula'),
    path('transacciones/<int:pk>/devolver/', devolver_transaccion, name='devolver_transaccion'),
]