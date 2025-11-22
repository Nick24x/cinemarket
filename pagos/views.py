import json

import mercadopago
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from peliculas.models import Pelicula
from arriendos.models import Transaccion


@login_required
def iniciar_pago(request, pelicula_id, tipo):
    pelicula = get_object_or_404(Pelicula, id=pelicula_id)

    tipo = tipo.lower()
    if tipo not in ("arriendo", "compra"):
        raise Http404("Tipo de operación no válido")

    precio = float(pelicula.precio_arriendo)  # luego puedes cambiar a precio_compra si lo agregas

    # 1) Crear transacción en estado "pendiente"
    trans = Transaccion.objects.create(
        usuario=request.user,
        pelicula=pelicula,
        tipo=tipo,
        precio=precio,
        estado='pendiente',
    )

    print("MP_ACCESS_TOKEN >>>", repr(settings.MP_ACCESS_TOKEN))
    sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)

    # URL del webhook (debe ser pública en producción)
    notification_url = request.build_absolute_uri(reverse("pagos:mp_webhook"))

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
        # Para poder identificar la transacción en el webhook
        "external_reference": str(trans.id),

        "back_urls": {
            "success": request.build_absolute_uri(reverse("pagos:pago_success")),
            "failure": request.build_absolute_uri(reverse("pagos:pago_failure")),
            "pending": request.build_absolute_uri(reverse("pagos:pago_pending")),
        },
        "auto_return": "approved",

        # Webhook
        "notification_url": notification_url,
    }

    result = sdk.preference().create(preference_data)
    response = result.get("response", {})

    print("MP preference response:", response)

    # Guardamos el id de la preferencia en la transacción
    trans.mp_preference_id = response.get("id")
    trans.save()

    init_point = response.get("init_point") or response.get("sandbox_init_point")
    if not init_point:
        return render(request, "pagos/error_mp.html", {
            "mensaje": "No se pudo obtener la URL de pago de Mercado Pago.",
            "detalle": response,
        })

    # Página puente que abre la pantalla de MP
    return render(request, "pagos/checkout_puente.html", {
        "init_point": init_point,
        "pelicula": pelicula,
        "tipo": tipo,
        "transaccion": trans,
    })


@login_required
def pago_success(request):
    """
    Solo muestra un mensaje al usuario.
    El guardado REAL del pago lo hace el webhook.
    """
    mp_status = request.GET.get("status")
    mp_payment_id = request.GET.get("payment_id")
    mp_pref_id = request.GET.get("preference_id")

    transaccion = None
    if mp_pref_id:
        transaccion = Transaccion.objects.filter(mp_preference_id=mp_pref_id).first()

    contexto = {
        "transaccion": transaccion,
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


@csrf_exempt
def mp_webhook(request):
    """
    MercadoPago llama a esta URL cuando cambia el estado de un pago.
    Aquí consultamos el pago y actualizamos la Transaccion.
    """
    if request.method == "POST":
        try:
            payload = json.loads(request.body.decode("utf-8") or "{}")
        except json.JSONDecodeError:
            payload = {}

        # MP puede mandar info en query o en el body, cubrimos ambas
        topic = (
            request.GET.get("topic")
            or request.GET.get("type")
            or payload.get("type")
        )

        payment_id = (
            request.GET.get("id")
            or request.GET.get("data.id")
            or (payload.get("data") or {}).get("id")
        )

        if topic == "payment" and payment_id:
            sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)
            payment_info = sdk.payment().get(payment_id)
            payment = payment_info.get("response", {})

            status = payment.get("status")                 # approved, rejected, etc.
            external_ref = payment.get("external_reference")  # ID de Transaccion
            pref_id = payment.get("preference_id")

            if external_ref:
                try:
                    trans = Transaccion.objects.get(id=external_ref)
                    trans.mp_payment_id = str(payment_id)
                    trans.mp_status = status
                    trans.mp_preference_id = pref_id or trans.mp_preference_id

                    if status == "approved":
                        trans.estado = "completada"
                    elif status in ("rejected", "cancelled"):
                        trans.estado = "rechazada"

                    trans.save()
                except Transaccion.DoesNotExist:
                    pass

    # MP solo necesita un 200 para considerar que el webhook respondió bien
    return HttpResponse("OK", status=200)