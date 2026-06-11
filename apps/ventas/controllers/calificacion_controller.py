from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.urls import reverse
from apps.ventas.models.movimiento import ProductoUsuarioMovimiento, Movimiento
from apps.ventas.forms.calificacion_form import CalificacionForm
import json
import logging

logger = logging.getLogger(__name__)


@login_required
def calificar_transaccion(request, movimiento_id):
    """
    Vista para que un usuario califique una transacción de compra/venta
    """
    movimiento_detalle = get_object_or_404(
        ProductoUsuarioMovimiento,
        id_movimiento_usuario=movimiento_id
    )
    
    # Verificar que el usuario participe en esta transacción
    movimiento = movimiento_detalle.id_movimiento
    if movimiento.id_usuario != request.user:
        messages.error(request, 'No puedes calificar esta transacción.')
        return redirect('inventario:listar')
    
    # Verificar que aún no haya sido calificado
    if movimiento_detalle.calificacion is not None:
        messages.info(request, 'Ya has calificado esta transacción.')
        return redirect('inventario:listar')
    
    if request.method == 'POST':
        form = CalificacionForm(request.POST, instance=movimiento_detalle)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    logger.info(
                        f"User {request.user.pk} rated transaction {movimiento_id} "
                        f"with {form.cleaned_data['calificacion']}"
                    )
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': True, 'calificacion': form.cleaned_data['calificacion']})
                    messages.success(request, '¡Calificación enviada exitosamente!')
                    return redirect('ventas:historial_movimientos')
            except Exception as e:
                logger.error(
                    f"Error rating transaction {movimiento_id} by user {request.user.pk}: {str(e)}",
                    exc_info=True
                )
                msg = 'Error al enviar la calificación. Intente nuevamente.'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': msg})
                messages.error(request, msg)
        else:
            errors = form.errors.get_json_data()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(errors)})
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        form = CalificacionForm(instance=movimiento_detalle)
    
    movimiento_data = {
        'movimientoDetalle': {
            'id': movimiento_detalle.id_movimiento_usuario,
            'producto_nombre': movimiento_detalle.id_producto_usuario.id_producto.nombre,
            'cantidad': float(abs(movimiento_detalle.cantidad)),
            'fecha': movimiento_detalle.fecha_movimiento.strftime('%d/%m/%Y %H:%M') if movimiento_detalle.fecha_movimiento else 'N/A',
            'tipo': movimiento_detalle.id_movimiento.id_tipo_movimiento.tipo,
            'calificacion': float(movimiento_detalle.calificacion) if movimiento_detalle.calificacion else None,
        },
        'urls': {
            'calificar': reverse('ventas:calificar_transaccion', args=[movimiento_id]),
            'historial': reverse('ventas:historial_movimientos'),
        }
    }

    return render(request, 'ventas/calificaciones/calificar.html', {
        'form': form,
        'movimiento_detalle': movimiento_detalle,
        'calificaciones_json': json.dumps(movimiento_data),
    })


@login_required
def historial_movimientos(request):
    """
    Vista para ver el historial de movimientos del usuario
    """
    movimientos = ProductoUsuarioMovimiento.objects.select_related(
        'id_producto_usuario',
        'id_producto_usuario__id_producto',
        'id_producto_usuario__id_usuario',
        'id_movimiento'
    ).filter(
        id_movimiento__id_usuario=request.user
    ).order_by('-fecha_movimiento')
    
    return render(request, 'ventas/calificaciones/historial.html', {
        'movimientos': movimientos
    })
