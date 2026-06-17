from django.contrib import admin
from .models.profile_model import Tblusuarios, UserProfile


@admin.register(Tblusuarios)
class TblusuariosAdmin(admin.ModelAdmin):
    list_display = ['id_users', 'nombres', 'apellidos', 'correo', 'telefono', 'is_active', 'is_staff', 'fecha_creacion']
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'fecha_creacion']
    search_fields = ['correo', 'nombres', 'apellidos']
    ordering = ['nombres', 'apellidos']
    list_per_page = 20
    list_editable = ['is_active']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id_perfil', 'id_usuario', 'telefono_contacto', 'idioma_preferido', 'zona_horaria', 'notificaciones_activas', 'fecha_creacion']
    list_filter = ['idioma_preferido', 'notificaciones_activas', 'fecha_creacion']
    search_fields = ['id_usuario', 'telefono_contacto']
    ordering = ['-fecha_creacion']
    list_per_page = 20