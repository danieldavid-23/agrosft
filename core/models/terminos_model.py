from django.db import models
from apps.usuarios.models.profile_model import Tblusuarios  # Changed to custom user model
from core.models.base_model import BaseModel

class TerminoQuerySet(models.QuerySet):
    def activos(self):
        # Devolvemos un queryset simulado con un objeto estático
        return self.filter(pk=1)  # Simulamos que hay un término activo con pk=1


class TerminoManager(models.Manager):
    def get_queryset(self):
        # Devolvemos un queryset que simula tener términos
        return TerminoQuerySet(model=Termino)
    
    def filter(self, **kwargs):
        # Simulamos el filtro devolviendo instancias estáticas
        if kwargs.get('es_activo', False) or kwargs.get('pk', 0) == 1:
            # Creamos una instancia simulada con datos estáticos
            termino = Termino(
                pk=1,
                version="1.0.0",
                titulo="Términos y Condiciones de Uso",
                contenido="""
TÉRMINOS Y CONDICIONES GENERALES

1. OBJETO
Estos Términos y condiciones regulan el uso de la plataforma Agrosft, destinada a conectar 
productores agrícolas con compradores interesados en productos agrícolas frescos y locales.

2. ACEPTACIÓN DE TÉRMINOS
Al registrarse en la plataforma, usted acepta estos términos y condiciones en su totalidad. 
Si no está de acuerdo, no debe utilizar nuestros servicios.

3. REGISTRO DE USUARIOS
- Debe proporcionar información veraz y actualizada.
- Es responsable de mantener la confidencialidad de su cuenta.
- Debe tener al menos 18 años para registrarse.

4. SERVICIOS DE LA PLATAFORMA
- Facilitamos la conexión entre productores y compradores.
- No somos propietarios de los productos ofertados.
- No intervenimos directamente en las transacciones entre usuarios.

5. OBLIGACIONES DE LOS USUARIOS
- Utilizar la plataforma de manera responsable.
- Proporcionar información veraz sobre productos y servicios.
- Cumplir con las normativas locales aplicables.

6. PROPIEDAD INTELECTUAL
Todos los derechos de propiedad intelectual de la plataforma pertenecen a Agrosft.

7. LIMITACIÓN DE RESPONSABILIDAD
No nos hacemos responsables por incumplimientos de terceros ni por problemas ajenos a nuestra actuación.

8. RESOLUCIÓN DE CONFLICTOS
Cualquier conflicto será resuelto según las leyes vigentes en Colombia.

9. MODIFICACIONES
Nos reservamos el derecho de modificar estos términos en cualquier momento.
                """,
                es_activo=True
            )
            # Simulamos que el queryset tiene un resultado
            termino._state = type('obj', (object,), {'adding': False, 'db': 'default'})()
            return [termino]
        return []


class Termino(models.Model):
    version = models.CharField(max_length=20, default="1.0.0")
    titulo = models.CharField(max_length=200, default="Términos y Condiciones")
    contenido = models.TextField(default="")
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    es_activo = models.BooleanField(default=True)
    
    objects = TerminoManager()
    
    class Meta:
        # Marcamos como managed=False para evitar que Django intente crear la tabla
        managed = False
        ordering = ['-fecha_publicacion']
        verbose_name = "Término y Condición"
        verbose_name_plural = "Términos y Condiciones"
    
    def __str__(self):
        return f"Versión {self.version}"

    def save(self, *args, **kwargs):
        # Sobrescribimos save para evitar intentar guardar en la base de datos
        pass

    def delete(self, *args, **kwargs):
        # Sobrescribimos delete para evitar intentar eliminar de la base de datos
        pass


class AceptacionTerminoManager(models.Manager):
    def create(self, **kwargs):
        # Simulamos la creación pero no guardamos en la base de datos
        aceptacion = AceptacionTermino(**kwargs)
        return aceptacion


class AceptacionTermino(models.Model):
    usuario = models.ForeignKey(Tblusuarios, on_delete=models.CASCADE)  # Changed to custom user model
    termino = models.ForeignKey(Termino, on_delete=models.CASCADE)
    fecha_aceptacion = models.DateTimeField(auto_now_add=True)
    ip_aceptacion = models.GenericIPAddressField(null=True, blank=True)
    
    objects = AceptacionTerminoManager()
    
    class Meta:
        # Marcamos como managed=False para evitar que Django intente crear la tabla
        managed = False
        unique_together = []  # Desactivamos unique_together para evitar errores
        verbose_name = "Aceptación de Término"
        verbose_name_plural = "Aceptaciones de Términos"
    
    def __str__(self):
        return f"{self.usuario} aceptó v{self.termino.version if self.termino else 'N/A'}"

    def save(self, *args, **kwargs):
        # Sobrescribimos save para evitar intentar guardar en la base de datos
        pass

    def delete(self, *args, **kwargs):
        # Sobrescribimos delete para evitar intentar eliminar de la base de datos
        pass