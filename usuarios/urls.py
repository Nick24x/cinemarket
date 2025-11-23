from django.urls import path
from . import views

urlpatterns = [
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path("mi-perfil/", views.mi_perfil, name="mi_perfil"),
    path("cambiar-password/", views.cambiar_password, name="cambiar_password"),
]