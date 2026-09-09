import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('facturacion', '0002_remove_factura_metodo_pago_remove_factura_pagada_en_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='factura',
            name='vendedor',
            field=models.ForeignKey(
                blank=True,
                db_column='id_vendedor',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='facturas_vendedor',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='factura',
            name='usuario',
            field=models.ForeignKey(
                db_column='id_usuario',
                on_delete=django.db.models.deletion.CASCADE,
                related_name='facturas_comprador',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='factura',
            name='movimiento',
            field=models.ForeignKey(
                blank=True,
                db_column='id_movimiento',
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='facturas',
                to='ventas.movimiento',
            ),
        ),
        # Nota: No se añade UniqueConstraint porque MariaDB 10.4 no soporta
        # partial unique indexes. La unicidad movimiento+vendedor se garantiza
        # a nivel de FacturaService (crear_facturas_desde_movimiento).
    ]

