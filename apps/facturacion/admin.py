from django.contrib import admin
from .models import Factura, ItemFactura


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ['id_factura', 'usuario', 'total', 'estado', 'creada_en']
    list_filter = ['estado', 'creada_en']
    search_fields = ['id_factura', 'usuario__correo']
    ordering = ['-creada_en']
    list_per_page = 20
    raw_id_fields = ['usuario', 'movimiento']


@admin.register(ItemFactura)
class ItemFacturaAdmin(admin.ModelAdmin):
    list_display = ['id_item', 'factura', 'producto', 'cantidad', 'precio_unitario', 'subtotal']
    search_fields = ['factura__id_factura', 'descripcion']
    ordering = ['factura', 'id_item']
    list_per_page = 20
