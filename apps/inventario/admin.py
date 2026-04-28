from django.contrib import admin
from .models import Categoria, Producto, HistorialProducto

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'activo', 'created_at']
    search_fields = ['nombre']
    list_filter = ['activo']

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'categoria', 'precio', 'stock', 'estado', 'agricultor_id', 'created_at']
    list_filter = ['estado', 'categoria', 'eliminado']
    search_fields = ['nombre', 'descripcion']
    actions = ['aprobar_productos', 'rechazar_productos']
    
    def aprobar_productos(self, request, queryset):
        queryset.update(estado='aprobado')
    aprobar_productos.short_description = "Aprobar productos seleccionados"
    
    def rechazar_productos(self, request, queryset):
        queryset.update(estado='rechazado')
    rechazar_productos.short_description = "Rechazar productos seleccionados"

@admin.register(HistorialProducto)
class HistorialProductoAdmin(admin.ModelAdmin):
    list_display = ['producto_id', 'accion', 'usuario_id', 'fecha']
    list_filter = ['accion']
    readonly_fields = ['fecha']