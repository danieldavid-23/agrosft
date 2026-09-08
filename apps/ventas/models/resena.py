from django.db import models
from apps.usuarios.models.profile_model import Tblusuarios
from apps.inventario.models.producto import ProductoUsuario
from apps.ventas.models.movimiento import ProductoUsuarioMovimiento


class Resena(models.Model):
    """
    Modelo que representa la tabla resena en la base de datos.
    Almacena la reseña (calificación en estrellas + comentario) que un comprador
    deja sobre un producto después de haberlo comprado.
    """
    id_resena = models.AutoField(primary_key=True, db_column='id_resena')
    id_movimiento_usuario = models.OneToOneField(
        ProductoUsuarioMovimiento,
        on_delete=models.CASCADE,
        db_column='id_movimiento_usuario',
        related_name='resena'
    )
    id_producto_usuario = models.ForeignKey(
        ProductoUsuario,
        on_delete=models.CASCADE,
        db_column='tblproductos_has_tblusuarios_id_pd_us',
        related_name='resenas'
    )
    id_usuario = models.ForeignKey(
        Tblusuarios,
        on_delete=models.CASCADE,
        db_column='tblusuarios_id_users',
        related_name='resenas'
    )
    calificacion = models.PositiveSmallIntegerField(
        db_column='calificacion',
        help_text='Calificación de 1 a 5 estrellas'
    )
    comentario = models.TextField(
        null=True,
        blank=True,
        db_column='comentario',
        help_text='Comentario del comprador'
    )
    fecha_creacion = models.DateTimeField(
        auto_now_add=True,
        db_column='fecha_creacion'
    )

    class Meta:
        db_table = 'resena'
        managed = False
        verbose_name = 'Reseña'
        verbose_name_plural = 'Reseñas'
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Reseña de {self.id_usuario.get_full_name()} - {self.calificacion}★"