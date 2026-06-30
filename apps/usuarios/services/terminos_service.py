from ..models.terminos_model import fake_termino_manager, AceptacionTermino
from apps.usuarios.models.profile_model import Tblusuarios
from django.core.cache import cache
from datetime import datetime


class TerminosService:
    
    @staticmethod
    def obtener_terminos_activos():
        """Obtiene los términos y condiciones activos"""
        return fake_termino_manager.get_terminos_por_defecto()
    
    @staticmethod
    def aceptar_terminos(usuario, request):
        """Registra la aceptación de términos por un usuario"""
        termino_activo = TerminosService.obtener_terminos_activos()
        if termino_activo:
            # Guardar la aceptación de términos en caché usando el ID del usuario (persistencia de 30 días)
            cache_key = f"user_{usuario.id_users}_acepto_terminos"
            cache.set(cache_key, True, 60 * 60 * 24 * 30)
            
            # Intentar actualizar el atributo en memoria (persistente mientras dure el objeto)
            usuario.acepta_terminos = True
            
            # Registrar aceptación simulada para el historial en memoria
            aceptacion_simulada = AceptacionTermino(
                usuario=usuario,
                termino=termino_activo,
                ip_aceptacion=request.META.get('REMOTE_ADDR')
            )
            return True, "Términos aceptados correctamente."
        return False, "No hay términos activos para aceptar."
    
    @staticmethod
    def verificar_aceptacion(usuario):
        """Verifica si un usuario ha aceptado los términos actuales"""
        # 1. Comprobar caché primero
        cache_key = f"user_{usuario.id_users}_acepto_terminos"
        if cache.get(cache_key):
            return True
            
        # 2. Comprobar atributo en memoria
        if hasattr(usuario, 'acepta_terminos') and usuario.acepta_terminos:
            return True
            
        return False
    
    @staticmethod
    def historial_aceptacion(usuario):
        """Obtiene el historial de aceptación de términos de un usuario"""
        return TerminosService.obtener_historial_usuario(usuario)
    
    @staticmethod
    def usuario_debe_aceptar_terminos(usuario):
        """Verifica si un usuario debe aceptar los términos actuales"""
        return not TerminosService.verificar_aceptacion(usuario)
    
    @staticmethod
    def obtener_historial_usuario(usuario):
        """Obtiene el historial de aceptación de términos de un usuario"""
        # Si el usuario ya ha aceptado los términos, devolvemos el registro simulado
        cache_key = f"user_{usuario.id_users}_acepto_terminos"
        if cache.get(cache_key) or (hasattr(usuario, 'acepta_terminos') and usuario.acepta_terminos):
            termino_activo = TerminosService.obtener_terminos_activos()
            return [
                AceptacionTermino(
                    usuario=usuario,
                    termino=termino_activo,
                    fecha_aceptacion=datetime.now(),
                    ip_aceptacion="127.0.0.1"
                )
            ]
        return []