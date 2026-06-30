from django.urls import path
from apps.facturacion.controllers import factura_controller

app_name = 'facturacion'

urlpatterns = [
    path('crear/', factura_controller.crear_factura, name='crear_factura'),
    path('detalle/<int:factura_id>/', factura_controller.detalle_factura, name='detalle_factura'),
    path('historial/', factura_controller.historial_facturas, name='historial_facturas'),
]
