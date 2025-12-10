from django.contrib.auth.decorators import login_required, user_passes_test # Asegura que solo admins accedan
from django.shortcuts import render, redirect, get_object_or_404 # Para renderizar plantillas y manejar redirecciones
from django.contrib import messages # Para mostrar mensajes flash
from django.core.paginator import Paginator # Para paginar listas largas
from django.db.models import Count, Sum # Para agregaciones en consultas
from django.http import HttpResponse # Para respuestas HTTP personalizadas
from peliculas.models import Pelicula
from peliculas.forms import PeliculaForm
from arriendos.models import Transaccion
from datetime import datetime, timedelta
from django.utils import timezone

from usuarios.models import Perfil

# Verifica si el usuario es administrador
def is_admin(user):
    return user.is_staff 


@login_required
@user_passes_test(is_admin)
# Panel de administración - Dashboard
def dashboard(request):
    total_peliculas = Pelicula.objects.count()
    total_transacciones = Transaccion.objects.count()
    total_arriendos = Transaccion.objects.filter(tipo='arriendo').count()
    total_compras   = Transaccion.objects.filter(tipo='compra').count()
    total_devueltas = Transaccion.objects.filter(estado='devuelta').count()

    # Ingresos por tipo de transacción
    ingreso_arriendos = (
        Transaccion.objects
        .filter(tipo='arriendo', estado='completada')
        .aggregate(total=Sum('precio'))['total'] or 0
    )
    ingreso_compras = (
        Transaccion.objects
        .filter(tipo='compra', estado='completada')
        .aggregate(total=Sum('precio'))['total'] or 0
    )
    ingresos_totales = ingreso_arriendos + ingreso_compras
    
    # Datos para el contexto de la plantilla
    ctx = {
        'total_peliculas': total_peliculas,
        'total_transacciones': total_transacciones,
        'total_arriendos': total_arriendos,
        'total_compras': total_compras,
        'total_devueltas': total_devueltas,
        'ingreso_arriendos': ingreso_arriendos,
        'ingreso_compras': ingreso_compras,
        'ingresos_totales': ingresos_totales,
        'ingreso_estimado': ingresos_totales,
    }
    return render(request, 'panel/dashboard.html', ctx)


@login_required
@user_passes_test(is_admin)
def catalogo_admin(request):
    # Alta (form en el panel izquierdo)
    if request.method == 'POST' and request.POST.get('_accion') == 'crear':
        form = PeliculaForm(request.POST, request.FILES)
        if form.is_valid():
            pelicula = form.save(commit=False)

            # Si no se indicó precio_compra, lo calculamos a partir del arriendo
            if not pelicula.precio_compra or pelicula.precio_compra == 0:
                base = pelicula.precio_arriendo or 0
                pelicula.precio_compra = base + 1500

            pelicula.save()
            messages.success(request, 'Película agregada.')
            return redirect('admin_catalogo')
    else:
        form = PeliculaForm()

    # Listado
    q = request.GET.get('q', '').strip()
    qs = Pelicula.objects.all().order_by('-anio', 'titulo')
    if q:
        qs = qs.filter(titulo__icontains=q)
    page = Paginator(qs, 12).get_page(request.GET.get('page'))

    return render(request, 'panel/catalogo_admin.html', {
        'form': form, 'peliculas': page, 'total': qs.count(), 'q': q
    })


@login_required
@user_passes_test(is_admin)
def pelicula_editar_admin(request, pk):
    obj = get_object_or_404(Pelicula, pk=pk)
    if request.method == 'POST':
        form = PeliculaForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            pelicula = form.save(commit=False)

            # Si el precio_compra quedó vacío o en 0, lo recalculamos
            if not pelicula.precio_compra or pelicula.precio_compra == 0:
                base = pelicula.precio_arriendo or 0
                pelicula.precio_compra = base + 1500

            pelicula.save()
            messages.success(request, 'Película actualizada.')
            return redirect('admin_catalogo')
    else:
        form = PeliculaForm(instance=obj)
    return render(request, 'panel/pelicula_form_admin.html', {'form': form, 'obj': obj})


@login_required
@user_passes_test(is_admin)
# Eliminar película
def pelicula_eliminar_admin(request, pk):
    """
    Ya no borramos: alternamos el campo `disponible`.
    Si viene POST, cambiamos disponible = not disponible y guardamos.
    """
    obj = get_object_or_404(Pelicula, pk=pk)

    if request.method == 'POST':
        obj.disponible = not obj.disponible
        obj.save()
        if obj.disponible:
            messages.success(request, f'“{obj.titulo}” activada nuevamente.')
        else:
            messages.success(request, f'“{obj.titulo}” desactivada correctamente.')
        return redirect('admin_catalogo')

    # Si GET: mostramos la confirmación (puedes reutilizar tu template actual)
    return render(request, 'panel/pelicula_delete_admin.html', {'obj': obj})


@login_required
@user_passes_test(is_admin)
def reportes_admin(request):
    # Ejemplos simples: top géneros y años
    por_genero = (
        Pelicula.objects.values('genero')
        .annotate(cantidad=Count('id'))
        .order_by('-cantidad')[:10]
    )
    por_anio = (
        Pelicula.objects.values('anio')
        .annotate(cantidad=Count('id'))
        .order_by('-anio')[:10]
    )
    return render(request, 'panel/reportes_admin.html', {
        'por_genero': por_genero,
        'por_anio': por_anio
    })


@login_required
@user_passes_test(is_admin)
# Transacciones
def transacciones_admin(request):
    trans = (
        Transaccion.objects
        .select_related('usuario', 'pelicula')
        .order_by('-fecha')[:200]
    )

    return render(request, 'panel/transacciones_admin.html', {
        'trans': trans,
    })


@login_required
@user_passes_test(is_admin)
def transaccion_devolver(request, trans_id):
    if request.method != "POST":
        return redirect('admin_transacciones')

    trans = get_object_or_404(Transaccion, id=trans_id)

    # Verificar límite de 15 minutos
    if timezone.now() > trans.fecha + timedelta(minutes=15):
        messages.error(request, "El reembolso ya no es posible. Superó el límite de 15 minutos.")
        return redirect('admin_transacciones')

    if trans.estado == 'devuelta':
        messages.info(request, 'Esta transacción ya estaba marcada como devuelta.')
        return redirect('admin_transacciones')

    trans.estado = 'devuelta'
    trans.devuelta_por = request.user
    trans.fecha_devolucion = timezone.now()
    trans.save()

    # Actualizar saldo del usuario que hizo la transacción
    perfil, created = Perfil.objects.get_or_create(user=trans.usuario)
    perfil.saldo += trans.precio
    perfil.save()

    messages.success(request, 'Transacción marcada como devuelta y saldo actualizado.')
    return redirect('admin_transacciones')

# Helpers para reportes
def _parse_date(s):
    # Intenta parsear una fecha en varios formatos
    if not s:
        return None
    for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


@login_required
@user_passes_test(is_admin)
# Reportes avanzados con filtros y exportación CSV
def reportes_admin(request):
    # Filtros
    tipo   = request.GET.get('tipo', 'todos')  
    genero = request.GET.get('genero', 'todos')        
    desde  = _parse_date(request.GET.get('desde', ''))
    hasta  = _parse_date(request.GET.get('hasta', ''))

    # Construir queryset base
    qs = (Transaccion.objects
          .select_related('pelicula', 'usuario')
          .order_by('-fecha'))
    
    # Aplicar filtros
    if tipo in ('arriendo', 'compra'):
        qs = qs.filter(tipo=tipo)

    if genero != 'todos':
        qs = qs.filter(pelicula__genero=genero)

    if desde:
        qs = qs.filter(fecha__date__gte=desde)
    if hasta:
        qs = qs.filter(fecha__date__lte=hasta)

    # Agregados
    ventas_totales = (qs.filter(estado='completada')
                        .aggregate(total=Sum('precio'))['total'] or 0)
    
    # Conteos por tipo
    compras_count   = qs.filter(tipo='compra').count()
    arriendos_count = qs.filter(tipo='arriendo').count()
    clientes_activos = qs.values('usuario').distinct().count()
    
    # Exportar CSV
    if request.GET.get('export') in ('1', 'csv'):
        import csv
        resp = HttpResponse(content_type='text/csv; charset=utf-8')
        resp['Content-Disposition'] = 'attachment; filename=reportes_cinemarket.csv'
        w = csv.writer(resp)
        w.writerow(['Fecha', 'Usuario', 'Tipo', 'Título', 'Género', 'Precio', 'Estado'])
        for t in qs:
            w.writerow([
                t.fecha.strftime('%d-%m-%Y %H:%M'),
                getattr(t.usuario, 'username', ''),
                t.tipo,
                t.pelicula.titulo if t.pelicula_id else '',
                t.pelicula.genero if t.pelicula_id else '',
                f"{t.precio:.0f}",
                t.estado,
            ])
        return resp

    generos = (Pelicula.objects
               .values_list('genero', flat=True)
               .distinct().order_by('genero'))

    ctx = {
        'f_tipo': tipo,
        'f_genero': genero,
        'f_desde': request.GET.get('desde', ''),
        'f_hasta': request.GET.get('hasta', ''),

        'generos': generos,
        'ventas_totales': ventas_totales,
        'compras_count': compras_count,
        'arriendos_count': arriendos_count,
        'clientes_activos': clientes_activos,
        'transacciones': qs[:200],
    }
    return render(request, 'panel/reportes_admin.html', ctx)
