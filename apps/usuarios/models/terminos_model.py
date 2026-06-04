from django.db import models
from apps.usuarios.models.profile_model import Tblusuarios
from core.models.base_model import BaseModel

class Termino:
    """Clase simulada para términos y condiciones sin base de datos"""
    
    def __init__(self, version="1.0", titulo="Términos y Condiciones", contenido="", fecha_publicacion=None, es_activo=True):
        self.version = version
        self.titulo = titulo
        self.contenido = contenido
        self.fecha_publicacion = fecha_publicacion or "2026-01-01 00:00:00"
        self.es_activo = es_activo
    
    def __str__(self):
        return f"Versión {self.version}"


class AceptacionTermino:
    """Clase simulada para aceptación de términos sin base de datos"""
    
    def __init__(self, usuario, termino, fecha_aceptacion=None, ip_aceptacion=None):
        self.usuario = usuario
        self.termino = termino
        self.fecha_aceptacion = fecha_aceptacion or "2026-01-01 00:00:00"
        self.ip_aceptacion = ip_aceptacion


class TerminoManager:
    """Simulación de un manager para manejar términos estáticos"""
    
    @staticmethod
    def get_terminos_por_defecto():
        """Devuelve los términos y condiciones por defecto"""
        contenido = """
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
        """
        return Termino(
            version="1.0.0",
            titulo="Términos y Condiciones de Uso",
            contenido=contenido,
            fecha_publicacion="2026-01-01 00:00:00",
            es_activo=True
        )


# Creamos un objeto global para simular el acceso a través del modelo
fake_termino_manager = TerminoManager()