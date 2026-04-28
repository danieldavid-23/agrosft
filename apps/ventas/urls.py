from django.urls import path
from .controllers import venta_controller, solicitud_controller

app_name = 'ventas'

urlpatterns = [
    # Ventas
    path('', venta_controller.listar_ventas, name='venta_list'),
    path('<int:pk>/', venta_controller.detalle_venta, name='venta_detail'),
    path('crear/', venta_controller.crear_venta, name='venta_create'),
    
    # Solicitudes de Compra Combinadas
    path('solicitudes/', solicitud_controller.listar_solicitudes, name='solicitud_list'),
    path('solicitudes/crear/', solicitud_controller.crear_solicitud, name='solicitud_create'),
    path('solicitudes/<int:pk>/', solicitud_controller.detalle_solicitud, name='solicitud_detail'),
    path('solicitudes/<int:pk>/aceptar/', solicitud_controller.aceptar_solicitud, name='solicitud_aceptar'),
    path('solicitudes/<int:pk>/rechazar/', solicitud_controller.rechazar_solicitud, name='solicitud_rechazar'),
    path('solicitudes/<int:pk>/vendido/', solicitud_controller.marcar_vendido, name='solicitud_marcar_vendido'),
]
