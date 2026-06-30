from django.apps import AppConfig
from django.db.models.signals import post_migrate


def seed_metodos_pago(sender, **kwargs):
    from .models import MetodoPago
    defaults = [
        ('mercadopago', 'Mercado Pago', 2.99, 'https://www.mercadopago.com/favicon.ico', 1),
        ('wompi', 'Wompi', 1.90, 'https://wompi.co/favicon.ico', 2),
        ('paypal', 'PayPal', 3.50, 'https://www.paypal.com/favicon.ico', 3),
    ]
    for codigo, nombre, comision, logo, orden in defaults:
        MetodoPago.objects.get_or_create(
            codigo=codigo,
            defaults={
                'nombre': nombre,
                'comision_porcentaje': comision,
                'logo_url': logo,
                'orden': orden,
                'estado': 'activo',
            }
        )


class FacturacionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.facturacion'
    label = 'facturacion'
    verbose_name = 'Facturacion'

    def ready(self):
        post_migrate.connect(seed_metodos_pago, sender=self)
