from django.db import models
from django.contrib.auth.models import User
from apps.clientes.models import Cliente
from apps.inventario.models import Producto

class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='ventas')
    productos = models.ManyToManyField(Producto, through='DetalleVenta')
    fecha_venta = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    vendedor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ventas_realizadas')

    def __str__(self):
        return f"Venta {self.id} - {self.cliente.nombre_completo}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre} x {self.cantidad}"