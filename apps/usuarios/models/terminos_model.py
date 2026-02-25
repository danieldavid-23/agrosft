from django.db import models
from django.contrib.auth.models import User
from core.models.base_model import BaseModel

class Termino(BaseModel):
    version = models.CharField(max_length=20, unique=True)
    titulo = models.CharField(max_length=200, default="Términos y Condiciones")
    contenido = models.TextField()
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    es_activo = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-fecha_publicacion']
        verbose_name = "Término y Condición"
        verbose_name_plural = "Términos y Condiciones"
    
    def __str__(self):
        return f"Versión {self.version}"

class AceptacionTermino(BaseModel):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    termino = models.ForeignKey(Termino, on_delete=models.CASCADE)
    fecha_aceptacion = models.DateTimeField(auto_now_add=True)
    ip_aceptacion = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        unique_together = ['usuario', 'termino']
    
    def __str__(self):
        return f"{self.usuario} aceptó v{self.termino.version}"