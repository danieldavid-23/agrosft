from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from apps.usuarios.models.profile_model import Tblusuarios
from apps.ventas.models.movimiento import Movimiento, ProductoUsuarioMovimiento

@login_required
def listar_clientes(request):
    """
    Vista que muestra el historial de clientes que han realizado compras
    o tienen procesos de compra activos
    Solo usa la tabla tblproductos_has_tblusuarios_has_movimiento
    """
    # Obtener todos los usuarios que han realizado movimientos (compras/ventas)
    usuarios_con_movimientos = Tblusuarios.objects.filter(
        movimientos_venta__isnull=False
    ).distinct().annotate(
        total_movimientos=Count('movimientos_venta'),
        total_compras=Count(
            'movimientos_venta',
            filter=Q(movimientos_venta__id_tipo_movimiento__tipo='compra')
        ),
        total_ventas=Count(
            'movimientos_venta',
            filter=Q(movimientos_venta__id_tipo_movimiento__tipo='venta')
        )
    )
    
    # Preparar datos para el template
    clientes_data = []
    for usuario in usuarios_con_movimientos:
        clientes_data.append({
            'id': usuario.id_users,
            'nombre': usuario.get_full_name(),
            'correo': usuario.correo,
            'telefono': usuario.telefono or 'No registrado',
            'total_movimientos': usuario.total_movimientos,
            'total_compras': usuario.total_compras,
            'total_ventas': usuario.total_ventas,
            'es_vendedor': usuario.total_ventas > 0,
            'es_comprador': usuario.total_compras > 0,
        })
    
    # Ordenar por cantidad de movimientos (más activos primero)
    clientes_data.sort(key=lambda x: x['total_movimientos'], reverse=True)
    
    return render(request, 'clientes/listar_clientes.html', {
        'clientes': clientes_data
    })

@login_required
def detalle_cliente(request, pk):
    """
    Vista que muestra el detalle de historial de compras/ventas de un cliente
    """
    usuario = get_object_or_404(Tblusuarios, id_users=pk)
    
    # Obtener movimientos del usuario desde tblproductos_has_tblusuarios_has_movimiento
    movimientos = ProductoUsuarioMovimiento.objects.select_related(
        'id_producto_usuario',
        'id_producto_usuario__id_producto',
        'id_movimiento'
    ).filter(
        id_movimiento__id_usuario=usuario
    ).order_by('-fecha_movimiento')
    
    # Estadísticas
    total_compras = movimientos.filter(
        id_movimiento__id_tipo_movimiento__tipo='compra'
    ).count()
    
    total_ventas = movimientos.filter(
        id_movimiento__id_tipo_movimiento__tipo='venta'
    ).count()
    
    contexto = {
        'cliente': usuario,
        'movimientos': movimientos[:20],  # Últimos 20 movimientos
        'total_compras': total_compras,
        'total_ventas': total_ventas,
    }
    
    return render(request, 'clientes/detalle_cliente.html', contexto)

@login_required
def historial_compras(request, cliente_id):
    """
    Vista que muestra exclusivamente el historial de compras de un cliente
    """
    usuario = get_object_or_404(Tblusuarios, id_users=cliente_id)
    
    compras = ProductoUsuarioMovimiento.objects.select_related(
        'id_producto_usuario',
        'id_producto_usuario__id_producto',
        'id_movimiento'
    ).filter(
        id_movimiento__id_usuario=usuario,
        id_movimiento__id_tipo_movimiento__tipo='compra'
    ).order_by('-fecha_movimiento')
    
    return render(request, 'clientes/historial_compras.html', {
        'cliente': usuario,
        'compras': compras
    })