# arriendos/views.py
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from django.http import Http404
from .models import Transaccion
from peliculas.models import Pelicula


def es_admin(u):
    return u.is_staff


@login_required
def comprar_pelicula(request, pelicula_id):
    print(">>> ENTRÓ A comprar_pelicula")  # DEBUG en consola

    pelicula = get_object_or_404(Pelicula, pk=pelicula_id, disponible=True)

    if request.method == "POST":
        Transaccion.objects.create(
            usuario=request.user,
            pelicula=pelicula,
            tipo='compra',
            precio=pelicula.precio_arriendo,
        )
        messages.success(request, f"Compraste: {pelicula.titulo}")
        # o podrías redirigir al historial si quieres
        return redirect("home")

    return redirect("home")


@login_required
def historial(request):
    """
    Historial que ve el CLIENTE.
    Solo muestra transacciones COMPLETADAS del usuario.
    Las pendientes / rechazadas se siguen guardando para reportes admin.
    """
    qs = (
        Transaccion.objects
        .filter(usuario=request.user, estado='completada')
        .select_related('pelicula')
        .order_by('-fecha')
    )

    # opcional: filtro por título
    q = request.GET.get('q', '').strip()
    if q:
        qs = qs.filter(pelicula__titulo__icontains=q)

    ctx = {
        "transacciones": qs,
        "q": q,
    }
    return render(request, "transacciones/historial.html", ctx)


@login_required
@user_passes_test(es_admin)
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


# -------------------
# Vista para ver película por token (la afinamos después)
# -------------------
@login_required
def ver_pelicula(request, token):
    # Token → transacción
    trans = get_object_or_404(Transaccion, token=token)

    # Verificamos que la transacción le pertenezca
    if trans.usuario != request.user:
        raise Http404("No tienes acceso a esta película.")

    # Si es arriendo, verificamos expiración
    if trans.tipo == "arriendo" and trans.expires_at:
        if timezone.now() > trans.expires_at:
            return render(request, "transacciones/expirado.html", {
                "pelicula": trans.pelicula,
            })

    peli = trans.pelicula

    # Validamos que exista el video
    if not peli.video_url and not peli.video:
        return render(request, "transacciones/sin_video.html")

    return render(request, "transacciones/ver_pelicula.html", {
        "pelicula": peli
    })
