from django.urls import path
from .controllers import venta_controller, solicitud_controller, carrito_controller, calificacion_controller

app_name = 'ventas'

urlpatterns = [
    # Carrito de Compras
    path('carrito/', carrito_controller.detalle_carrito, name='carrito_detalle'),
    path('carrito/agregar/<int:producto_id>/', carrito_controller.agregar_al_carrito, name='carrito_agregar'),
    path('carrito/actualizar/<int:producto_id>/', carrito_controller.actualizar_carrito, name='carrito_actualizar'),
    path('carrito/eliminar/<int:producto_id>/', carrito_controller.eliminar_del_carrito, name='carrito_eliminar'),
    path('carrito/checkout/', carrito_controller.checkout_carrito, name='carrito_checkout'),
    path('carrito/checkout-venta/', carrito_controller.checkout_venta_carrito, name='carrito_checkout_venta'),

    # Ventas
    path('', venta_controller.listar_ventas, name='venta_list'),
    path('<int:pk>/', venta_controller.detalle_venta, name='venta_detail'),
    path('crear/', venta_controller.crear_venta, name='venta_create'),
    path('<int:pk>/marcar-vendida/', venta_controller.marcar_como_vendida, name='venta_marcar_vendida'),
    
    # Solicitudes de Compra Combinadas
    path('solicitudes/', solicitud_controller.listar_solicitudes, name='solicitud_list'),
    path('solicitudes/crear/', solicitud_controller.crear_solicitud, name='solicitud_create'),
    path('solicitudes/<int:pk>/', solicitud_controller.detalle_solicitud, name='solicitud_detail'),
    path('solicitudes/<int:pk>/aceptar/', solicitud_controller.aceptar_solicitud, name='solicitud_aceptar'),
    path('solicitudes/<int:pk>/rechazar/', solicitud_controller.rechazar_solicitud, name='solicitud_rechazar'),
    path('solicitudes/<int:pk>/vendido/', solicitud_controller.marcar_vendido, name='solicitud_marcar_vendido'),
    path('solicitudes/<int:pk>/detalle/<int:detalle_id>/<str:estado>/', solicitud_controller.estado_detalle, name='solicitud_estado_detalle'),
    
    # Calificaciones
    path('calificaciones/calificar/<int:movimiento_id>/', calificacion_controller.calificar_transaccion, name='calificar_transaccion'),
    path('calificaciones/historial/', calificacion_controller.historial_movimientos, name='historial_movimientos'),
]
