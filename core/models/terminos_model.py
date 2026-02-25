from django.db import models
from django.contrib.auth.models import User
from core.models.base_model import BaseModel

class Termino(BaseModel):
    """Modelo para almacenar las versiones de términos y condiciones"""
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
        return f"Versión {self.version} - {self.fecha_publicacion.strftime('%d/%m/%Y')}"

class AceptacionTermino(BaseModel):
    """Modelo para registrar qué usuarios aceptaron qué versión de términos"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='aceptaciones_terminos')
    termino = models.ForeignKey(Termino, on_delete=models.CASCADE, related_name='aceptaciones')
    fecha_aceptacion = models.DateTimeField(auto_now_add=True)
    ip_aceptacion = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-fecha_aceptacion']
        unique_together = ['usuario', 'termino']  # Un usuario solo puede aceptar una vez cada versión
        verbose_name = "Aceptación de Término"
        verbose_name_plural = "Aceptaciones de Términos"
    
    def __str__(self):
        return f"{self.usuario.username} aceptó v{self.termino.version} el {self.fecha_aceptacion.strftime('%d/%m/%Y')}"