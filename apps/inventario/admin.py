from django.contrib import admin
from .models.producto import Producto, Categoria, ProductoUsuario, Estado, TipoMovimiento, Calificacion


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['id_categoria', 'nombre', 'descripcion', 'activo', 'created_at']
    list_filter = ['activo', 'created_at']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']
    list_editable = ['activo']


@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ['id_estado', 'estado']
    search_fields = ['estado']
    ordering = ['id_estado']


@admin.register(TipoMovimiento)
class TipoMovimientoAdmin(admin.ModelAdmin):
    list_display = ['id_tipo_movimiento', 'tipo']
    search_fields = ['tipo']
    ordering = ['id_tipo_movimiento']


@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ['id_calificacion', 'calificacion']
    ordering = ['id_calificacion']


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['id_producto', 'nombre', 'id_categoria', 'cantidad', 'stock_minimo', 'estado', 'fecha_creacion', 'eliminado']
    list_filter = ['estado', 'id_categoria', 'fecha_creacion', 'eliminado']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']
    list_per_page = 20


@admin.register(ProductoUsuario)
class ProductoUsuarioAdmin(admin.ModelAdmin):
    list_display = ['id_producto_usuario', 'id_producto', 'id_usuario', 'cantidad', 'precio', 'calificacion_promedio', 'id_estado', 'fecha_creacion']
    list_filter = ['id_estado', 'fecha_creacion']
    search_fields = ['id_producto__nombre', 'id_usuario__nombres', 'id_usuario__apellidos']
    ordering = ['-fecha_creacion']
    list_per_page = 20