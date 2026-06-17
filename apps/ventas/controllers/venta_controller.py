from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.ventas.models.movimiento import Movimiento, ProductoUsuarioMovimiento, TipoMovimiento
from apps.inventario.models import ProductoUsuario

# Mapeo de estado interno (BD) a estado visible para el usuario
ESTADOS_VISIBLES = {
    'venta': 'En proceso',
    'vendida': 'Vendido',
}

@login_required
def listar_ventas(request):
    """
    Lista las ventas del usuario (solicitudes aceptadas)
    """
    tipos_venta = TipoMovimiento.objects.filter(tipo__in=['venta', 'vendida'])
    
    mis_productos_ids = ProductoUsuario.objects.filter(
        id_usuario=request.user
    ).values_list('id_producto_usuario', flat=True)
    
    ventas_ids = ProductoUsuarioMovimiento.objects.filter(
        id_producto_usuario_id__in=mis_productos_ids,
        id_movimiento__id_tipo_movimiento__in=tipos_venta
    ).values_list('id_movimiento', flat=True).distinct()
    
    ventas = Movimiento.objects.filter(
        id_movimiento__in=ventas_ids
    ).order_by('-id_movimiento')
    
    ventas_data = []
    for venta in ventas:
        mis_productos = ProductoUsuarioMovimiento.objects.filter(
            id_movimiento=venta,
            id_producto_usuario_id__in=mis_productos_ids
        ).select_related(
            'id_producto_usuario__id_producto'
        )
        
        # Como en compras la cantidad se guarda negativa, usamos abs() para el total
        total = sum(abs(p.cantidad) * p.id_producto_usuario.precio for p in mis_productos)
        comprador = venta.id_usuario
        
        ventas_data.append({
            'id': venta.id_movimiento,
            'cliente': comprador,
            'fecha_venta': venta.obtener_fecha(),
            'total': total,
            'estado': venta.id_tipo_movimiento.tipo,
            'estado_visible': ESTADOS_VISIBLES.get(venta.id_tipo_movimiento.tipo, venta.id_tipo_movimiento.tipo.title()),
            'puede_marcar_vendido': venta.id_tipo_movimiento.tipo == 'venta',
        })

    return render(request, 'ventas/venta_list.html', {
        'ventas': ventas_data
    })

@login_required
def detalle_venta(request, pk):
    """
    Ver detalle de una venta específica
    """
    tipos_venta = TipoMovimiento.objects.filter(tipo__in=['venta', 'vendida'])
    venta = get_object_or_404(Movimiento, pk=pk, id_tipo_movimiento__in=tipos_venta)
    
    mis_productos_ids = ProductoUsuario.objects.filter(
        id_usuario=request.user
    ).values_list('id_producto_usuario', flat=True)
    
    productos = ProductoUsuarioMovimiento.objects.filter(
        id_movimiento=venta,
        id_producto_usuario_id__in=mis_productos_ids
    ).select_related(
        'id_producto_usuario__id_producto',
        'id_producto_usuario__id_usuario'
    )
    
    if not productos.exists():
        messages.error(request, 'No tienes permiso para ver esta venta o no contiene productos tuyos.')
        return redirect('ventas:venta_list')
        
    total = sum(abs(p.cantidad) * p.id_producto_usuario.precio for p in productos)
    comprador = venta.id_usuario
    
    venta_data = {
        'id': venta.id_movimiento,
        'fecha': venta.obtener_fecha(),
        'descripcion': getattr(venta, 'descripcion', 'Sin descripción'),
        'estado': venta.id_tipo_movimiento.tipo,
        'estado_visible': ESTADOS_VISIBLES.get(venta.id_tipo_movimiento.tipo, venta.id_tipo_movimiento.tipo.title()),
        'puede_marcar_vendido': venta.id_tipo_movimiento.tipo == 'venta',
        'comprador_nombre': f"{comprador.nombres} {comprador.apellidos}",
        'comprador_email': comprador.correo,
        'comprador_telefono': getattr(comprador, 'telefono', 'No proporcionado'),
        'total_estimado': total,
    }
    
    return render(request, 'ventas/venta_detail.html', {
        'venta': venta_data,
        'productos': productos,
    })

@login_required
def crear_venta(request):
    messages.info(request, 'Para crear una venta, acepta una solicitud de compra.')
    return redirect('ventas:solicitud_list')


@login_required
def marcar_como_vendida(request, pk):
    """
    Cambiar el estado de una venta de 'venta' (en proceso) a 'vendida' (vendido/completada).
    Solo el vendedor dueño de los productos puede marcarla como vendida.
    """
    if request.method != 'POST':
        messages.error(request, 'Método no permitido.')
        return redirect('ventas:venta_list')

    tipo_venta = get_object_or_404(TipoMovimiento, tipo='venta')
    venta = get_object_or_404(Movimiento, pk=pk, id_tipo_movimiento=tipo_venta)

    # Verificar que el usuario actual es vendedor de al menos un producto en esta venta
    mis_productos_ids = ProductoUsuario.objects.filter(
        id_usuario=request.user
    ).values_list('id_producto_usuario', flat=True)

    tiene_productos = ProductoUsuarioMovimiento.objects.filter(
        id_movimiento=venta,
        id_producto_usuario_id__in=mis_productos_ids
    ).exists()

    if not tiene_productos:
        messages.error(request, 'No tienes permiso para marcar como vendida esta venta.')
        return redirect('ventas:venta_list')

    # Verificar stock suficiente antes de marcar como vendida.
    # El trigger trg_descontar_stock_vendida descontara el stock automaticamente
    # al cambiar tipo_movimiento a 'vendida'. Validamos primero para evitar
    # que el stock quede en negativo.
    detalles = ProductoUsuarioMovimiento.objects.filter(
        id_movimiento=venta,
        id_producto_usuario_id__in=mis_productos_ids
    ).select_related('id_producto_usuario__id_producto')

    for detalle in detalles:
        pu = detalle.id_producto_usuario
        cantidad_solicitada = abs(detalle.cantidad)
        if pu.cantidad < cantidad_solicitada:
            messages.error(
                request,
                f'Stock insuficiente para "{pu.id_producto.nombre}". '
                f'Disponible: {int(pu.cantidad)}, solicitado: {int(cantidad_solicitada)}.'
            )
            return redirect('ventas:venta_detail', pk=pk)

    try:
        tipo_vendida = TipoMovimiento.objects.get_or_create(tipo='vendida')[0]
        venta.id_tipo_movimiento = tipo_vendida
        venta.save()  # El trigger trg_descontar_stock_vendida descuenta stock aqui
        messages.success(request, f'¡Venta #{pk} marcada como vendida y stock actualizado!')
    except Exception as e:
        messages.error(request, f'Error al marcar como vendida: {str(e)}')

    return redirect('ventas:venta_detail', pk=pk)