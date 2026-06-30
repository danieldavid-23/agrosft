from decimal import Decimal
from datetime import datetime
from django.db import transaction
from django.utils import timezone
from apps.facturacion.models import Factura, ItemFactura, MetodoPago
from apps.facturacion.payment_gateways import get_gateway, PagoResultado
from apps.ventas.models.movimiento import Movimiento, ProductoUsuarioMovimiento, TipoMovimiento
from apps.inventario.models.producto import ProductoUsuario, Producto
import logging

logger = logging.getLogger(__name__)


class FacturaService:

    @staticmethod
    @transaction.atomic
    def crear_factura_desde_carrito(usuario, carrito, metodo_pago_codigo='mercadopago') -> Factura:
        metodo = MetodoPago.objects.get(codigo=metodo_pago_codigo, estado='activo')
        tipo_compra, _ = TipoMovimiento.objects.get_or_create(tipo='compra')
        movimiento = Movimiento.objects.create(
            id_tipo_movimiento=tipo_compra,
            id_usuario=usuario,
        )
        total = Decimal('0.00')
        items_data = []
        for item in carrito:
            pu: ProductoUsuario = item['producto']
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
            metodo_pago=metodo,
            estado='pendiente',
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
    def procesar_pago(factura: Factura, request) -> PagoResultado:
        gateway = get_gateway(factura.metodo_pago.codigo)
        resultado = gateway.crear_pago(factura, request)
        if resultado.exito and resultado.transaction_id:
            factura.transaction_id = resultado.transaction_id
            factura.payment_data = resultado.raw_response
            factura.save(update_fields=['transaction_id', 'payment_data'])
        return resultado

    @staticmethod
    @transaction.atomic
    def confirmar_pago(factura: Factura, transaction_id=None) -> bool:
        tid = transaction_id or factura.transaction_id
        if not tid:
            return False
        gateway = get_gateway(factura.metodo_pago.codigo)
        resultado = gateway.verificar_pago(tid)
        if resultado.exito:
            factura.estado = 'pagada'
            factura.pagada_en = timezone.now()
            factura.payment_data = resultado.raw_response
            factura.save(update_fields=['estado', 'pagada_en', 'payment_data'])
            logger.info(f"Factura #{factura.id_factura} pagada via {factura.metodo_pago.codigo}")
            return True
        return False

    @staticmethod
    @transaction.atomic
    def cancelar_factura(factura: Factura):
        factura.estado = 'cancelada'
        factura.save(update_fields=['estado'])
        if factura.movimiento:
            factura.movimiento.delete()

    @staticmethod
    def historial_usuario(usuario):
        return Factura.objects.filter(usuario=usuario).select_related('metodo_pago', 'movimiento').order_by('-creada_en')
