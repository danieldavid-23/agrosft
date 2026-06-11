from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.ventas.models.movimiento import Movimiento, ProductoUsuarioMovimiento, TipoMovimiento
from apps.inventario.models import ProductoUsuario

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
            'estado': venta.id_tipo_movimiento.tipo
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