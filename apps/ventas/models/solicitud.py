"""
NOTA IMPORTANTE: Este módulo está OBSOLETO

Las solicitudes de compra ahora se manejan usando las tablas existentes:
- movimiento (como header de la solicitud)
- tblproductos_has_tblusuarios_has_movimiento (como detalles)
- tipo_movimiento (filtrando por tipo='compra')

Estos modelos se mantienen SOLO para compatibilidad con código legacy.
NO se deben usar en nuevo código.

Para implementar solicitudes de compra, usar:
- apps.ventas.models.movimiento.Movimiento
- apps.ventas.models.movimiento.ProductoUsuarioMovimiento
"""
from django.db import models
from apps.usuarios.models.profile_model import Tblusuarios
from apps.inventario.models.producto import ProductoUsuario


class SolicitudCompra(models.Model):
    """
    MODELO OBSOLETO - NO USAR
    
    Este modelo NO tiene una tabla real en la base de datos.
    Las solicitudes de compra se implementan usando el modelo Movimiento
    con tipo_movimiento.tipo='compra' o 'venta'.
    
    Ver: apps.ventas.models.movimiento.Movimiento
    """
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
        ('vendido', 'Vendido'),
        ('cancelado', 'Cancelado'),
    )
    
    cliente_id = models.IntegerField(help_text="ID del cliente en la tabla externa")
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    observaciones = models.TextField(blank=True, null=True)
    creado_por_id = models.IntegerField(help_text="ID del usuario creador en la tabla externa", null=True, blank=True)
    
    class Meta:
        db_table = 'ventas_solicitudcompra'  # Tabla que NO existe en la BD
        managed = False
        verbose_name = 'Solicitud de Compra (OBSOLETO)'
        verbose_name_plural = 'Solicitudes de Compra (OBSOLETO)'
    
    def __str__(self):
        return f"Solicitud {self.id} - Cliente ID: {self.cliente_id} ({self.get_estado_display()}) - OBSOLETO"
    
    def total_estimado(self):
        """Método placeholder - no se puede calcular sin relaciones directas"""
        return 0


class DetalleSolicitudCompra(models.Model):
    """
    MODELO OBSOLETO - NO USAR
    
    Este modelo NO tiene una tabla real en la base de datos.
    Los detalles de solicitudes se implementan usando ProductoUsuarioMovimiento.
    
    Ver: apps.ventas.models.movimiento.ProductoUsuarioMovimiento
    """
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('aceptado', 'Aceptado'),
        ('rechazado', 'Rechazado'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
    )

    solicitud = models.ForeignKey(SolicitudCompra, on_delete=models.CASCADE, related_name='detalles')
    producto_id = models.IntegerField(help_text="ID del producto en la tabla externa")
    cantidad = models.PositiveIntegerField()
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    
    class Meta:
        db_table = 'ventas_detallesolicitudcompra'  # Tabla que NO existe en la BD
        managed = False
        verbose_name = 'Detalle de Solicitud (OBSOLETO)'
        verbose_name_plural = 'Detalles de Solicitud (OBSOLETO)'
    
    def __str__(self):
        return f"Detalle {self.id} - Producto ID: {self.producto_id}, Cantidad: {self.cantidad} - OBSOLETO"
        
    def subtotal(self):
        """Método placeholder - no se puede calcular sin acceso directo al producto"""
        return 0