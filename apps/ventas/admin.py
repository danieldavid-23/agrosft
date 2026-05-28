from django.contrib import admin
# NOTA: Estos modelos apuntan a tablas que NO existen en la BD actual
# from .models import SolicitudCompra, DetalleSolicitudCompra, Venta, DetalleVenta, Movimiento, ProductoUsuarioMovimiento
from .models import Movimiento, ProductoUsuarioMovimiento

# @admin.register(SolicitudCompra)
# class SolicitudCompraAdmin(admin.ModelAdmin):
#     list_display = ['id', 'cliente_id', 'fecha_solicitud', 'estado', 'creado_por_id']
#     list_filter = ['estado', 'fecha_solicitud']
#     search_fields = ['cliente_id']
#     ordering = ['-fecha_solicitud']
#
#
# @admin.register(DetalleSolicitudCompra)
# class DetalleSolicitudCompraAdmin(admin.ModelAdmin):
#     list_display = ['id', 'solicitud_id', 'producto_id', 'cantidad', 'estado']
#     list_filter = ['estado']
#     search_fields = ['solicitud_id', 'producto_id']
#
#
# @admin.register(Venta)
# class VentaAdmin(admin.ModelAdmin):
#     list_display = ['id', 'cliente_id', 'fecha_venta', 'total', 'vendedor_id']
#     list_filter = ['fecha_venta']
#     search_fields = ['cliente_id', 'vendedor_id']
#     ordering = ['-fecha_venta']
#
#
# @admin.register(DetalleVenta)
# class DetalleVentaAdmin(admin.ModelAdmin):
#     list_display = ['id', 'venta_id', 'producto_id', 'cantidad', 'precio_unitario']
#     search_fields = ['venta_id', 'producto_id']


@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ['id_movimiento', 'id_tipo_movimiento', 'id_usuario']
    list_filter = ['id_tipo_movimiento']
    search_fields = ['id_usuario__nombres', 'id_usuario__apellidos']
    ordering = ['-id_movimiento']


@admin.register(ProductoUsuarioMovimiento)
class ProductoUsuarioMovimientoAdmin(admin.ModelAdmin):
    list_display = ['id_movimiento_usuario', 'id_producto_usuario', 'id_movimiento', 'cantidad', 'calificacion', 'fecha_movimiento']
    list_filter = ['fecha_movimiento', 'calificacion']
    search_fields = ['id_producto_usuario__id_producto__nombre', 'id_movimiento__descripcion']
    ordering = ['-fecha_movimiento']