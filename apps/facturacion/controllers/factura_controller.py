import logging
import io
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404
from django.template.loader import render_to_string
from apps.facturacion.models import Factura
from apps.facturacion.services.factura_service import FacturaService
from apps.ventas.services.carrito_service import Carrito
from apps.ventas.models.movimiento import Movimiento, ProductoUsuarioMovimiento

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers de autorización
# ---------------------------------------------------------------------------

def _tiene_permiso_movimiento(usuario, movimiento):
    """Comprador, admin, o vendedor con productos en el movimiento."""
    if usuario.is_staff or movimiento.id_usuario == usuario:
        return True
    return ProductoUsuarioMovimiento.objects.filter(
        id_movimiento=movimiento,
        id_producto_usuario__id_usuario=usuario
    ).exists()


def _tiene_permiso_factura(usuario, factura):
    """
    Admin, comprador de la factura, o vendedor dueño de la factura.
    Previene IDOR: un usuario no puede ver facturas de otros.
    """
    if usuario.is_staff:
        return True
    if factura.usuario == usuario:
        return True
    # Vendedor dueño de la factura
    if factura.vendedor and factura.vendedor == usuario:
        return True
    # Compatibilidad con facturas legacy sin campo vendedor
    if factura.movimiento:
        return _tiene_permiso_movimiento(usuario, factura.movimiento)
    return False


# ---------------------------------------------------------------------------
# Crear facturas desde carrito (N facturas, una por vendedor)
# ---------------------------------------------------------------------------

@login_required
def crear_factura(request):
    """
    Procesa el carrito y genera UNA FACTURA POR VENDEDOR.
    Redirige al resumen de facturas del movimiento creado.
    """
    carrito = Carrito(request)
    if len(carrito) == 0:
        messages.error(request, 'No hay productos en el carrito.')
        return redirect('ventas:carrito_detalle')

    try:
        facturas = FacturaService.crear_facturas_desde_carrito(
            usuario=request.user,
            carrito=carrito,
        )
        carrito.limpiar()
        n = len(facturas)
        messages.success(
            request,
            f'¡Se generaron {n} factura{"s" if n != 1 else ""} exitosamente!'
        )
        # Redirigir al resumen del pedido (lista de facturas del movimiento)
        movimiento_id = facturas[0].movimiento_id
        return redirect('facturacion:facturas_pedido', movimiento_id=movimiento_id)
    except Exception as e:
        logger.exception("Error al crear facturas desde carrito")
        messages.error(request, f'Error al generar las facturas: {str(e)}')
        return redirect('ventas:carrito_detalle')


# ---------------------------------------------------------------------------
# Detalle de una factura
# ---------------------------------------------------------------------------

@login_required
def detalle_factura(request, factura_id):
    """Vista detallada de una factura. Autoriza comprador, vendedor o admin."""
    factura = get_object_or_404(Factura, id_factura=factura_id)
    if not _tiene_permiso_factura(request.user, factura):
        raise Http404("Factura no encontrada o no tienes permisos para verla.")
    items = factura.items.select_related('producto', 'producto__id_categoria').all()
    return render(request, 'facturacion/detalle_factura.html', {
        'factura': factura,
        'items': items,
    })


# ---------------------------------------------------------------------------
# Historial de facturas del usuario autenticado (como comprador)
# ---------------------------------------------------------------------------

@login_required
def historial_facturas(request):
    facturas = FacturaService.historial_usuario(request.user)
    return render(request, 'facturacion/historial_facturas.html', {
        'facturas': facturas,
    })


# ---------------------------------------------------------------------------
# Resumen de facturas de un pedido (movimiento)
# ---------------------------------------------------------------------------

@login_required
def facturas_pedido(request, movimiento_id):
    """
    Lista todas las facturas generadas para un pedido (movimiento).
    Visible para el comprador (ve todas), o para el vendedor (ve la suya).
    """
    movimiento = get_object_or_404(Movimiento, id_movimiento=movimiento_id)
    if not _tiene_permiso_movimiento(request.user, movimiento):
        raise Http404("Pedido no encontrado o no tienes permisos.")

    es_comprador = movimiento.id_usuario == request.user

    if es_comprador or request.user.is_staff:
        # Comprador/admin ve todas las facturas del pedido
        facturas = FacturaService.facturas_del_movimiento(movimiento)
    else:
        # Vendedor solo ve su propia factura
        factura_propia = FacturaService.factura_vendedor_en_movimiento(movimiento, request.user)
        facturas = [factura_propia] if factura_propia else []

    return render(request, 'facturacion/facturas_pedido.html', {
        'movimiento': movimiento,
        'facturas': facturas,
        'es_comprador': es_comprador,
    })


# ---------------------------------------------------------------------------
# Generar PDF de una factura
# ---------------------------------------------------------------------------

@login_required
def generar_pdf_factura(request, factura_id):
    factura = get_object_or_404(Factura, id_factura=factura_id)
    if not _tiene_permiso_factura(request.user, factura):
        raise Http404("Factura no encontrada o no tienes permisos para verla.")
    items = factura.items.select_related('producto', 'producto__id_categoria').all()

    html = render_to_string('facturacion/factura_pdf.html', {
        'factura': factura,
        'items': items,
    })

    result = io.BytesIO()
    from xhtml2pdf import pisa
    pisa_status = pisa.CreatePDF(html, dest=result, encoding='utf-8')

    if pisa_status.err:
        logger.error("Error al generar PDF de factura #%s", factura_id)
        messages.error(request, 'Error al generar el PDF.')
        return redirect('facturacion:detalle_factura', factura_id=factura_id)

    factura.pdf_generado = True
    factura.save(update_fields=['pdf_generado'])

    num_factura = f"FAC-{factura.id_factura:06d}"
    disposition_type = 'attachment' if request.GET.get('descargar') == '1' else 'inline'
    response = HttpResponse(result.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'{disposition_type}; filename="Factura_{num_factura}.pdf"'
    return response


# ---------------------------------------------------------------------------
# Generar facturas desde movimiento existente (endpoint legacy)
# ---------------------------------------------------------------------------

@login_required
def generar_factura_pedido(request, movimiento_id):
    """
    Genera (o recupera) las facturas de un movimiento y redirige al resumen.
    Compatible con el flujo de solicitudes/ventas existente.
    """
    movimiento = get_object_or_404(Movimiento, id_movimiento=movimiento_id)
    if not _tiene_permiso_movimiento(request.user, movimiento):
        raise Http404("Movimiento no encontrado o no tienes permisos para acceder.")
    try:
        FacturaService.crear_facturas_desde_movimiento(request.user, movimiento)
    except Exception as e:
        logger.exception("Error generando facturas del movimiento #%s", movimiento_id)
        messages.error(request, f'Error al generar las facturas: {str(e)}')
        return redirect('ventas:solicitud_list')

    return redirect('facturacion:facturas_pedido', movimiento_id=movimiento_id)
