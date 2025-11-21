from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count, Q
from arriendos.models import Transaccion
from .models import Pelicula


def home(request):
    q = request.GET.get("q", "").strip()
    genre = request.GET.get("genre", "").strip()

    # Partimos de todas las películas
    peliculas_qs = Pelicula.objects.all()

    # Filtro por texto de búsqueda
    if q:
        request.session["ultima_busqueda"] = q
        peliculas_qs = peliculas_qs.filter(
            Q(titulo__icontains=q) |
            Q(genero__icontains=q) |
            Q(descripcion__icontains=q)
        ).distinct()
    else:
        request.session.pop("ultima_busqueda", None)

    # Filtro por género (si no es "Todos")
    if genre and genre.lower() != "todos":
        peliculas_qs = peliculas_qs.filter(genero__iexact=genre)

    # ✅ Paginación
    paginator = Paginator(peliculas_qs, 24)   # 24 pelis por página
    page_number = request.GET.get("page")
    peliculas = paginator.get_page(page_number)

    return render(request, "home.html", {
        "peliculas": peliculas,  # ahora es un Page, no un queryset
        "q": q,
        "genre": genre,
    })


def catalogo_publico(request):
    q = request.GET.get('q', '').strip()
    qs = Pelicula.objects.filter(disponible=True).order_by('-anio', 'titulo')
    if q:
        qs = qs.filter(titulo__icontains=q)
    page = Paginator(qs, 12).get_page(request.GET.get('page'))
    return render(request, 'peliculas/catalogo_publico.html', {
        'peliculas': page,
        'q': q
    })


def _populares(limit=16):
    pop_ids = (Transaccion.objects.filter(estado='completada')
               .values('pelicula').annotate(n=Count('id'))
               .order_by('-n')[:max(limit, 50)])
    ids = [x['pelicula'] for x in pop_ids]
    qs = (Pelicula.objects.filter(id__in=ids, disponible=True)
          .order_by('-calificacion', '-anio')[:limit])
    if not qs.exists():
        qs = (Pelicula.objects.filter(disponible=True)
              .order_by('-calificacion', '-anio')[:limit])
    return qs


def recomendaciones(request):
    peliculas = Pelicula.objects.none()

    # 1️⃣ Recomendación por búsqueda reciente
    ultima_busqueda = request.session.get("ultima_busqueda")

    if ultima_busqueda:
        peliculas = Pelicula.objects.filter(
            Q(titulo__icontains=ultima_busqueda) |
            Q(genero__icontains=ultima_busqueda) |
            Q(descripcion__icontains=ultima_busqueda)
        ).distinct()

    # 2️⃣ Si no encontró nada, recomendar por historial del usuario
    if request.user.is_authenticated and not peliculas.exists():
        generos_vistos = Transaccion.objects.filter(
            usuario=request.user
        ).values_list("pelicula__genero", flat=True)

        if generos_vistos:
            peliculas = Pelicula.objects.filter(
                genero__in=generos_vistos
            ).distinct()

    # 3️⃣ Si aún no hay nada, recomendar por calificación
    if not peliculas.exists():
        peliculas = Pelicula.objects.order_by("-calificacion")[:12]

    return render(request, "peliculas/recomendaciones.html", {
        "peliculas": peliculas
    })
