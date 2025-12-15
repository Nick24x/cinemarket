from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Count, Q
from arriendos.models import Transaccion
from .models import Pelicula


def home(request):
    q = request.GET.get("q", "").strip()
    genre = request.GET.get("genre", "").strip()

    # ✅ SOLO películas disponibles
    peliculas_qs = Pelicula.activas.all()

    if q:
        request.session["ultima_busqueda"] = q
        peliculas_qs = peliculas_qs.filter(
            Q(titulo__icontains=q) |
            Q(genero__icontains=q) |
            Q(descripcion__icontains=q)
        ).distinct()
    else:
        request.session.pop("ultima_busqueda", None)

    if genre and genre.lower() != "todos":
        peliculas_qs = peliculas_qs.filter(genero__iexact=genre)

    paginator = Paginator(peliculas_qs, 24)
    peliculas = paginator.get_page(request.GET.get("page"))

    return render(request, "home.html", {
        "peliculas": peliculas,
        "q": q,
        "genre": genre,
    })


def catalogo_publico(request):
    q = request.GET.get('q', '').strip()
    qs = Pelicula.activas.order_by('-anio', 'titulo')

    if q:
        qs = qs.filter(titulo__icontains=q)

    page = Paginator(qs, 12).get_page(request.GET.get('page'))

    return render(request, 'peliculas/catalogo.html', {
        'peliculas': page,
        'q': q
    })


def recomendaciones(request):
    peliculas = Pelicula.objects.none()
    ultima_busqueda = request.session.get("ultima_busqueda")

    if ultima_busqueda:
        peliculas = Pelicula.activas.filter(
            Q(titulo__icontains=ultima_busqueda) |
            Q(genero__icontains=ultima_busqueda) |
            Q(descripcion__icontains=ultima_busqueda)
        ).distinct()

    if request.user.is_authenticated and not peliculas.exists():
        generos_vistos = Transaccion.objects.filter(
            usuario=request.user
        ).values_list("pelicula__genero", flat=True)

        if generos_vistos:
            peliculas = Pelicula.activas.filter(
                genero__in=generos_vistos
            ).distinct()

    if not peliculas.exists():
        peliculas = Pelicula.activas.order_by("-calificacion")[:12]

    return render(request, "peliculas/recomendaciones.html", {
        "peliculas": peliculas
    })
