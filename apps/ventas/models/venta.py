"""
NOTA IMPORTANTE: Este módulo está OBSOLETO

Las ventas se manejan usando las tablas existentes:
- movimiento (como header de la venta)
- tblproductos_has_tblusuarios_has_movimiento (como detalles)
- tipo_movimiento (filtrando por tipo='venta')

Estos modelos se mantienen SOLO para compatibilidad con código legacy.
NO se deben usar en nuevo código.

Para implementar ventas, usar:
- apps.ventas.models.movimiento.Movimiento
- apps.ventas.models.movimiento.ProductoUsuarioMovimiento
"""
from django.db import models


class Venta(models.Model):
    """
    MODELO OBSOLETO - NO USAR
    
    Este modelo NO tiene una tabla real en la base de datos.
    Las ventas se implementan usando el modelo Movimiento
    con tipo_movimiento.tipo='venta'.
    
    Ver: apps.ventas.models.movimiento.Movimiento
    """
    cliente_id = models.IntegerField(help_text="ID del cliente en la tabla externa")
    fecha_venta = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    vendedor_id = models.IntegerField(help_text="ID del vendedor en la tabla externa")
    
    class Meta:
        db_table = 'ventas_venta'  # Tabla que NO existe en la BD
        managed = False
        verbose_name = 'Venta (OBSOLETO)'
        verbose_name_plural = 'Ventas (OBSOLETO)'

    def __str__(self):
        return f"Venta {self.id} - Cliente ID: {self.cliente_id} - OBSOLETO"


class DetalleVenta(models.Model):
    """
    MODELO OBSOLETO - NO USAR
    
    Este modelo NO tiene una tabla real en la base de datos.
    Los detalles de ventas se implementan usando ProductoUsuarioMovimiento.
    
    Ver: apps.ventas.models.movimiento.ProductoUsuarioMovimiento
    """
    venta_id = models.IntegerField(help_text="ID de la venta en la tabla externa")
    producto_id = models.IntegerField(help_text="ID del producto en la tabla externa")
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        db_table = 'ventas_detalleventa'  # Tabla que NO existe en la BD
        managed = False
        verbose_name = 'Detalle de Venta (OBSOLETO)'
        verbose_name_plural = 'Detalles de Venta (OBSOLETO)'

    def __str__(self):
        return f"Detalle Venta {self.id} - Producto ID: {self.producto_id} - OBSOLETO"
        
    def subtotal(self):
        return self.cantidad * self.precio_unitario