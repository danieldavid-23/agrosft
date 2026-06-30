import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.facturacion.models import Factura
from apps.facturacion.services.factura_service import FacturaService
from apps.ventas.services.carrito_service import Carrito

logger = logging.getLogger(__name__)


@login_required
def crear_factura(request):
    carrito = Carrito(request)
    if len(carrito) == 0:
        messages.error(request, 'No hay productos en el carrito.')
        return redirect('ventas:carrito_detalle')

    try:
        factura = FacturaService.crear_factura_desde_carrito(
            usuario=request.user,
            carrito=carrito,
        )
        carrito.limpiar()
        messages.success(request, f'Factura #{factura.id_factura} generada exitosamente.')
        return redirect('facturacion:detalle_factura', factura_id=factura.id_factura)
    except Exception as e:
        logger.exception("Error al crear factura")
        messages.error(request, f'Error al generar la factura: {str(e)}')
        return redirect('ventas:carrito_detalle')


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
