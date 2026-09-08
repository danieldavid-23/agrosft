from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.urls import reverse
from apps.ventas.models.movimiento import ProductoUsuarioMovimiento
from apps.ventas.models.resena import Resena
from apps.ventas.forms.resena_form import ResenaForm
import logging

logger = logging.getLogger(__name__)


@login_required
def calificar_transaccion(request, movimiento_id):
    """
    Vista para que un comprador deje una reseña (estrellas + comentario)
    sobre un producto que compró.
    """
    movimiento_detalle = get_object_or_404(
        ProductoUsuarioMovimiento,
        id_movimiento_usuario=movimiento_id
    )

    movimiento = movimiento_detalle.id_movimiento
    producto_usuario = movimiento_detalle.id_producto_usuario

    if movimiento.id_usuario != request.user:
        messages.error(request, 'No puedes calificar esta transacción.')
        return redirect('inventario:listar')

    resena_existente = Resena.objects.filter(
        id_movimiento_usuario=movimiento_detalle
    ).first()

    if resena_existente:
        messages.info(request, 'Ya has dejado una reseña para esta transacción.')
        return redirect('ventas:historial_movimientos')

    if request.method == 'POST':
        form = ResenaForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    resena = form.save(commit=False)
                    resena.id_movimiento_usuario = movimiento_detalle
                    resena.id_producto_usuario = producto_usuario
                    resena.id_usuario = request.user
                    resena.save()

                    movimiento_detalle.calificacion = form.cleaned_data['calificacion']
                    movimiento_detalle.save(update_fields=['calificacion'])

                    logger.info(
                        f"User {request.user.pk} left a review ({form.cleaned_data['calificacion']}★) "
                        f"on transaction {movimiento_id}"
                    )
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'success': True,
                            'calificacion': form.cleaned_data['calificacion'],
                            'comentario': resena.comentario,
                        })
                    messages.success(request, '¡Reseña enviada exitosamente!')
                    return redirect('ventas:historial_movimientos')
            except Exception as e:
                logger.error(
                    f"Error saving review for transaction {movimiento_id} by user {request.user.pk}: {str(e)}",
                    exc_info=True
                )
                msg = 'Error al enviar la reseña. Intente nuevamente.'
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'error': msg})
                messages.error(request, msg)
        else:
            errors = form.errors.get_json_data()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(errors)})
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = ResenaForm(initial={'calificacion': 5})

    movimiento_data = {
        'movimientoDetalle': {
            'id': movimiento_detalle.id_movimiento_usuario,
            'producto_nombre': producto_usuario.id_producto.nombre,
            'cantidad': float(abs(movimiento_detalle.cantidad)),
            'fecha': movimiento_detalle.fecha_movimiento.strftime('%d/%m/%Y %H:%M') if movimiento_detalle.fecha_movimiento else 'N/A',
            'tipo': movimiento.id_tipo_movimiento.tipo,
            'imagen': producto_usuario.id_producto.imagen.url if producto_usuario.id_producto.imagen else None,
        },
        'urls': {
            'calificar': reverse('ventas:calificar_transaccion', args=[movimiento_id]),
            'historial': reverse('ventas:historial_movimientos'),
        }
    }

    return render(request, 'ventas/calificaciones/calificar.html', {
        'form': form,
        'movimiento_detalle': movimiento_detalle,
        'calificaciones_json': movimiento_data,
    })


@login_required
def historial_movimientos(request):
    """
    Vista para ver el historial de movimientos del usuario con sus reseñas.
    """
    movimientos = ProductoUsuarioMovimiento.objects.select_related(
        'id_producto_usuario__id_producto',
        'id_movimiento__id_tipo_movimiento',
    ).filter(
        id_movimiento__id_usuario=request.user
    ).prefetch_related('resena').order_by('-fecha_movimiento')

    return render(request, 'ventas/calificaciones/historial.html', {
        'movimientos': movimientos
    })


def listar_resenas_producto(producto_usuario_id):
    """
    Retorna las reseñas de un producto específico (publicación), ordenadas
    de la más reciente a la más antigua. Helper reutilizable.
    """
    return Resena.objects.select_related(
        'id_usuario'
    ).filter(
        id_producto_usuario_id=producto_usuario_id
    ).order_by('-fecha_creacion')