from django.db import models

class HistorialProducto(models.Model):
    ACCION_CHOICES = [
        ('creacion', 'Creación'),
        ('modificacion', 'Modificación'),
        ('aprobacion', 'Aprobación'),
        ('rechazo', 'Rechazo'),
        ('eliminacion', 'Eliminación'),
    ]
    
    producto_id = models.IntegerField(db_index=True)
    usuario_id = models.IntegerField(null=True)
    accion = models.CharField(max_length=20, choices=ACCION_CHOICES)
    campo_modificado = models.CharField(max_length=50, blank=True)
    valor_anterior = models.TextField(blank=True)
    valor_nuevo = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-fecha']