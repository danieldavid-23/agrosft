from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from ..models import SolicitudCompra, Venta, DetalleVenta
from ..forms.solicitud_form import SolicitudCompraForm, DetalleSolicitudFormSet

@login_required
def listar_solicitudes(request):
    solicitudes = SolicitudCompra.objects.all().order_by('-fecha_solicitud')
    return render(request, 'ventas/solicitudes/solicitud_list.html', {'solicitudes': solicitudes})

@login_required
def crear_solicitud(request):
    if request.method == 'POST':
        form = SolicitudCompraForm(request.POST)
        formset = DetalleSolicitudFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    solicitud = form.save(commit=False)
                    solicitud.creado_por = request.user
                    solicitud.save()
                    
                    formset.instance = solicitud
                    formset.save()
                    
                    messages.success(request, 'Solicitud de compra creada exitosamente.')
                    return redirect('ventas:solicitud_list')
            except Exception as e:
                messages.error(request, f'Error al crear la solicitud: {str(e)}')
        else:
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = SolicitudCompraForm()
        formset = DetalleSolicitudFormSet()
        
    return render(request, 'ventas/solicitudes/solicitud_form.html', {
        'form': form,
        'formset': formset
    })

@login_required
def detalle_solicitud(request, pk):
    solicitud = get_object_or_404(SolicitudCompra, pk=pk)
    return render(request, 'ventas/solicitudes/solicitud_detail.html', {'solicitud': solicitud})

@login_required
def aceptar_solicitud(request, pk):
    solicitud = get_object_or_404(SolicitudCompra, pk=pk)
    
    # Verificar que el usuario sea agricultor
    is_agricultor = False
    try:
        if request.user.userprofile.rol == 'agricultor':
            is_agricultor = True
    except Exception:
        pass
        
    if not is_agricultor:
        messages.error(request, 'Solo los agricultores pueden aceptar solicitudes.')
        return redirect('ventas:solicitud_detail', pk=pk)
    
    if request.method == 'POST':
        if solicitud.estado != 'pendiente':
            messages.warning(request, 'Solo se pueden aceptar solicitudes pendientes.')
            return redirect('ventas:solicitud_detail', pk=pk)
            
        try:
            with transaction.atomic():
                # Actualizar estado
                solicitud.estado = 'aceptada'
                solicitud.save()
                
                # Crear venta
                venta = Venta.objects.create(
                    cliente=solicitud.cliente,
                    total=solicitud.total_estimado(),
                    vendedor=request.user
                )
                
                # Crear detalles de venta
                for detalle_solicitud in solicitud.detalles.all():
                    DetalleVenta.objects.create(
                        venta=venta,
                        producto=detalle_solicitud.producto,
                        cantidad=detalle_solicitud.cantidad,
                        precio_unitario=detalle_solicitud.producto.precio
                    )
                    
                    # Actualizar stock
                    producto = detalle_solicitud.producto
                    if producto.stock < detalle_solicitud.cantidad:
                        raise ValueError(f"No hay stock suficiente para '{producto.nombre}'. Stock actual: {producto.stock}, Solicitado: {detalle_solicitud.cantidad}")
                    producto.stock -= detalle_solicitud.cantidad
                    producto.save()
                
                messages.success(request, 'Solicitud aceptada y venta generada exitosamente.')
                return redirect('ventas:venta_detail', pk=venta.pk)
        except Exception as e:
            messages.error(request, f'Error al aceptar solicitud: {str(e)}')
            
    return redirect('ventas:solicitud_detail', pk=pk)

@login_required
def rechazar_solicitud(request, pk):
    solicitud = get_object_or_404(SolicitudCompra, pk=pk)
    
    # Verificar que el usuario sea agricultor
    is_agricultor = False
    try:
        if request.user.userprofile.rol == 'agricultor':
            is_agricultor = True
    except Exception:
        pass
        
    if not is_agricultor:
        messages.error(request, 'Solo los agricultores pueden rechazar solicitudes.')
        return redirect('ventas:solicitud_detail', pk=pk)
        
    if request.method == 'POST':
        solicitud.estado = 'rechazada'
        solicitud.save()
        messages.success(request, 'Solicitud rechazada.')
    return redirect('ventas:solicitud_detail', pk=pk)

@login_required
def marcar_vendido(request, pk):
    solicitud = get_object_or_404(SolicitudCompra, pk=pk)
    
    # Verificar que el usuario sea agricultor
    is_agricultor = False
    try:
        if request.user.userprofile.rol == 'agricultor':
            is_agricultor = True
    except Exception:
        pass
        
    if not is_agricultor:
        messages.error(request, 'Solo los agricultores pueden marcar solicitudes como vendidas.')
        return redirect('ventas:solicitud_detail', pk=pk)
    
    if request.method == 'POST':
        if solicitud.estado in ['vendido', 'rechazada']:
            messages.warning(request, 'No se puede cambiar el estado de esta solicitud.')
            return redirect('ventas:solicitud_detail', pk=pk)
            
        try:
            with transaction.atomic():
                solicitud.estado = 'vendido'
                solicitud.save()
                messages.success(request, 'Solicitud marcada como Vendida.')
                return redirect('ventas:solicitud_detail', pk=pk)
        except Exception as e:
            messages.error(request, f'Error al actualizar estado: {str(e)}')
            
    return redirect('ventas:solicitud_detail', pk=pk)
