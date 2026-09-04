from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from apps.usuarios.models.profile_model import Tblusuarios
from apps.ventas.models.movimiento import Movimiento, ProductoUsuarioMovimiento

@login_required
def listar_clientes(request):
    """
    Vista que muestra el historial de clientes que le han comprado al vendedor autenticado.
    """
    vendedor = request.user
    
    # Obtener detalles de movimientos válidos donde el producto pertenece al vendedor
    # y el comprador es otro usuario (excluyendo ventas canceladas)
    detalles_compras = ProductoUsuarioMovimiento.objects.filter(
        id_producto_usuario__id_usuario=vendedor,
        id_movimiento__id_tipo_movimiento__tipo__in=['compra', 'venta', 'vendida']
    ).exclude(
        id_movimiento__id_usuario=vendedor
    ).select_related(
        'id_movimiento__id_usuario',
        'id_movimiento__id_tipo_movimiento',
        'id_producto_usuario'
    )
    
    # Agrupar compras por cliente único
    clientes_dict = {}
    movimientos_por_cliente = {}

    for detalle in detalles_compras:
        cliente = detalle.id_movimiento.id_usuario
        c_id = cliente.id_users
        if c_id not in clientes_dict:
            clientes_dict[c_id] = {
                'id': c_id,
                'nombre': cliente.get_full_name() or cliente.correo,
                'correo': cliente.correo,
                'telefono': cliente.telefono or '',
                'total_compras_conmigo': 0,
            }
            movimientos_por_cliente[c_id] = set()

        # Contar pedidos únicos
        mov_id = detalle.id_movimiento_id
        if mov_id not in movimientos_por_cliente[c_id]:
            movimientos_por_cliente[c_id].add(mov_id)
            clientes_dict[c_id]['total_compras_conmigo'] += 1
    
    clientes_data = list(clientes_dict.values())
    clientes_data.sort(key=lambda x: x['total_compras_conmigo'], reverse=True)
    total_pedidos = sum(len(s) for s in movimientos_por_cliente.values())
    
    return render(request, 'clientes/listar_clientes.html', {
        'clientes': clientes_data,
        'total_clientes': len(clientes_data),
        'total_pedidos': total_pedidos
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