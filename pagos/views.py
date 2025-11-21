import mercadopago
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.http import Http404
from django.urls import reverse

from peliculas.models import Pelicula
from arriendos.models import Transaccion


@login_required
def iniciar_pago(request, pelicula_id, tipo):
    pelicula = get_object_or_404(Pelicula, id=pelicula_id)

    tipo = tipo.lower()
    if tipo not in ("arriendo", "compra"):
        raise Http404("Tipo de operación no válido")

    precio = float(pelicula.precio_arriendo)  # luego lo cambiamos cuando tengas precio_compra

    sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)

    preference_data = {
        "items": [
            {
                "title": f"{tipo.capitalize()} - {pelicula.titulo}",
                "quantity": 1,
                "currency_id": "CLP",
                "unit_price": precio,
            }
        ],
        "payer": {
            "email": request.user.email or "test_user@example.com"
        },
        # las back_urls aquí dan igual, porque NO vamos a depender de ellas
    }

    result = sdk.preference().create(preference_data)
    response = result.get("response", {})

    print("MP preference response:", response)

    init_point = response.get("init_point") or response.get("sandbox_init_point")
    if not init_point:
        return render(request, "pagos/error_mp.html", {
            "mensaje": "No se pudo obtener la URL de pago de Mercado Pago.",
            "detalle": response,
        })

    # 👇 en vez de redirect(init_point), mostramos una página puente
    return render(request, "pagos/checkout_puente.html", {
        "init_point": init_point,
        "pelicula": pelicula,
        "tipo": tipo,
    })

@login_required
@login_required
def pago_success(request, pelicula_id, tipo):
    pelicula = get_object_or_404(Pelicula, id=pelicula_id)

    tipo = tipo.lower()
    if tipo not in ("arriendo", "compra"):
        raise Http404("Tipo de operación no válido")

    precio = pelicula.precio_arriendo

    trans = Transaccion.objects.create(
        usuario=request.user,
        pelicula=pelicula,
        tipo=tipo,
        precio=precio,
    )

    mp_status = request.GET.get("status")
    mp_payment_id = request.GET.get("payment_id")
    mp_pref_id = request.GET.get("preference_id")

    contexto = {
        "transaccion": trans,
        "mp_status": mp_status,
        "mp_payment_id": mp_payment_id,
        "mp_pref_id": mp_pref_id,
    }

    return render(request, "pagos/success.html", contexto)


@login_required
def pago_failure(request):
    return render(request, "pagos/failure.html")


@login_required
def pago_pending(request):
    return render(request, "pagos/pending.html")    
