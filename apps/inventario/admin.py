from django.contrib import admin
from .models.producto import Producto, Categoria, ProductoUsuario, Estado
from apps.ventas.models.movimiento import TipoMovimiento


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['id_categoria', 'nombre', 'descripcion', 'activo', 'created_at']
    list_filter = ['activo', 'created_at']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']
    list_editable = ['activo']


@admin.register(TipoMovimiento)
class TipoMovimientoAdmin(admin.ModelAdmin):
    list_display = ['id_tipo_movimiento', 'tipo']
    search_fields = ['tipo']
    ordering = ['id_tipo_movimiento']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['id_producto', 'nombre', 'id_categoria', 'cantidad', 'stock_minimo', 'fecha_creacion', 'eliminado']
    list_filter = ['id_categoria', 'fecha_creacion', 'eliminado']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']
    list_per_page = 20


@admin.register(ProductoUsuario)
class ProductoUsuarioAdmin(admin.ModelAdmin):
    list_display = ['id_producto_usuario', 'id_producto', 'id_usuario', 'cantidad', 'precio', 'fecha_creacion']
    list_filter = ['fecha_creacion']
    search_fields = ['id_producto__nombre', 'id_usuario__nombres', 'id_usuario__apellidos']
    ordering = ['-fecha_creacion']
    list_per_page = 20