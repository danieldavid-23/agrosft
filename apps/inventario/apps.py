from django.apps import AppConfig

class InventarioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.inventario'  # Full module path
    label = 'inventario'      # Simple label for internal references
    verbose_name = 'Inventario'
    
    def ready(self):
        # No hacer nada especial durante la inicialización
        pass