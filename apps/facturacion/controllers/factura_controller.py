import json
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from apps.facturacion.models import Factura, MetodoPago
from apps.facturacion.services.factura_service import FacturaService
from apps.ventas.services.carrito_service import Carrito
from apps.facturacion.payment_gateways import get_gateway

logger = logging.getLogger(__name__)


@login_required
def seleccionar_pago(request):
    carrito = Carrito(request)
    if len(carrito) == 0:
        messages.error(request, 'No hay productos en el carrito.')
        return redirect('ventas:carrito_detalle')

    metodos = MetodoPago.objects.filter(estado='activo').order_by('orden')
    total = sum(float(item['subtotal']) for item in carrito)

    context = {
        'metodos': metodos,
        'total': round(total, 2),
        'items': [
            {
                'nombre': item['producto'].id_producto.nombre,
                'cantidad': item['cantidad'],
                'precio': float(item['precio']),
                'subtotal': float(item['subtotal']),
            }
            for item in carrito
        ],
    }
    return render(request, 'facturacion/seleccionar_pago.html', context)


@login_required
@require_POST
def iniciar_pago(request):
    carrito = Carrito(request)
    if len(carrito) == 0:
        messages.error(request, 'No hay productos en el carrito.')
        return redirect('ventas:carrito_detalle')

    metodo_codigo = request.POST.get('metodo_pago', 'mercadopago')
    try:
        factura = FacturaService.crear_factura_desde_carrito(
            usuario=request.user,
            carrito=carrito,
            metodo_pago_codigo=metodo_codigo,
        )
        resultado = FacturaService.procesar_pago(factura, request)
        if resultado.exito and resultado.redirect_url:
            carrito.limpiar()
            return redirect(resultado.redirect_url)
        elif resultado.exito:
            carrito.limpiar()
            messages.success(request, 'Solicitud de pago creada.')
            return redirect('facturacion:detalle_factura', factura_id=factura.id_factura)
        else:
            FacturaService.cancelar_factura(factura)
            messages.error(request, f'Error al procesar el pago: {resultado.mensaje}')
            return redirect('facturacion:seleccionar_pago')
    except Exception as e:
        logger.exception("Error en iniciar_pago")
        messages.error(request, f'Error: {str(e)}')
        return redirect('facturacion:seleccionar_pago')


@login_required
def retorno_pago(request, gateway):
    facturas = Factura.objects.filter(
        usuario=request.user, estado='pendiente'
    ).order_by('-creada_en')[:1]
    if facturas:
        factura = facturas[0]
        exito = FacturaService.confirmar_pago(factura)
        if exito:
            messages.success(request, f'Pago recibido. Factura #{factura.id_factura} generada.')
        else:
            messages.info(request, 'El pago esta pendiente de confirmacion.')
    return redirect('facturacion:historial_facturas')


@csrf_exempt
def webhook_pago(request, gateway):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            transaction_id = ''

            if gateway == 'mercadopago':
                transaction_id = data.get('data', {}).get('id') or data.get('id', '')
            elif gateway == 'wompi':
                transaction_id = data.get('data', {}).get('transaction', {}).get('id', '')
            elif gateway == 'paypal':
                transaction_id = data.get('resource', {}).get('id', '')

            if transaction_id:
                factura = Factura.objects.filter(transaction_id=transaction_id).first()
                if factura and factura.estado == 'pendiente':
                    FacturaService.confirmar_pago(factura, transaction_id)
                    return JsonResponse({'status': 'ok'})
        except Exception as e:
            logger.exception("Error en webhook")
    return JsonResponse({'status': 'ignored'})


@login_required
def detalle_factura(request, factura_id):
    factura = get_object_or_404(Factura, id_factura=factura_id, usuario=request.user)
    items = factura.items.select_related('producto').all()
    return render(request, 'facturacion/detalle_factura.html', {
        'factura': factura,
        'items': items,
    })


@login_required
def historial_facturas(request):
    facturas = FacturaService.historial_usuario(request.user)
    return render(request, 'facturacion/historial_facturas.html', {
        'facturas': facturas,
    })
