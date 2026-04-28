from django.db import models
from django.contrib.auth.models import User
from apps.clientes.models import Cliente
from apps.inventario.models import Producto

class SolicitudCompra(models.Model):
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('aceptada', 'Aceptada'),
        ('rechazada', 'Rechazada'),
        ('vendido', 'Vendido'),
    )
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='solicitudes_compra')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    observaciones = models.TextField(blank=True, null=True)
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitudes_creadas')
    
    def __str__(self):
        return f"Solicitud {self.id} - {self.cliente.nombre_completo} ({self.get_estado_display()})"
    
    def total_estimado(self):
        return sum(detalle.subtotal() for detalle in self.detalles.all())

class DetalleSolicitudCompra(models.Model):
    solicitud = models.ForeignKey(SolicitudCompra, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    
    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"
        
    def subtotal(self):
        return self.cantidad * self.producto.precio
