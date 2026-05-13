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


from django.db import transaction
from apps.ventas.forms.solicitud_form import CheckoutSolicitudForm
from apps.clientes.models import Cliente
from apps.ventas.models.solicitud import DetalleSolicitudCompra

def checkout_carrito(request):
    carrito = Carrito(request)
    if len(carrito) == 0:
        messages.error(request, 'No puedes procesar un carrito vacío.')
        return redirect('ventas:carrito_detalle')

    if request.method == 'POST':
        form = CheckoutSolicitudForm(request.POST)
        if form.is_valid():
            try:
                items = list(carrito)
                with transaction.atomic():
                    solicitud = form.save(commit=False)
                    
                    # Auto-assign or create client for current user
                    cliente, created = Cliente.objects.get_or_create(
                        user=request.user,
                        defaults={'nombre_completo': request.user.get_full_name() or request.user.username}
                    )
                    solicitud.cliente = cliente
                    solicitud.creado_por = request.user if request.user.is_authenticated else None
                    solicitud.save()

                    for item in items:
                        DetalleSolicitudCompra.objects.create(
                            solicitud=solicitud,
                            producto=item['producto'],
                            cantidad=item['cantidad']
                        )

                    carrito.limpiar()
                    messages.success(request, '¡Pedido (Solicitud de Compra) realizado exitosamente!')
                    return redirect('ventas:solicitud_detail', pk=solicitud.pk)
            except Exception as e:
                messages.error(request, f'Error al procesar el pedido: {str(e)}')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = CheckoutSolicitudForm()

    return render(request, 'ventas/carrito/checkout.html', {
        'form': form,
        'carrito': carrito
    })

from apps.ventas.models.venta import Venta, DetalleVenta
from apps.ventas.forms.venta_form import CheckoutVentaForm

def checkout_venta_carrito(request):
    carrito = Carrito(request)
    if len(carrito) == 0:
        messages.error(request, 'No puedes procesar un carrito vacío.')
        return redirect('ventas:carrito_detalle')

    if request.method == 'POST':
        form = CheckoutVentaForm(request.POST)
        if form.is_valid():
            try:
                items = list(carrito)
                with transaction.atomic():
                    # Verificar stock primero
                    for item in items:
                        producto = item['producto']
                        if producto.stock < item['cantidad']:
                            raise ValueError(f"No hay stock suficiente para '{producto.nombre}'. Stock actual: {producto.stock}, Solicitado: {item['cantidad']}")

                    venta = form.save(commit=False)
                    
                    # Auto-assign or create client for current user
                    cliente, created = Cliente.objects.get_or_create(
                        user=request.user,
                        defaults={'nombre_completo': request.user.get_full_name() or request.user.username}
                    )
                    venta.cliente = cliente
                    venta.total = carrito.get_total_precio()
                    venta.vendedor = request.user if request.user.is_authenticated else None
                    venta.save()

                    for item in items:
                        producto = item['producto']
                        DetalleVenta.objects.create(
                            venta=venta,
                            producto=producto,
                            cantidad=item['cantidad'],
                            precio_unitario=producto.precio
                        )
                        # Actualizar stock
                        producto.stock -= item['cantidad']
                        producto.save()

                    carrito.limpiar()
                    messages.success(request, '¡Venta directa registrada exitosamente!')
                    return redirect('ventas:venta_detail', pk=venta.pk)
            except ValueError as e:
                messages.error(request, str(e))
            except Exception as e:
                messages.error(request, f'Error al procesar la venta: {str(e)}')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = CheckoutVentaForm()

    return render(request, 'ventas/carrito/checkout_venta.html', {
        'form': form,
        'carrito': carrito
    })
