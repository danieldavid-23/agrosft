from django.db import models
from apps.usuarios.models.profile_model import Tblusuarios


class TipoMovimiento(models.Model):
    """
    Modelo que representa la tabla tipo_movimiento en la base de datos
    Define los tipos de movimiento: 'compra' (abastecimiento) y 'venta' (producto vendido)
    NOTA: Este modelo está duplicado en inventario.models. Considerar usar uno solo.
    """
    id_tipo_movimiento = models.AutoField(primary_key=True, db_column='id_tipo_movimiento')
    tipo = models.CharField(max_length=45, db_column='tipo_movimiento')

    class Meta:
        db_table = 'tipo_movimiento'
        managed = False
        verbose_name = 'Tipo de Movimiento'
        verbose_name_plural = 'Tipos de Movimiento'

    def __str__(self):
        return self.tipo


class Movimiento(models.Model):
    """
    Modelo que representa la tabla movimiento en la base de datos
    Registra cada acción de compra o venta realizada por un usuario.
    
    NOTA IMPORTANTE:
    - Esta tabla NO tiene campos fecha_movimiento ni descripcion
    - La fecha está en tblproductos_has_tblusuarios_has_movimiento.fecha_movimiento
    - Un movimiento puede tener múltiples productos (detalles)
    """
    id_movimiento = models.AutoField(primary_key=True, db_column='id_movimiento')
    
    # Relaciones según la estructura real de la BD
    id_tipo_movimiento = models.ForeignKey(
        TipoMovimiento,
        on_delete=models.CASCADE,
        db_column='tipo_movimiento_id_tipo_movimiento',
        related_name='movimientos'
    )
    id_usuario = models.ForeignKey(
        Tblusuarios,
        on_delete=models.CASCADE,
        db_column='tblusuarios_id_users',
        related_name='movimientos'
    )

    class Meta:
        db_table = 'movimiento'
        managed = False
        verbose_name = 'Movimiento'
        verbose_name_plural = 'Movimientos'

    def __str__(self):
        return f"Movimiento #{self.id_movimiento} - {self.id_tipo_movimiento.tipo} - {self.id_usuario.get_full_name()}"
    
    def obtener_fecha(self):
        """
        Obtiene la fecha del movimiento desde el primer detalle asociado.
        La fecha está en la tabla de detalles, no en esta tabla.
        """
        primer_detalle = self.productousuariomovimiento_set.first()
        if primer_detalle:
            return primer_detalle.fecha_movimiento
        return None
    
    def obtener_total(self):
        """Calcula el total del movimiento sumando los subtotales de los detalles"""
        return sum(detalle.cantidad * detalle.id_producto_usuario.precio for detalle in self.productousuariomovimiento_set.all())
    
    def obtener_detalles(self):
        """Retorna todos los detalles del movimiento con información del producto"""
        return self.productousuariomovimiento_set.select_related(
            'id_producto_usuario',
            'id_producto_usuario__id_producto',
            'id_producto_usuario__id_usuario'
        ).all()


class ProductoUsuarioMovimiento(models.Model):
    """
    Modelo que representa la tabla tblproductos_has_tblusuarios_has_movimiento en la base de datos
    Tabla de detalles que vincula el movimiento con la publicación concreta (ProductoUsuario).
    
    Esta tabla es clave porque:
    - Registra qué producto de qué vendedor se está comprando/vendiendo
    - Almacena la cantidad movida (positiva=abastecimiento, negativa=venta)
    - Contiene la fecha del movimiento (fecha_movimiento)
    - Permite calificar cada transacción individualmente
    - Los triggers actualizan automáticamente el stock y calificación_promedio
    """
    id_movimiento_usuario = models.AutoField(
        primary_key=True, 
        db_column='id_movimiento_usuario'
    )
    id_producto_usuario = models.ForeignKey(
        'inventario.ProductoUsuario',
        on_delete=models.CASCADE,
        db_column='tblproductos_has_tblusuarios_id_pd_us',
        related_name='movimientos_detalle'
    )
    id_movimiento = models.ForeignKey(
        Movimiento,
        on_delete=models.CASCADE,
        db_column='movimiento_id_movimiento',
        related_name='detalles'
    )
    cantidad = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        db_column='cantidad',
        help_text='Cantidad movida (positiva=entrada/abastecimiento, negativa=salida/venta)'
    )
    calificacion = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        null=True, 
        blank=True,
        db_column='calificacion',
        help_text='Calificación de 1.0 a 5.0 en pasos de 0.5'
    )
    fecha_movimiento = models.DateTimeField(
        auto_now_add=True,
        db_column='fecha_movimiento',
        verbose_name='Fecha del movimiento'
    )

    class Meta:
        db_table = 'tblproductos_has_tblusuarios_has_movimiento'
        managed = False
        verbose_name = 'Detalle de Movimiento'
        verbose_name_plural = 'Detalles de Movimiento'

    def __str__(self):
        return f"Detalle #{self.id_movimiento_usuario} - {self.id_producto_usuario.id_producto.nombre} - Cantidad: {self.cantidad}"
    
    def obtener_subtotal(self):
        """Calcula el subtotal de este detalle"""
        return self.cantidad * self.id_producto_usuario.precio
    
    def obtener_vendedor(self):
        """Retorna el usuario vendedor de este producto"""
        return self.id_producto_usuario.id_usuario
    
    def es_venta(self):
        """Determina si este movimiento es una venta (stock negativo)"""
        return self.cantidad < 0
    
    def es_abastecimiento(self):
        """Determina si este movimiento es un abastecimiento (stock positivo)"""
        return self.cantidad > 0