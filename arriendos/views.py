# arriendos/views.py
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.http import Http404
from .models import Transaccion
from peliculas.models import Pelicula

# Función para verificar si el usuario es admin
def es_admin(u):
    return u.is_staff


@login_required
def comprar_pelicula(request, pelicula_id):
    # Obtener la película o 404 si no está disponible
    pelicula = get_object_or_404(Pelicula, pk=pelicula_id, disponible=True)

    if request.method == "POST":
        Transaccion.objects.create(
            usuario=request.user,
            pelicula=pelicula,
            tipo='compra',
            precio=pelicula.precio_arriendo,
        )
        messages.success(request, f"Compraste: {pelicula.titulo}")
        return redirect("home")

    return redirect("home")


@login_required
# Vista para el historial de transacciones
def historial(request):
    # Obtener las transacciones del usuario
    qs = (
        Transaccion.objects
        .filter(usuario=request.user, estado='completada')
        .select_related('pelicula')
        .order_by('-fecha')
    )

    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(pelicula__titulo__icontains=q)

    ctx = {
        "transacciones": qs,
        "q": q,
        "ahora": timezone.now(), #compara la expiración del link
    }
    return render(request, "transacciones/historial.html", ctx)


@login_required
@user_passes_test(es_admin)
# Vista para devolver una transacción
def devolver_transaccion(request, pk):
    tx = get_object_or_404(Transaccion, pk=pk)
    if request.method == 'POST':
        if tx.estado == 'devuelta':
            messages.info(request, 'La transacción ya fue devuelta.')
        else:
            tx.estado = 'devuelta'
            tx.devuelta_por = request.user
            tx.fecha_devolucion = timezone.now()
            tx.motivo_devolucion = request.POST.get('motivo', '')
            tx.save()
            messages.success(request, 'Transacción devuelta correctamente.')
    return redirect('arriendos:historial')



# Vista para ver película por token (la afinamos después)
def ver_pelicula(request, token):
    trans = get_object_or_404(Transaccion, ver_token=token)

    # validar que la transacción esté completada
    if trans.estado != "completada":
        raise Http404("La transacción no está completa.")

    # si es arriendo, verificar expiración
    if trans.tipo == "arriendo" and trans.ver_expires_at:
        if timezone.now() > trans.ver_expires_at:
            raise Http404("El arriendo ha expirado.")

    pelicula = trans.pelicula

    # fecha de expiración (solo arriendo)
    expira_en = trans.ver_expires_at if trans.tipo == "arriendo" else None

    # URL del video:
    # 1) si hay archivo subido
    # 2) si no, se usa video_url 
    if pelicula.video:
        video_url = pelicula.video.url
    elif pelicula.video_url:
        video_url = pelicula.video_url
    else:
        video_url = None
    # Renderizar la plantilla con el contexto 
    return render(
        request,
        "arriendos/ver_pelicula.html",
        {
            "transaccion": trans,
            "pelicula": pelicula,
            "usuario": trans.usuario,
            "expira_en": expira_en,
            "video_url": video_url,
        },
    )