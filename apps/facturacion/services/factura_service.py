from collections import defaultdict
from decimal import Decimal
from django.db import transaction
from apps.facturacion.models import Factura, ItemFactura
from apps.ventas.models.movimiento import Movimiento, ProductoUsuarioMovimiento, TipoMovimiento
import logging

logger = logging.getLogger(__name__)


class FacturaService:
    """
    Servicio de facturación que implementa la regla:
        UN PEDIDO (Movimiento) = UNA FACTURA POR VENDEDOR

    Principios de seguridad:
    - vendedor_id nunca se toma del frontend; se obtiene de ProductoUsuario.id_usuario en BD.
    - precio nunca se toma del frontend; se obtiene de ProductoUsuario.precio en BD.
    - cliente_id nunca se toma del frontend; se obtiene del Movimiento.id_usuario en BD.
    - La operación es atómica: si falla una factura, se hace rollback de todas.
    """

    # ------------------------------------------------------------------
    # Método principal: desde carrito (checkout con factura inmediata)
    # ------------------------------------------------------------------
    @staticmethod
    @transaction.atomic
    def crear_facturas_desde_carrito(usuario, carrito) -> list:
        """
        Crea un Movimiento de tipo 'compra' a partir del carrito y genera
        UNA FACTURA POR CADA VENDEDOR que participa en el carrito.

        Args:
            usuario: Tblusuarios — comprador autenticado.
            carrito: iterable de dicts con claves 'producto' (ProductoUsuario),
                     'cantidad' (int/Decimal), 'precio' (Decimal).

        Returns:
            Lista de objetos Factura creados (una por vendedor).
        """
        tipo_compra, _ = TipoMovimiento.objects.get_or_create(tipo='compra')
        movimiento = Movimiento.objects.create(
            id_tipo_movimiento=tipo_compra,
            id_usuario=usuario,
        )

        # Agrupar ítems del carrito por vendedor (id_usuario del ProductoUsuario)
        grupos_por_vendedor = defaultdict(list)
        for item in carrito:
            pu = item['producto']
            vendedor = pu.id_usuario  # origen seguro: BD, no frontend
            precio_bd = Decimal(str(pu.precio))  # precio desde BD, no frontend
            cantidad = Decimal(str(item['cantidad']))

            # Registrar movimiento en BD (activa trigger de stock)
            ProductoUsuarioMovimiento.objects.create(
                id_movimiento=movimiento,
                id_producto_usuario=pu,
                cantidad=-cantidad,  # negativa = salida de stock
            )

            grupos_por_vendedor[vendedor.pk].append({
                'pu': pu,
                'vendedor': vendedor,
                'cantidad': cantidad,
                'precio_unitario': precio_bd,
                'subtotal': cantidad * precio_bd,
            })

        # Crear una factura por cada grupo de vendedor
        facturas_creadas = []
        for vendedor_id, items in grupos_por_vendedor.items():
            vendedor = items[0]['vendedor']
            total_vendedor = sum(it['subtotal'] for it in items)

            factura = Factura.objects.create(
                usuario=usuario,          # comprador (fuente: request.user en BD)
                vendedor=vendedor,        # vendedor (fuente: ProductoUsuario.id_usuario en BD)
                movimiento=movimiento,
                total=total_vendedor,
                estado='emitida',
                payer_email=usuario.correo,
            )

            for it in items:
                ItemFactura.objects.create(
                    factura=factura,
                    producto=it['pu'].id_producto,
                    descripcion=it['pu'].id_producto.nombre,
                    cantidad=it['cantidad'],
                    precio_unitario=it['precio_unitario'],
                    subtotal=it['subtotal'],
                )

            facturas_creadas.append(factura)
            logger.info(
                "Factura #%s creada — movimiento #%s — vendedor %s — total %s",
                factura.id_factura, movimiento.id_movimiento,
                vendedor.correo, total_vendedor
            )

        return facturas_creadas

    # ------------------------------------------------------------------
    # Método principal: desde movimiento existente (solicitud aceptada)
    # ------------------------------------------------------------------
    @staticmethod
    @transaction.atomic
    def crear_facturas_desde_movimiento(usuario, movimiento: Movimiento) -> list:
        """
        A partir de un Movimiento ya registrado en BD, genera UNA FACTURA
        POR CADA VENDEDOR que participa en el pedido.

        Si ya existe una factura para (movimiento, vendedor), la reutiliza
        en lugar de crear una duplicada.

        Args:
            usuario: Tblusuarios — comprador o actor que solicita la generación.
            movimiento: Movimiento ya persistido.

        Returns:
            Lista de objetos Factura (existentes o recién creadas).
        """
        detalles = ProductoUsuarioMovimiento.objects.filter(
            id_movimiento=movimiento
        ).select_related(
            'id_producto_usuario__id_producto',
            'id_producto_usuario__id_usuario',
        )

        # Comprador real desde BD (nunca del frontend)
        comprador = movimiento.id_usuario

        # Agrupar detalles por vendedor
        grupos_por_vendedor = defaultdict(list)
        for d in detalles:
            pu = d.id_producto_usuario
            vendedor = pu.id_usuario  # seguro: viene de BD
            cantidad = Decimal(str(abs(d.cantidad)))
            precio_bd = Decimal(str(pu.precio))  # seguro: viene de BD
            grupos_por_vendedor[vendedor.pk].append({
                'pu': pu,
                'vendedor': vendedor,
                'cantidad': cantidad,
                'precio_unitario': precio_bd,
                'subtotal': cantidad * precio_bd,
            })

        facturas_resultado = []
        for vendedor_id, items in grupos_por_vendedor.items():
            vendedor = items[0]['vendedor']

            # Verificar si ya existe factura para este par (movimiento, vendedor) — evita duplicados
            factura = Factura.objects.filter(
                movimiento=movimiento,
                vendedor=vendedor,
            ).first()

            if factura:
                logger.info(
                    "Factura #%s ya existía para movimiento #%s vendedor %s — reutilizando.",
                    factura.id_factura, movimiento.id_movimiento, vendedor.correo
                )
                facturas_resultado.append(factura)
                continue

            total_vendedor = sum(it['subtotal'] for it in items)
            factura = Factura.objects.create(
                usuario=comprador,
                vendedor=vendedor,
                movimiento=movimiento,
                total=total_vendedor,
                estado='emitida',
                payer_email=getattr(comprador, 'correo', ''),
            )

            for it in items:
                ItemFactura.objects.create(
                    factura=factura,
                    producto=it['pu'].id_producto,
                    descripcion=it['pu'].id_producto.nombre,
                    cantidad=it['cantidad'],
                    precio_unitario=it['precio_unitario'],
                    subtotal=it['subtotal'],
                )

            facturas_resultado.append(factura)
            logger.info(
                "Factura #%s creada desde movimiento #%s — vendedor %s — total %s",
                factura.id_factura, movimiento.id_movimiento,
                vendedor.correo, total_vendedor
            )

        return facturas_resultado

    # ------------------------------------------------------------------
    # Compatibilidad hacia atrás — wrapper que retorna la primera factura
    # ------------------------------------------------------------------
    @staticmethod
    @transaction.atomic
    def obtener_o_crear_factura_desde_movimiento(usuario, movimiento: Movimiento) -> Factura:
        """
        Mantiene compatibilidad con código legacy que espera una sola Factura.
        Genera (o reutiliza) las facturas del movimiento y retorna la primera.
        """
        facturas = FacturaService.crear_facturas_desde_movimiento(usuario, movimiento)
        if not facturas:
            raise ValueError(f"El movimiento #{movimiento.id_movimiento} no tiene detalles de productos.")
        return facturas[0]

    # ------------------------------------------------------------------
    # Cancelar una factura específica
    # ------------------------------------------------------------------
    @staticmethod
    @transaction.atomic
    def cancelar_factura(factura: Factura):
        factura.estado = 'cancelada'
        factura.save(update_fields=['estado'])
        # Solo elimina el movimiento si esta es la ÚNICA factura del movimiento
        if factura.movimiento:
            otras = Factura.objects.filter(
                movimiento=factura.movimiento
            ).exclude(id_factura=factura.id_factura).exists()
            if not otras:
                factura.movimiento.delete()

    # ------------------------------------------------------------------
    # Historial para el comprador
    # ------------------------------------------------------------------
    @staticmethod
    def historial_usuario(usuario):
        """Facturas donde el usuario es el COMPRADOR."""
        return (
            Factura.objects
            .filter(usuario=usuario)
            .select_related('movimiento', 'vendedor')
            .order_by('-creada_en')
        )

    # ------------------------------------------------------------------
    # Facturas de un movimiento — para vista de pedido
    # ------------------------------------------------------------------
    @staticmethod
    def facturas_del_movimiento(movimiento: Movimiento):
        """Retorna todas las facturas asociadas a un movimiento, con sus items."""
        return (
            Factura.objects
            .filter(movimiento=movimiento)
            .select_related('vendedor')
            .prefetch_related('items__producto')
            .order_by('id_factura')
        )

    # ------------------------------------------------------------------
    # Factura de un vendedor específico en un movimiento
    # ------------------------------------------------------------------
    @staticmethod
    def factura_vendedor_en_movimiento(movimiento: Movimiento, vendedor):
        """Retorna la factura de un vendedor específico en un movimiento."""
        return Factura.objects.filter(
            movimiento=movimiento,
            vendedor=vendedor,
        ).first()
