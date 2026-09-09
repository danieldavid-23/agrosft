"""
Controlador para la gestión de ventas, movimientos y facturas
en el Panel de Administración.
"""
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Q
from apps.ventas.models.movimiento import Movimiento, ProductoUsuarioMovimiento
from apps.facturacion.models import Factura
from .admin_controller import admin_required


@admin_required
def lista_movimientos(request):
    """Listado de movimientos (compras y ventas)."""
    movimientos = Movimiento.objects.select_related(
        'id_tipo_movimiento', 'id_usuario'
    ).order_by('-id_movimiento')

    contexto = {
        'titulo': 'Movimientos',
        'movimientos': movimientos,
        'seccion_activa': 'movimientos',
    }
    return render(request, 'administracion/movimientos/lista.html', contexto)


@admin_required
def detalle_movimiento(request, pk):
    """Detalle de un movimiento con sus líneas de producto."""
    movimiento = get_object_or_404(
        Movimiento.objects.select_related('id_tipo_movimiento', 'id_usuario'),
        pk=pk,
    )
    detalles = ProductoUsuarioMovimiento.objects.filter(
        id_movimiento=movimiento
    ).select_related('id_producto_usuario__id_producto')

    total = sum(abs(d.cantidad) * d.id_producto_usuario.precio for d in detalles)

    contexto = {
        'titulo': f'Movimiento #{pk}',
        'movimiento': movimiento,
        'detalles': detalles,
        'total': total,
        'seccion_activa': 'movimientos',
    }
    return render(request, 'administracion/movimientos/detalle.html', contexto)


@admin_required
def lista_facturas(request):
    """Listado de facturas emitidas."""
    facturas = Factura.objects.select_related('usuario').order_by('-creada_en')

    contexto = {
        'titulo': 'Facturas',
        'facturas': facturas,
        'seccion_activa': 'facturas',
    }
    return render(request, 'administracion/facturas/lista.html', contexto)


@admin_required
def detalle_factura(request, pk):
    """Detalle de una factura con sus ítems."""
    factura = get_object_or_404(Factura.objects.select_related('usuario'), pk=pk)
    items = factura.items.all().select_related('producto')
    contexto = {
        'titulo': f'Factura #{pk}',
        'factura': factura,
        'items': items,
        'seccion_activa': 'facturas',
    }
    return render(request, 'administracion/facturas/detalle.html', contexto)