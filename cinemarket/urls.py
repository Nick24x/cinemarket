from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from peliculas import views as peliculas_views  # 👈 usamos la home de películas

urlpatterns = [
    # Home del sitio = catálogo (home.html)
    path('', peliculas_views.home, name='home'),
    path('arriendos/', include('arriendos.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('peliculas/', include('peliculas.urls')),
    path('panel/', include('panel.urls')),
    path('admin/', admin.site.urls),
    path('pagos/', include('pagos.urls')),
    path("cuentas/", include("cuentas.urls")),
]

if settings.DEBUG:
    handler500 = 'django.views.defaults.server_error'
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
