from django.contrib import admin
from django.utils.html import format_html
from .models.movimiento import Movimiento, ProductoUsuarioMovimiento


@admin.register(Movimiento)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ['id_movimiento', 'id_tipo_movimiento', 'id_usuario', 'obtener_fecha', 'obtener_total_display']
    list_filter = ['id_tipo_movimiento']
    search_fields = ['id_usuario__nombres', 'id_usuario__apellidos', 'id_usuario__correo']
    ordering = ['-id_movimiento']
    list_per_page = 20
    raw_id_fields = ['id_usuario', 'id_tipo_movimiento']

    def obtener_fecha(self, obj):
        fecha = obj.obtener_fecha()
        return fecha.strftime('%d/%m/%Y %H:%M') if fecha else '-'
    obtener_fecha.short_description = 'Fecha'
    obtener_fecha.admin_order_field = 'id_movimiento'

    def obtener_total_display(self, obj):
        try:
            total = obj.obtener_total()
            return f'${total:,.2f}'
        except Exception:
            return '-'
    obtener_total_display.short_description = 'Total'


@admin.register(ProductoUsuarioMovimiento)
class ProductoUsuarioMovimientoAdmin(admin.ModelAdmin):
    list_display = ['id_movimiento_usuario', 'id_producto_usuario', 'id_movimiento', 'cantidad_display', 'calificacion_display', 'fecha_movimiento']
    list_filter = ['fecha_movimiento', 'calificacion']
    search_fields = ['id_producto_usuario__id_producto__nombre', 'id_movimiento__id_usuario__nombres']
    ordering = ['-fecha_movimiento']
    list_per_page = 20
    raw_id_fields = ['id_producto_usuario', 'id_movimiento']

    def cantidad_display(self, obj):
        color = '#dc2626' if obj.cantidad < 0 else '#059669'
        return format_html('<span style="color: {}; font-weight: bold;">{}</span>', color, obj.cantidad)
    cantidad_display.short_description = 'Cantidad'

    def calificacion_display(self, obj):
        if obj.calificacion:
            estrellas = '★' * int(obj.calificacion) + '☆' * (5 - int(obj.calificacion))
            return f'{estrellas} ({obj.calificacion})'
        return '-'
    calificacion_display.short_description = 'Calificación'