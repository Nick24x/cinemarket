from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from peliculas import views as peliculas_views

urlpatterns = [
    # Home
    path('', peliculas_views.home, name='home'),
    path('arriendos/', include('arriendos.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('peliculas/', include('peliculas.urls')),
    path('panel/', include('panel.urls')),
    path('admin/', admin.site.urls),
    path('pagos/', include('pagos.urls', namespace='pagos')),
]

# Manejo de archivos multimedia
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Manejo de archivos estáticos en desarrollo
if settings.DEBUG:
    handler500 = 'django.views.defaults.server_error'
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
