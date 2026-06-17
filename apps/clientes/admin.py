from django.contrib import admin
from .models.cliente import Cliente


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre_completo', 'usuario', 'telefono', 'fecha_registro']
    list_filter = ['fecha_registro']
    search_fields = ['nombre_completo', 'telefono', 'usuario__correo']
    ordering = ['-fecha_registro']
    list_per_page = 20
    raw_id_fields = ['usuario']
