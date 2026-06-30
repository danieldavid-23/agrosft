from django.db import models
from django.conf import settings


class MetodoPago(models.Model):
    TIPOS = [
        ('mercadopago', 'Mercado Pago'),
        ('wompi', 'Wompi'),
        ('paypal', 'PayPal'),
    ]
    ESTADOS = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]
    codigo = models.CharField(max_length=20, unique=True, choices=TIPOS)
    nombre = models.CharField(max_length=60)
    comision_porcentaje = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    estado = models.CharField(max_length=10, choices=ESTADOS, default='activo')
    logo_url = models.URLField(blank=True)
    orden = models.IntegerField(default=0)

    class Meta:
        db_table = 'metodo_pago'
        verbose_name = 'Metodo de Pago'
        verbose_name_plural = 'Metodos de Pago'

    def __str__(self):
        return self.nombre


class Factura(models.Model):
    ESTADOS = [
        ('pendiente', 'Pendiente de pago'),
        ('pagada', 'Pagada'),
        ('cancelada', 'Cancelada'),
        ('reembolsada', 'Reembolsada'),
    ]
    id_factura = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        db_column='id_usuario'
    )
    movimiento = models.ForeignKey(
        'ventas.Movimiento', on_delete=models.SET_NULL, null=True, blank=True,
        db_column='id_movimiento'
    )
    total = models.DecimalField(max_digits=12, decimal_places=2)
    metodo_pago = models.ForeignKey(
        MetodoPago, on_delete=models.SET_NULL, null=True,
        db_column='id_metodo_pago'
    )
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')
    transaction_id = models.CharField(max_length=255, blank=True)
    payer_email = models.EmailField(max_length=255, blank=True)
    payment_data = models.JSONField(default=dict, blank=True)
    creada_en = models.DateTimeField(auto_now_add=True, db_column='creada_en')
    pagada_en = models.DateTimeField(null=True, blank=True, db_column='pagada_en')
    pdf_generado = models.BooleanField(default=False, db_column='pdf_generado')

    class Meta:
        db_table = 'factura'
        verbose_name = 'Factura'
        verbose_name_plural = 'Facturas'

    def __str__(self):
        return f'Factura #{self.id_factura} - {self.usuario.correo} - ${self.total}'


class ItemFactura(models.Model):
    id_item = models.AutoField(primary_key=True)
    factura = models.ForeignKey(
        Factura, on_delete=models.CASCADE, related_name='items',
        db_column='id_factura'
    )
    producto = models.ForeignKey(
        'inventario.Producto', on_delete=models.SET_NULL, null=True,
        db_column='id_producto'
    )
    descripcion = models.CharField(max_length=255)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    precio_unitario = models.DecimalField(max_digits=12, decimal_places=2, db_column='precio_unitario')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = 'item_factura'
        verbose_name = 'Item de Factura'
        verbose_name_plural = 'Items de Factura'

    def __str__(self):
        return f'{self.descripcion} x{self.cantidad}'
