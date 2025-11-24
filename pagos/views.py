import json
import uuid
from datetime import timedelta

import mercadopago
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt

from peliculas.models import Pelicula
from arriendos.models import Transaccion


@login_required
def iniciar_pago(request, pelicula_id, tipo):
    pelicula = get_object_or_404(Pelicula, id=pelicula_id)

    tipo = tipo.lower()
    if tipo not in ("arriendo", "compra"):
        raise Http404("Tipo de operación no válido")

    # Usar precio correcto según tipo
    if tipo == "arriendo":
        precio = float(pelicula.precio_arriendo)
    else:  # compra
        precio = float(pelicula.precio_compra)

    # 1) Crear transacción pendiente
    trans = Transaccion.objects.create(
        usuario=request.user,
        pelicula=pelicula,
        tipo=tipo,
        precio=precio,
        estado="pendiente",
    )

    sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)

    # URLs absolutas
    success_url = request.build_absolute_uri(reverse("pagos:pago_success"))
    failure_url = request.build_absolute_uri(reverse("pagos:pago_failure"))
    pending_url = request.build_absolute_uri(reverse("pagos:pago_pending"))
    notification_url = request.build_absolute_uri(reverse("pagos:mp_webhook"))

    # Forzar https (Railway soporta https)
    success_url = success_url.replace("http://", "https://")
    failure_url = failure_url.replace("http://", "https://")
    pending_url = pending_url.replace("http://", "https://")
    notification_url = notification_url.replace("http://", "https://")

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
        "external_reference": str(trans.id),
        "back_urls": {
            "success": success_url,
            "failure": failure_url,
            "pending": pending_url,
        },
        "auto_return": "approved",
        "notification_url": notification_url,
    }

    print("PREFERENCE DATA ENVIADA A MP >>>", preference_data)

    result = sdk.preference().create(preference_data)
    response = result.get("response", {})

    print("MP preference response:", response)

    trans.mp_preference_id = response.get("id")
    trans.save()

    init_point = response.get("init_point") or response.get("sandbox_init_point")
    if not init_point:
        return render(
            request,
            "pagos/error_mp.html",
            {
                "mensaje": "No se pudo obtener la URL de pago de Mercado Pago.",
                "detalle": response,
            },
        )

    return redirect(init_point)


@login_required
def pago_success(request):
    return redirect("home")


@login_required
def pago_failure(request):
    return redirect("home")


@login_required
def pago_pending(request):
    return redirect("home")


@csrf_exempt
def mp_webhook(request):
    """
    MercadoPago llama a esta URL cuando cambia el estado de un pago.
    Actualizamos la Transaccion según el external_reference.
    Si el pago queda 'approved':
      - marcamos la transacción como 'completada'
      - generamos un ver_token único
      - seteamos ver_expires_at para arriendos (48h)
      - enviamos email con link
    """
    print("WEBHOOK RECIBIDO >>>", request.method, request.GET)

    # Intentamos leer JSON (si lo hay)
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        payload = {}

    print("WEBHOOK PAYLOAD >>>", payload)

    # MP puede mandar info en query o en el body
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

        print("INFO PAGO MP >>>", payment)

        status = payment.get("status")  # approved, rejected, etc.
        external_ref = payment.get("external_reference")  # ID de Transaccion
        pref_id = payment.get("preference_id")

        if external_ref:
            try:
                trans = Transaccion.objects.get(id=external_ref)
                trans.mp_payment_id = str(payment_id)
                trans.mp_status = status
                trans.mp_preference_id = pref_id or trans.mp_preference_id

                if status == "approved":
                    # Generar token único si no existe aún
                    if not trans.ver_token:
                        trans.ver_token = uuid.uuid4().hex

                    # Expiración solo para arriendo (ej: 48 horas)
                    if trans.tipo == "arriendo":
                        trans.ver_expires_at = timezone.now() + timedelta(hours=48)
                    else:  # compra -> sin expiración
                        trans.ver_expires_at = None

                    trans.estado = "completada"

                    print("TRANSACCION APROBADA >>>", trans.id, trans.tipo)
                    print("LINK TOKEN GENERADO >>>", trans.ver_token)
                    if trans.ver_expires_at:
                        print("EXPIRA EL >>>", trans.ver_expires_at)

                    trans.save()
                    enviar_email_entrega(trans)

                elif status in ("rejected", "cancelled"):
                    trans.estado = "rechazada"
                    trans.save()

                print("TRANSACCION ACTUALIZADA >>>", trans.id, trans.estado)

            except Transaccion.DoesNotExist:
                print("NO SE ENCONTRO TRANSACCION CON ID", external_ref)

    return HttpResponse("OK", status=200)


def enviar_email_entrega(transaccion: Transaccion):
    user = transaccion.usuario
    pelicula = transaccion.pelicula
    expiracion = transaccion.ver_expires_at if transaccion.tipo == "arriendo" else None

    html_message = render_to_string(
        "emails/entrega_pelicula.html",
        {
            "usuario": user,
            "pelicula": pelicula,
            "transaccion": transaccion,
            "expiracion": expiracion,
            "link": f"https://cinemarket-production.up.railway.app/arriendos/ver/{transaccion.ver_token}/",
        },
    )
    plain_message = strip_tags(html_message)

    try:
        send_mail(
            subject=(
                f"Tu {'arriendo' if transaccion.tipo == 'arriendo' else 'compra'} "
                f"de {pelicula.titulo}"
            ),
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
        )
        print("EMAIL ENVIADO >>>", user.email)
    except Exception as e:
        print("ERROR ENVIANDO EMAIL >>>", e)
