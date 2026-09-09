from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.ventas.models.movimiento import Movimiento, ProductoUsuarioMovimiento

# State mapping: internal DB type -> user-visible label
ESTADOS_COMPRA = {
    'compra': 'Pendiente',
    'venta': 'En proceso',
    'vendida': 'Finalizada',
}

ESTADOS_BADGE = {
    'compra': 'bg-warning text-dark',
    'venta': 'bg-primary',
    'vendida': 'bg-success',
}

ESTADOS_ICONO = {
    'compra': 'fa-clock',
    'venta': 'fa-spinner',
    'vendida': 'fa-check-circle',
}


@login_required
def listar_compras(request):
    """
    List all purchases made by the current user (buyer perspective).
    Shows movements where id_usuario = request.user.
    """
    movimientos = Movimiento.objects.filter(
        id_usuario=request.user
    ).select_related('id_tipo_movimiento').order_by('-id_movimiento')

    compras = []
    for mov in movimientos:
        tipo = mov.id_tipo_movimiento.tipo
        detalles = ProductoUsuarioMovimiento.objects.filter(
            id_movimiento=mov
        ).select_related('id_producto_usuario__id_producto')

        total = float(sum(
            abs(d.cantidad) * d.id_producto_usuario.precio
            for d in detalles
        ))

        # Build per-product info for the list view
        productos_info = []
        for d in detalles:
            productos_info.append({
                'movimiento_usuario_id': d.id_movimiento_usuario,
                'nombre': d.id_producto_usuario.id_producto.nombre,
            })

        compras.append({
            'id': mov.id_movimiento,
            'fecha': mov.obtener_fecha(),
            'total_productos': detalles.count(),
            'total': total,
            'estado': ESTADOS_COMPRA.get(tipo, tipo),
            'badge_class': ESTADOS_BADGE.get(tipo, 'bg-secondary'),
            'icono': ESTADOS_ICONO.get(tipo, 'fa-question'),
            'tipo_interno': tipo,
            'productos_info': productos_info,
        })

    return render(request, 'ventas/compras/compra_list.html', {
        'compras': compras,
    })


@login_required
def detalle_compra(request, pk):
    """
    Show detail of a specific purchase. Only the buyer can view it.
    """
    movimiento = get_object_or_404(Movimiento, pk=pk, id_usuario=request.user)
    tipo = movimiento.id_tipo_movimiento.tipo

    productos_qs = ProductoUsuarioMovimiento.objects.filter(
        id_movimiento=movimiento
    ).select_related(
        'id_producto_usuario__id_producto',
        'id_producto_usuario__id_producto__id_categoria',
        'id_producto_usuario__id_usuario',
    )

    total = float(sum(
        abs(d.cantidad) * d.id_producto_usuario.precio
        for d in productos_qs
    ))

    # Attach metadata to each product line
    productos = []
    for d in productos_qs:
        productos.append({
            'detalle': d,
            'movimiento_usuario_id': d.id_movimiento_usuario,
        })

    return render(request, 'ventas/compras/compra_detail.html', {
        'compra': {
            'id': movimiento.id_movimiento,
            'fecha': movimiento.obtener_fecha(),
            'estado': ESTADOS_COMPRA.get(tipo, tipo),
            'badge_class': ESTADOS_BADGE.get(tipo, 'bg-secondary'),
            'icono': ESTADOS_ICONO.get(tipo, 'fa-question'),
            'total': total,
        },
        'productos': productos,
    })
