from django.urls import path
from apps.facturacion.controllers import factura_controller

app_name = 'facturacion'

urlpatterns = [
    # Crear N facturas desde el carrito (una por vendedor)
    path('crear/', factura_controller.crear_factura, name='crear_factura'),
    # Detalle de una factura específica
    path('detalle/<int:factura_id>/', factura_controller.detalle_factura, name='detalle_factura'),
    # Historial de facturas del comprador
    path('historial/', factura_controller.historial_facturas, name='historial_facturas'),
    # PDF de una factura
    path('pdf/<int:factura_id>/', factura_controller.generar_pdf_factura, name='generar_pdf'),
    # Resumen de todas las facturas de un pedido (movimiento)
    path('pedido/<int:movimiento_id>/', factura_controller.facturas_pedido, name='facturas_pedido'),
    # Generar/recuperar facturas de un movimiento existente (flujo solicitudes/ventas)
    path('generar_pedido/<int:movimiento_id>/', factura_controller.generar_factura_pedido, name='generar_factura_pedido'),
]
