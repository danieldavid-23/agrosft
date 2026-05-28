from django.contrib import admin
from .models.profile_model import Tblusuarios, UserProfile


@admin.register(Tblusuarios)
class TblusuariosAdmin(admin.ModelAdmin):
    list_display = ['id_users', 'nombres', 'apellidos', 'correo', 'is_active', 'fecha_creacion']
    list_filter = ['is_active', 'is_staff', 'fecha_creacion']
    search_fields = ['correo', 'nombres', 'apellidos']
    ordering = ['nombres', 'apellidos']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['id_usuario', 'telefono_contacto', 'fecha_creacion']
    list_filter = ['fecha_creacion']
    ordering = ['-fecha_creacion']