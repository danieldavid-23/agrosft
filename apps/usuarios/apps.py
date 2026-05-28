from django.apps import AppConfig

class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.usuarios'  # Full module path
    label = 'usuarios'      # Simple label for internal references
    verbose_name = 'Usuarios'
    
    def ready(self):
        # No hacer nada especial durante la inicialización
        pass