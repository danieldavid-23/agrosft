from django.apps import AppConfig

class VentasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.ventas'  # Full module path
    label = 'ventas'      # Simple label for internal references
    verbose_name = 'Ventas'
    
    def ready(self):
        # No hacer nada especial durante la inicialización
        pass