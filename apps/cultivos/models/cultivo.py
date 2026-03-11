from django.db import models
from django.contrib.auth.models import User
from apps.inventario.models import Producto

class Cultivo(models.Model):
    agricultor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cultivos')
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    area_hectareas = models.DecimalField(max_digits=5, decimal_places=2)
    fecha_siembra = models.DateField()
    productos_utilizados = models.ManyToManyField(Producto, through='UsoProductoCultivo')
    estado = models.CharField(max_length=50, choices=[
        ('activo', 'Activo'),
        ('cosechado', 'Cosechado'),
        ('abandonado', 'Abandonado'),
    ], default='activo')

    def __str__(self):
        return self.nombre

class UsoProductoCultivo(models.Model):
    cultivo = models.ForeignKey(Cultivo, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_aplicacion = models.DateField()

    def __str__(self):
        return f"{self.producto.nombre} en {self.cultivo.nombre}"