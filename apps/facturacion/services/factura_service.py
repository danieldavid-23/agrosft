from decimal import Decimal
from django.db import transaction
from apps.facturacion.models import Factura, ItemFactura
from apps.ventas.models.movimiento import Movimiento, ProductoUsuarioMovimiento, TipoMovimiento
import logging

logger = logging.getLogger(__name__)


class FacturaService:

    @staticmethod
    @transaction.atomic
    def crear_factura_desde_carrito(usuario, carrito) -> Factura:
        tipo_compra, _ = TipoMovimiento.objects.get_or_create(tipo='compra')
        movimiento = Movimiento.objects.create(
            id_tipo_movimiento=tipo_compra,
            id_usuario=usuario,
        )
        total = Decimal('0.00')
        items_data = []
        for item in carrito:
            pu = item['producto']
            cantidad = Decimal(str(item['cantidad']))
            precio = Decimal(str(item['precio']))
            subtotal = cantidad * precio
            total += subtotal
            ProductoUsuarioMovimiento.objects.create(
                id_movimiento=movimiento,
                id_producto_usuario=pu,
                cantidad=-cantidad,
            )
            items_data.append({
                'producto': pu.id_producto,
                'descripcion': f"{pu.id_producto.nombre} - {pu.id_usuario.get_full_name()}",
                'cantidad': cantidad,
                'precio_unitario': precio,
                'subtotal': subtotal,
            })

        factura = Factura.objects.create(
            usuario=usuario,
            movimiento=movimiento,
            total=total,
            estado='emitida',
            payer_email=usuario.correo,
        )
        for it in items_data:
            ItemFactura.objects.create(
                factura=factura,
                producto=it['producto'],
                descripcion=it['descripcion'],
                cantidad=it['cantidad'],
                precio_unitario=it['precio_unitario'],
                subtotal=it['subtotal'],
            )
        return factura

    @staticmethod
    @transaction.atomic
    def cancelar_factura(factura: Factura):
        factura.estado = 'cancelada'
        factura.save(update_fields=['estado'])
        if factura.movimiento:
            factura.movimiento.delete()

    @staticmethod
    def historial_usuario(usuario):
        return Factura.objects.filter(usuario=usuario).select_related('movimiento').order_by('-creada_en')
