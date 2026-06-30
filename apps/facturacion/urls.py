from django.urls import path
from apps.facturacion.controllers import factura_controller

app_name = 'facturacion'

urlpatterns = [
    path('seleccionar-pago/', factura_controller.seleccionar_pago, name='seleccionar_pago'),
    path('iniciar-pago/', factura_controller.iniciar_pago, name='iniciar_pago'),
    path('retorno/<str:gateway>/', factura_controller.retorno_pago, name='retorno_pago'),
    path('webhook/<str:gateway>/', factura_controller.webhook_pago, name='webhook_pago'),
    path('detalle/<int:factura_id>/', factura_controller.detalle_factura, name='detalle_factura'),
    path('historial/', factura_controller.historial_facturas, name='historial_facturas'),
]
