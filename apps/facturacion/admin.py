from django.contrib import admin
from .models import MetodoPago, Factura, ItemFactura


@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'nombre', 'comision_porcentaje', 'estado', 'orden']
    list_filter = ['estado']
    search_fields = ['nombre', 'codigo']
    ordering = ['orden']
    list_editable = ['estado', 'orden']


@admin.register(Factura)
class FacturaAdmin(admin.ModelAdmin):
    list_display = ['id_factura', 'usuario', 'total', 'metodo_pago', 'estado', 'creada_en', 'pagada_en']
    list_filter = ['estado', 'creada_en', 'metodo_pago']
    search_fields = ['id_factura', 'usuario__correo', 'transaction_id']
    ordering = ['-creada_en']
    list_per_page = 20
    raw_id_fields = ['usuario', 'movimiento']


@admin.register(ItemFactura)
class ItemFacturaAdmin(admin.ModelAdmin):
    list_display = ['id_item', 'factura', 'producto', 'cantidad', 'precio_unitario', 'subtotal']
    search_fields = ['factura__id_factura', 'descripcion']
    ordering = ['factura', 'id_item']
    list_per_page = 20
