from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Transaccion
from peliculas.models import Pelicula

def es_admin(u): return u.is_staff

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
        return redirect("home")  # o 'catalogo' si tienes otra vista

    return redirect("home")

@login_required
def historial(request):
    q = request.GET.get("q", "").strip()

    trans_qs = (
        Transaccion.objects
        .filter(usuario=request.user)
        .select_related("pelicula")
        .order_by("-fecha")
    )

    if q:
        trans_qs = trans_qs.filter(pelicula__titulo__icontains=q)

    return render(request, "transacciones/historial.html", {
        "transacciones": trans_qs,  # 👈 ahora el nombre coincide con el template
        "q": q,
    })

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
