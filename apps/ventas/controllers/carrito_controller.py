from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.inventario.models import ProductoUsuario  # Cambiado de Producto a ProductoUsuario
from apps.ventas.services.carrito_service import Carrito
from core.utils.helpers import safe_int
import logging

logger = logging.getLogger(__name__)

def detalle_carrito(request):
    carrito = Carrito(request)
    return render(request, 'ventas/carrito/detalle.html', {'carrito': carrito})

def agregar_al_carrito(request, producto_id):
    carrito = Carrito(request)
    producto = get_object_or_404(ProductoUsuario, id_producto_usuario=producto_id)  # Cambiado para usar ProductoUsuario
    
    cantidad = 1
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        
    # Convertir cantidad disponible a entero ya que está almacenada como string
    cantidad_disponible = safe_int(producto.cantidad)  # Cambiado de stock a cantidad
    
    if cantidad > cantidad_disponible:
        messages.error(request, f'Solo hay {cantidad_disponible} unidades disponibles de {producto.id_producto.nombre}.')
    else:
        carrito.agregar(producto=producto, cantidad=cantidad)
        logger.info(f"User {request.user.pk} added product {producto_id} to cart")
        messages.success(request, f'{producto.id_producto.nombre} añadido al carrito.')
        
    # Obtener la URL desde donde se hizo la petición (Referer) para volver a esa página si es posible
    # o ir al detalle del carrito por defecto
    referer = request.META.get('HTTP_REFERER')
    if referer and 'carrito' not in referer:
        return redirect(referer)
    return redirect('ventas:carrito_detalle')

def actualizar_carrito(request, producto_id):
    carrito = Carrito(request)
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        producto = get_object_or_404(ProductoUsuario, id_producto_usuario=producto_id)  # Cambiado para usar ProductoUsuario
        cantidad_disponible = safe_int(producto.cantidad)  # Cambiado de stock a cantidad
        
        if cantidad > cantidad_disponible:
            messages.error(request, f'Solo hay {cantidad_disponible} unidades disponibles de {producto.id_producto.nombre}.')
        else:
            carrito.actualizar(producto_id=producto_id, cantidad=cantidad)
            messages.success(request, f'Cantidad actualizada correctamente.')
            
    return redirect('ventas:carrito_detalle')

def eliminar_del_carrito(request, producto_id):
    carrito = Carrito(request)
    carrito.eliminar(producto_id=producto_id)
    messages.success(request, 'Producto eliminado del carrito.')
    return redirect('ventas:carrito_detalle')


from django.db import transaction
from django.db.models import F
from apps.ventas.models.movimiento import Movimiento, ProductoUsuarioMovimiento, TipoMovimiento

@login_required
def checkout_carrito(request):
    """
    Checkout del carrito - Procesa la solicitud de compra
    """
    carrito = Carrito(request)
    
    if len(carrito) == 0:
        messages.error(request, 'No hay productos en el carrito.')
        return redirect('ventas:carrito_detalle')
    
    try:
        with transaction.atomic():
            # Crear movimiento de tipo compra
            tipo_compra, created = TipoMovimiento.objects.get_or_create(
                tipo='compra'
            )
            
            movimiento = Movimiento.objects.create(
                id_tipo_movimiento=tipo_compra,
                id_usuario=request.user
            )
            
            # Crear detalles del movimiento para cada producto en el carrito
            for item in carrito:
                producto_usuario = item['producto']
                cantidad = item['cantidad']
                
                # Verificar disponibilidad de stock
                if producto_usuario.cantidad < cantidad:
                    messages.error(request, f'No hay suficiente stock disponible para {producto_usuario.id_producto.nombre}.')
                    raise Exception(f'Stock insuficiente para {producto_usuario.id_producto.nombre}')
                
                # Crear detalle del movimiento
                ProductoUsuarioMovimiento.objects.create(
                    id_movimiento=movimiento,
                    id_producto_usuario=producto_usuario,
                    cantidad=cantidad
                )
                
                # Actualizar stock (restar la cantidad solicitada)
                producto_usuario.cantidad = F('cantidad') - cantidad
                producto_usuario.save()
            
            # Limpiar el carrito después del checkout exitoso
            carrito.limpiar()
            
            messages.success(request, f'¡Solicitud de compra #{movimiento.id_movimiento} creada exitosamente!')
            return redirect('ventas:solicitud_list')
            
    except Exception as e:
        messages.error(request, f'Error al procesar la solicitud de compra: {str(e)}')
        return redirect('ventas:carrito_detalle')


@login_required
def checkout_venta_carrito(request):
    """
    Checkout de venta - TEMPORALMENTE DESHABILITADO
    """
    messages.info(request, 'El checkout de venta estará disponible próximamente.')
    return redirect('ventas:carrito_detalle')