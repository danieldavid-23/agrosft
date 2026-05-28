from django.apps import AppConfig

class ClientesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.clientes'  # Full module path
    label = 'clientes'      # Simple label for internal references
    verbose_name = 'Clientes'
    
    def ready(self):
        # No hacer nada especial durante la inicialización
        pass