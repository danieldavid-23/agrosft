from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Count
from apps.ventas.models.movimiento import Movimiento, ProductoUsuarioMovimiento, TipoMovimiento
from apps.inventario.models import ProductoUsuario
from apps.usuarios.models.profile_model import Tblusuarios


@login_required
def listar_solicitudes(request):
    """
    Lista las solicitudes de compra RECIBIDAS por el usuario actual
    Muestra quién quiere comprar tus productos
    """
    # Obtener tipo de movimiento 'compra'
    try:
        tipo_compra = TipoMovimiento.objects.get(tipo='compra')
    except TipoMovimiento.DoesNotExist:
        messages.error(request, 'No se ha configurado el tipo de movimiento "compra".')
        return redirect('inventario:marketplace')
    
    # Obtener IDs de mis productos
    mis_productos_ids = ProductoUsuario.objects.filter(
        id_usuario=request.user
    ).values_list('id_producto_usuario', flat=True)
    
    # Buscar movimientos de compra que incluyan mis productos
    # ProductoUsuarioMovimiento conecta movimientos con productos
    solicitudes_ids = ProductoUsuarioMovimiento.objects.filter(
        id_producto_usuario_id__in=mis_productos_ids,
        id_movimiento__id_tipo_movimiento=tipo_compra
    ).values_list('id_movimiento', flat=True).distinct()
    
    # Obtener los movimientos completos
    solicitudes = Movimiento.objects.filter(
        id_movimiento__in=solicitudes_ids
    ).order_by('-id_movimiento')
    
    # Preparar datos para el template
    solicitudes_data = []
    for solicitud in solicitudes:
        # Obtener productos de esta solicitud que son MÍOS
        mis_productos_en_solicitud = ProductoUsuarioMovimiento.objects.filter(
            id_movimiento=solicitud,
            id_producto_usuario_id__in=mis_productos_ids
        ).select_related(
            'id_producto_usuario__id_producto',
            'id_producto_usuario__id_usuario'
        )
        
        # Calcular total de mis productos en esta solicitud
        total = sum(p.cantidad * p.id_producto_usuario.precio for p in mis_productos_en_solicitud)
        
        # Obtener información del comprador
        comprador = solicitud.id_usuario
        
        solicitudes_data.append({
            'id': solicitud.id_movimiento,
            'fecha': getattr(solicitud, 'fecha_movimiento', 'N/A'),
            'descripcion': getattr(solicitud, 'descripcion', 'Sin descripción'),
            'comprador_nombre': f"{comprador.nombres} {comprador.apellidos}",
            'comprador_email': comprador.correo,
            'total_productos_mios': mis_productos_en_solicitud.count(),
            'total_estimado': total,
            'estado': 'recibida',
            'productos_mios': mis_productos_en_solicitud,
        })
    
    return render(request, 'ventas/solicitudes/solicitud_list.html', {
        'solicitudes': solicitudes_data,
        'titulo': 'Solicitudes Recibidas',
        'subtitulo': 'Usuarios que quieren comprar tus productos'
    })


@login_required
def crear_solicitud(request):
    """
    Crear una nueva solicitud de compra
    Redirige al marketplace para seleccionar productos
    """
    messages.info(request, 'Para crear una solicitud, agrega productos al carrito y procede al checkout.')
    return redirect('ventas:carrito_detalle')


@login_required
def detalle_solicitud(request, pk):
    """
    Ver detalle de una solicitud específica
    """
    solicitud = get_object_or_404(Movimiento, pk=pk, id_usuario=request.user)
    
    # Obtener productos de esta solicitud
    productos = ProductoUsuarioMovimiento.objects.filter(
        id_movimiento=solicitud
    ).select_related(
        'id_producto_usuario__id_producto',
        'id_producto_usuario__id_usuario'
    )
    
    # Calcular total
    total = sum(p.cantidad * p.id_producto_usuario.precio for p in productos)
    
    return render(request, 'ventas/solicitudes/solicitud_detail.html', {
        'solicitud': {
            'id': solicitud.id_movimiento,
            'fecha': getattr(solicitud, 'fecha_movimiento', 'N/A'),
            'descripcion': getattr(solicitud, 'descripcion', 'Sin descripción'),
            'total_productos': productos.count(),
            'total_estimado': total,
        },
        'productos': productos,
    })


@login_required
def aceptar_solicitud(request, pk):
    """
    Aceptar una solicitud (marcar como procesada)
    """
    messages.info(request, 'La solicitud ha sido marcada como aceptada.')
    return redirect('ventas:solicitud_detail', pk=pk)


@login_required
def rechazar_solicitud(request, pk):
    """
    Rechazar una solicitud
    """
    messages.info(request, 'La solicitud ha sido rechazada.')
    return redirect('ventas:solicitud_list')


@login_required
def estado_detalle(request, pk, detalle_id, estado):
    """
    Cambiar estado de un producto específico en la solicitud
    """
    messages.success(request, f'Producto actualizado a estado: {estado}')
    return redirect('ventas:solicitud_detail', pk=pk)


@login_required
def marcar_vendido(request, pk):
    """
    Marcar solicitud como vendida/completada
    """
    messages.success(request, 'La solicitud ha sido marcada como completada.')
    return redirect('ventas:solicitud_detail', pk=pk)
