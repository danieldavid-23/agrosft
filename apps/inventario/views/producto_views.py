from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from apps.inventario.models import Producto, ProductoUsuario, Categoria
from apps.inventario.repositories.producto_repository import ProductoRepository
from apps.inventario.controllers.producto_controller import (
    listar_productos as controller_listar_productos,
    crear_producto as controller_crear_producto,
    editar_producto as controller_editar_producto,
    eliminar_producto as controller_eliminar_producto
)


@login_required
def producto_list(request):
    """Vista para listar productos"""
    return controller_listar_productos(request)


@login_required
def producto_detail(request, pk):
    """Vista para mostrar los detalles de un producto"""
    producto = get_object_or_404(ProductoUsuario, id_producto_usuario=pk)
    
    # Obtener productos relacionados (otros productos del mismo usuario o de la misma categoría)
    relacionados = ProductoUsuario.objects.filter(
        id_producto__id_categoria=producto.id_producto.id_categoria,
        id_producto_usuario__gt=0,
        id_producto__eliminado=False,
    ).exclude(
        id_producto_usuario=pk
    ).select_related('id_producto', 'id_estado', 'id_usuario')[:4]
    
    contexto = {
        'producto': producto,
        'relacionados': relacionados
    }
    return render(request, 'inventario/Productosdetalles.html', contexto)


@login_required
def producto_create(request):
    """Vista para crear un nuevo producto"""
    return controller_crear_producto(request)


@login_required
def producto_update(request, pk):
    """Vista para actualizar un producto existente"""
    return controller_editar_producto(request, pk)


@login_required
def producto_delete(request, pk):
    """Vista para eliminar un producto"""
    return controller_eliminar_producto(request, pk)


@login_required
def dashboard_inventario(request):
    # Estadísticas generales
    total_productos = Producto.objects.filter(eliminado=False).count()
    productos_activos = Producto.objects.filter(eliminado=False, estado='aprobado').count()
    productos_pendientes = Producto.objects.filter(eliminado=False, estado='pendiente').count()
    productos_rechazados = Producto.objects.filter(eliminado=False, estado='rechazado').count()
    
    contexto = {
        'total_productos': total_productos,
        'productos_activos': productos_activos,
        'productos_pendientes': productos_pendientes,
        'productos_rechazados': productos_rechazados,
    }
    
    return render(request, 'inventario/dashboard.html', contexto)


@login_required
def listar_productos_api(request):
    """Endpoint para listar productos con posibilidad de filtrar"""
    productos = ProductoRepository.get_all_with_filters(
        estado=request.GET.get('estado', ''),
        categoria_id=request.GET.get('categoria_id', ''),
        nombre=request.GET.get('nombre', '')
    )
    
    # Convertir a formato serializable
    productos_data = []
    for producto in productos:
        productos_data.append({
            'id': producto.id_producto_usuario if hasattr(producto, 'id_producto_usuario') else producto.id,
            'nombre': producto.id_producto.nombre if hasattr(producto, 'id_producto') else producto.nombre,
            'descripcion': producto.id_producto.descripcion if hasattr(producto, 'id_producto') else producto.descripcion,
            'categoria': producto.id_producto.id_categoria.nombre if hasattr(producto, 'id_producto') and producto.id_producto.id_categoria else '',
            'precio': float(producto.precio) if hasattr(producto, 'precio') else float(producto.precio if hasattr(producto, 'precio') else 0),
            'stock': int(producto.cantidad) if hasattr(producto, 'cantidad') else producto.cantidad,
            'estado': producto.id_estado.estado if hasattr(producto, 'id_estado') else producto.estado,
            'fecha_creacion': producto.fecha_creacion.strftime('%d/%m/%Y %H:%M') if hasattr(producto, 'fecha_creacion') else ''
        })
    
    return JsonResponse({'productos': productos_data})