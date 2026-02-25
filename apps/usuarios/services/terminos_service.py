from apps.usuarios.repositories.terminos_repository import TerminoRepository, AceptacionTerminoRepository
from core.services.base_service import BaseService
from django.contrib.auth.models import User

class TerminosService(BaseService):
    
    @classmethod
    def obtener_terminos_activos(cls):
        """Obtiene los términos activos para mostrar"""
        return TerminoRepository.get_termino_activo()
    
    @classmethod
    def usuario_debe_aceptar_terminos(cls, usuario):
        """Verifica si el usuario necesita aceptar los términos actuales"""
        termino_activo = cls.obtener_terminos_activos()
        if not termino_activo:
            return False
        
        return not AceptacionTerminoRepository.usuario_acepto_version(
            usuario, termino_activo
        )
    
    @classmethod
    def aceptar_terminos(cls, usuario, request):
        """Procesa la aceptación de términos por parte del usuario"""
        termino_activo = cls.obtener_terminos_activos()
        if not termino_activo:
            return False, "No hay términos activos para aceptar"
        
        # Verificar si ya aceptó
        if AceptacionTerminoRepository.usuario_acepto_version(usuario, termino_activo):
            return False, "Ya has aceptado los términos anteriormente"
        
        # Obtener IP
        ip = cls._get_client_ip(request)
        
        # Registrar aceptación
        AceptacionTerminoRepository.registrar_aceptacion(
            usuario=usuario,
            termino=termino_activo,
            ip=ip
        )
        
        return True, "Términos aceptados correctamente"
    
    @classmethod
    def _get_client_ip(cls, request):
        """Obtiene la IP del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    @classmethod
    def obtener_historial_usuario(cls, usuario):
        """Obtiene el historial de aceptaciones de un usuario"""
        return AceptacionTerminoRepository.get_aceptaciones_usuario(usuario)
    
    @classmethod
    def crear_nueva_version(cls, version, contenido, titulo="Términos y Condiciones"):
        """Crea una nueva versión de términos (solo para administradores)"""
        return TerminoRepository.crear_nueva_version(version, contenido, titulo)