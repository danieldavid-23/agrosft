from ..models.terminos_model import fake_termino_manager, AceptacionTermino
from apps.usuarios.models.profile_model import Tblusuarios


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
            # Actualizar el campo de aceptación de términos en el modelo de usuario
            usuario.acepta_terminos = True
            usuario.save(update_fields=['acepta_terminos'])
            
            # Simular el registro de aceptación (sin persistir en base de datos)
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
        if not hasattr(usuario, 'acepta_terminos'):
            return False
        return usuario.acepta_terminos
    
    @staticmethod
    def historial_aceptacion(usuario):
        """Obtiene el historial de aceptación de términos de un usuario"""
        # Simular historial vacío o básico
        return []
    
    @staticmethod
    def usuario_debe_aceptar_terminos(usuario):
        """Verifica si un usuario debe aceptar los términos actuales"""
        # Si el usuario no ha aceptado términos, debe aceptarlos
        return not hasattr(usuario, 'acepta_terminos') or not usuario.acepta_terminos
    
    @staticmethod
    def obtener_historial_usuario(usuario):
        """Obtiene el historial de aceptación de términos de un usuario"""
        # Simular historial vacío
        return []