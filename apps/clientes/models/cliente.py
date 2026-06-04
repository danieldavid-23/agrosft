from django.db import models
from apps.usuarios.models.profile_model import Tblusuarios


class Cliente(models.Model):
    usuario = models.OneToOneField(Tblusuarios, on_delete=models.CASCADE, db_column='usuario_id')
    nombre_completo = models.CharField(max_length=200)
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'clientes'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.nombre_completo