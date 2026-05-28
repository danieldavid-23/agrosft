from django.contrib import admin
from .models import Producto, Categoria, ProductoUsuario

# 原Tblcategoria模型已替换为Categoria

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['id_producto', 'nombre', 'id_categoria', 'cantidad', 'fecha_creacion', 'estado']
    list_filter = ['estado', 'id_categoria', 'fecha_creacion']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']

# Este modelo ya está cubierto por el ProductoAdmin anterior

@admin.register(ProductoUsuario)
class ProductoUsuarioAdmin(admin.ModelAdmin):
    list_display = ['id_producto_usuario', 'id_producto', 'id_usuario', 'cantidad', 'precio', 'id_estado', 'fecha_creacion']
    list_filter = ['id_estado', 'fecha_creacion']
    search_fields = ['id_producto__nombre', 'id_usuario__nombres', 'id_usuario__apellidos']
    ordering = ['-fecha_creacion']