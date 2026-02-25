from apps.usuarios.models import Termino, AceptacionTermino
from core.repositories.base_repository import BaseRepository
from django.utils import timezone

class TerminoRepository(BaseRepository):
    model = Termino
    
    @classmethod
    def get_termino_activo(cls):
        """Obtiene la versión activa de términos y condiciones"""
        try:
            return cls.model.objects.filter(es_activo=True).latest('fecha_publicacion')
        except cls.model.DoesNotExist:
            return None
    
    @classmethod
    def get_termino_por_version(cls, version):
        """Obtiene una versión específica de términos"""
        try:
            return cls.model.objects.get(version=version)
        except cls.model.DoesNotExist:
            return None
    
    @classmethod
    def crear_nueva_version(cls, version, contenido, titulo="Términos y Condiciones"):
        """Crea una nueva versión y desactiva la anterior"""
        # Desactivar versión activa actual
        cls.model.objects.filter(es_activo=True).update(es_activo=False)
        
        # Crear nueva versión
        return cls.model.objects.create(
            version=version,
            titulo=titulo,
            contenido=contenido,
            es_activo=True
        )

class AceptacionTerminoRepository(BaseRepository):
    model = AceptacionTermino
    
    @classmethod
    def usuario_acepto_version(cls, usuario, termino):
        """Verifica si un usuario ya aceptó una versión específica"""
        return cls.model.objects.filter(
            usuario=usuario,
            termino=termino
        ).exists()
    
    @classmethod
    def get_aceptaciones_usuario(cls, usuario):
        """Obtiene todas las aceptaciones de un usuario"""
        return cls.model.objects.filter(usuario=usuario).select_related('termino')
    
    @classmethod
    def registrar_aceptacion(cls, usuario, termino, ip=None):
        """Registra que un usuario aceptó los términos"""
        return cls.model.objects.create(
            usuario=usuario,
            termino=termino,
            ip_aceptacion=ip
        )