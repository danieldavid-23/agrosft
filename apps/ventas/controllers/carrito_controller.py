from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
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


# NOTA: Estas importaciones dependen de modelos que NO existen en la BD actual
# from django.db import transaction
# from django.db.models import F
# from apps.ventas.forms.solicitud_form import CheckoutSolicitudForm
# from apps.clientes.models import Cliente
# from apps.ventas.models.solicitud import DetalleSolicitudCompra

def checkout_carrito(request):
    """
    Checkout del carrito - TEMPORALMENTE DESHABILITADO
    Las tablas necesarias no existen en la base de datos actual
    """
    messages.info(request, 'El checkout estará disponible próximamente.')
    return redirect('ventas:carrito_detalle')

# from apps.ventas.models.venta import Venta, DetalleVenta
# from apps.ventas.forms.venta_form import CheckoutVentaForm
# from apps.ventas.models.movimiento import Movimiento, ProductoUsuarioMovimiento, TipoMovimiento

def checkout_venta_carrito(request):
    """
    Checkout de venta - TEMPORALMENTE DESHABILITADO
    Las tablas necesarias no existen en la base de datos actual
    """
    messages.info(request, 'El checkout estará disponible próximamente.')
    return redirect('ventas:carrito_detalle')