from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='admin_dashboard'),
    path('catalogo/', views.catalogo_admin, name='admin_catalogo'),
    path('catalogo/<int:pk>/editar/', views.pelicula_editar_admin, name='admin_pelicula_editar'),
    path('catalogo/<int:pk>/eliminar/', views.pelicula_eliminar_admin, name='admin_pelicula_eliminar'),
    path('reportes/', views.reportes_admin, name='admin_reportes'),
    path('transacciones/', views.transacciones_admin, name='admin_transacciones'),
    path('transacciones/<int:trans_id>/devolver/', views.transaccion_devolver , name='admin_transaccion_devolver'),
]
