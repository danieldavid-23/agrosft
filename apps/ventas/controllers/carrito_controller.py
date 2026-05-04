from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from apps.inventario.models import Producto
from apps.ventas.services.carrito_service import Carrito

def detalle_carrito(request):
    carrito = Carrito(request)
    return render(request, 'ventas/carrito/detalle.html', {'carrito': carrito})

def agregar_al_carrito(request, producto_id):
    carrito = Carrito(request)
    producto = get_object_or_404(Producto, id=producto_id)
    
    cantidad = 1
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        
    if cantidad > producto.stock:
        messages.error(request, f'Solo hay {producto.stock} unidades disponibles de {producto.nombre}.')
    else:
        carrito.agregar(producto=producto, cantidad=cantidad)
        messages.success(request, f'{producto.nombre} añadido al carrito.')
        
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
        producto = get_object_or_404(Producto, id=producto_id)
        if cantidad > producto.stock:
            messages.error(request, f'Solo hay {producto.stock} unidades disponibles de {producto.nombre}.')
        else:
            carrito.actualizar(producto_id=producto_id, cantidad=cantidad)
            messages.success(request, f'Cantidad actualizada correctamente.')
            
    return redirect('ventas:carrito_detalle')

def eliminar_del_carrito(request, producto_id):
    carrito = Carrito(request)
    carrito.eliminar(producto_id=producto_id)
    messages.success(request, 'Producto eliminado del carrito.')
    return redirect('ventas:carrito_detalle')
