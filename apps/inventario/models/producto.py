from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.contrib.auth.models import User
from .categoria import Categoria

class Producto(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente de aprobación'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('eliminado', 'Eliminado'),
    ]
    
    nombre = models.CharField(max_length=200, db_index=True)
    descripcion = models.TextField()
    categoria = models.ForeignKey(
        Categoria, on_delete=models.PROTECT, related_name='productos'
    )
    precio = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    stock = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    stock_minimo = models.PositiveIntegerField(default=5)
    
    # Relaciones (se completarán con el modelo Usuario de la app usuarios)
    agricultor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='productos', null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    
    # Soft delete
    eliminado = models.BooleanField(default=False)
    fecha_eliminacion = models.DateTimeField(null=True, blank=True)
    eliminado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos_eliminados')
    
    # Control
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.nombre
    
    @property
    def esta_agotado(self):
        return self.stock == 0
    
    def soft_delete(self, user_id=None):
        self.eliminado = True
        self.estado = 'eliminado'
        self.fecha_eliminacion = timezone.now()
        self.eliminado_por_id = user_id
        self.save()