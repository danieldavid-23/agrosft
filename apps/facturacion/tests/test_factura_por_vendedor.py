"""
Tests para la regla de facturación separada por vendedor.
"""
from decimal import Decimal
from unittest.mock import patch, MagicMock

from django.test import SimpleTestCase

from apps.facturacion.services.factura_service import FacturaService


def make_usuario(pk, correo='user@test.com'):
    u = MagicMock()
    u.pk = pk
    u.id = pk
    u.correo = correo
    return u


def make_pu(pk, vendedor, precio='1000.00', producto_nombre='Tomate'):
    pu = MagicMock()
    pu.pk = pk
    pu.id_usuario = vendedor
    pu.id_producto = MagicMock()
    pu.id_producto.pk = 1
    pu.id_producto.nombre = producto_nombre
    pu.precio = Decimal(precio)
    return pu


def make_carrito_item(pu, cantidad='3'):
    return {'producto': pu, 'cantidad': Decimal(cantidad), 'precio': pu.precio}


SVC = 'apps.facturacion.services.factura_service'


class TestAgrupacionPorVendedor(SimpleTestCase):

    def setUp(self):
        self.comprador = make_usuario(pk=10, correo='comprador@test.com')
        self.juan = make_usuario(pk=20, correo='juan@test.com')
        self.carlos = make_usuario(pk=21, correo='carlos@test.com')
        self.daniela = make_usuario(pk=22, correo='daniela@test.com')

    @patch(f'{SVC}.Factura')
    @patch(f'{SVC}.ItemFactura')
    @patch(f'{SVC}.TipoMovimiento')
    @patch(f'{SVC}.Movimiento')
    @patch(f'{SVC}.ProductoUsuarioMovimiento')
    def test_un_vendedor_una_factura(self, MockDet, MockMov, MockTipo, MockItem, MockFact):
        carrito = [make_carrito_item(make_pu(1, self.juan, '2000'), '2'),
                   make_carrito_item(make_pu(2, self.juan, '1500'), '3')]
        MockTipo.objects.get_or_create.return_value = (MagicMock(), True)
        MockMov.objects.create.return_value = MagicMock(id_movimiento=99)
        MockDet.objects.create.return_value = MagicMock()
        MockFact.objects.create.return_value = MagicMock(id_factura=1)

        facturas = FacturaService.crear_facturas_desde_carrito(self.comprador, carrito)
        self.assertEqual(len(facturas), 1)
        self.assertEqual(MockFact.objects.create.call_count, 1)
        self.assertEqual(MockItem.objects.create.call_count, 2)

    @patch(f'{SVC}.Factura')
    @patch(f'{SVC}.ItemFactura')
    @patch(f'{SVC}.TipoMovimiento')
    @patch(f'{SVC}.Movimiento')
    @patch(f'{SVC}.ProductoUsuarioMovimiento')
    def test_tres_vendedores_tres_facturas(self, MockDet, MockMov, MockTipo, MockItem, MockFact):
        carrito = [
            make_carrito_item(make_pu(1, self.juan, '2000'), '2'),
            make_carrito_item(make_pu(2, self.carlos, '3000'), '1'),
            make_carrito_item(make_pu(3, self.daniela, '1200'), '5'),
        ]
        MockTipo.objects.get_or_create.return_value = (MagicMock(), True)
        MockMov.objects.create.return_value = MagicMock(id_movimiento=99)
        MockDet.objects.create.return_value = MagicMock()
        MockFact.objects.create.side_effect = [MagicMock(id_factura=i) for i in range(1, 4)]

        facturas = FacturaService.crear_facturas_desde_carrito(self.comprador, carrito)
        self.assertEqual(len(facturas), 3)
        self.assertEqual(MockFact.objects.create.call_count, 3)
        self.assertEqual(MockItem.objects.create.call_count, 3)

    @patch(f'{SVC}.Factura')
    @patch(f'{SVC}.ItemFactura')
    @patch(f'{SVC}.TipoMovimiento')
    @patch(f'{SVC}.Movimiento')
    @patch(f'{SVC}.ProductoUsuarioMovimiento')
    def test_items_separados_por_vendedor(self, MockDet, MockMov, MockTipo, MockItem, MockFact):
        carrito = [make_carrito_item(make_pu(1, self.juan, '2000', 'Tomate'), '2'),
                   make_carrito_item(make_pu(2, self.carlos, '3000', 'Limon'), '1')]
        MockTipo.objects.get_or_create.return_value = (MagicMock(), True)
        MockMov.objects.create.return_value = MagicMock(id_movimiento=99)
        MockDet.objects.create.return_value = MagicMock()
        MockFact.objects.create.side_effect = [MagicMock(id_factura=1), MagicMock(id_factura=2)]

        FacturaService.crear_facturas_desde_carrito(self.comprador, carrito)
        self.assertEqual(MockItem.objects.create.call_count, 2)
        nombres = {c.kwargs['producto'].nombre for c in MockItem.objects.create.call_args_list}
        self.assertEqual(nombres, {'Tomate', 'Limon'})

    @patch(f'{SVC}.Factura')
    @patch(f'{SVC}.ItemFactura')
    @patch(f'{SVC}.TipoMovimiento')
    @patch(f'{SVC}.Movimiento')
    @patch(f'{SVC}.ProductoUsuarioMovimiento')
    def test_totales_correctos(self, MockDet, MockMov, MockTipo, MockItem, MockFact):
        carrito = [
            make_carrito_item(make_pu(1, self.juan, '2000'), '2'),   # 4000
            make_carrito_item(make_pu(2, self.juan, '1500'), '3'),   # 4500 → 8500
            make_carrito_item(make_pu(3, self.carlos, '3000'), '1'), # 3000
        ]
        MockTipo.objects.get_or_create.return_value = (MagicMock(), True)
        MockMov.objects.create.return_value = MagicMock(id_movimiento=99)
        MockDet.objects.create.return_value = MagicMock()
        MockFact.objects.create.side_effect = [MagicMock(id_factura=1), MagicMock(id_factura=2)]

        FacturaService.crear_facturas_desde_carrito(self.comprador, carrito)
        totales = sorted(float(c.kwargs['total']) for c in MockFact.objects.create.call_args_list)
        self.assertEqual(totales, [3000.0, 8500.0])

    @patch(f'{SVC}.Factura')
    @patch(f'{SVC}.ItemFactura')
    @patch(f'{SVC}.TipoMovimiento')
    @patch(f'{SVC}.Movimiento')
    @patch(f'{SVC}.ProductoUsuarioMovimiento')
    def test_precio_y_vendedor_de_bd(self, MockDet, MockMov, MockTipo, MockItem, MockFact):
        pu = make_pu(1, self.juan, '2000.00')
        item = {'producto': pu, 'cantidad': Decimal('2'), 'precio': Decimal('1.00')}
        MockTipo.objects.get_or_create.return_value = (MagicMock(), True)
        MockMov.objects.create.return_value = MagicMock(id_movimiento=99)
        MockDet.objects.create.return_value = MagicMock()
        MockFact.objects.create.return_value = MagicMock(id_factura=1)

        FacturaService.crear_facturas_desde_carrito(self.comprador, [item])
        kw = MockFact.objects.create.call_args.kwargs
        self.assertEqual(kw['total'], Decimal('4000.00'))
        self.assertEqual(kw['vendedor'], self.juan)

    @patch(f'{SVC}.ProductoUsuarioMovimiento')
    @patch(f'{SVC}.Movimiento')
    def test_idempotencia(self, MockMov, MockDet):
        """ crear_facturas_desde_movimiento reutiliza factura existente. """
        pu = make_pu(1, self.juan, '1000')
        MockDet.objects.filter.return_value.select_related.return_value = [
            MagicMock(cantidad=Decimal('-2'), id_producto_usuario=pu)
        ]
        movimiento = MagicMock(id_movimiento=99, id_usuario=self.comprador)

        with patch(f'{SVC}.Factura') as MockFact:
            MockFact.objects.filter.return_value.first.return_value = MagicMock(id_factura=42)
            resultado = FacturaService.crear_facturas_desde_movimiento(self.comprador, movimiento)
            self.assertEqual(len(resultado), 1)
            self.assertEqual(resultado[0].id_factura, 42)
            MockFact.objects.create.assert_not_called()

    @patch(f'{SVC}.ProductoUsuarioMovimiento')
    @patch(f'{SVC}.Movimiento')
    def test_wrapper_legacy(self, MockMov, MockDet):
        """ obtener_o_crear Factura delega a crear_facturas_desde_movimiento. """
        pu = make_pu(1, self.juan, '1000')
        MockDet.objects.filter.return_value.select_related.return_value = [
            MagicMock(cantidad=Decimal('-1'), id_producto_usuario=pu),
        ]
        movimiento = MagicMock(id_movimiento=99, id_usuario=self.comprador)

        with patch(f'{SVC}.Factura') as MockFact, \
             patch.object(FacturaService, 'crear_facturas_desde_movimiento') as mock_crear:
            mock_crear.return_value = [MagicMock(id_factura=7)]
            with patch(f'{SVC}.transaction.atomic', lambda f: f):
                # First call: crear_facturas internally
                pass
            # Simpler: patch the inner call directly
            pass

        # Test más directo: verificar que la función delega correctamente
        with patch.object(FacturaService, 'crear_facturas_desde_movimiento') as mock_crear:
            mock_crear.return_value = [MagicMock(id_factura=7)]
            resultado = FacturaService.obtener_o_crear_factura_desde_movimiento(
                self.comprador, movimiento
            )
            mock_crear.assert_called_once_with(self.comprador, movimiento)
            self.assertEqual(resultado.id_factura, 7)

    @patch(f'{SVC}.ProductoUsuarioMovimiento')
    @patch(f'{SVC}.Movimiento')
    def test_sin_detalles_lanza_error(self, MockMov, MockDet):
        """ obtener_o_crear lanza ValueError si no hay detalles. """
        with patch.object(FacturaService, 'crear_facturas_desde_movimiento') as mock_crear:
            mock_crear.return_value = []
            with self.assertRaises(ValueError):
                FacturaService.obtener_o_crear_factura_desde_movimiento(
                    self.comprador, MagicMock(id_movimiento=99)
                )

    @patch(f'{SVC}.Factura')
    @patch(f'{SVC}.ItemFactura')
    @patch(f'{SVC}.TipoMovimiento')
    @patch(f'{SVC}.Movimiento')
    @patch(f'{SVC}.ProductoUsuarioMovimiento')
    def test_excepcion_se_propaga(self, MockDet, MockMov, MockTipo, MockItem, MockFact):
        carrito = [make_carrito_item(make_pu(1, self.juan, '2000'), '2'),
                   make_carrito_item(make_pu(2, self.carlos, '3000'), '1')]
        MockTipo.objects.get_or_create.return_value = (MagicMock(), True)
        MockMov.objects.create.return_value = MagicMock(id_movimiento=99)
        MockDet.objects.create.return_value = MagicMock()
        MockFact.objects.create.side_effect = [MagicMock(id_factura=1), Exception('DB error')]

        with self.assertRaises(Exception):
            FacturaService.crear_facturas_desde_carrito(self.comprador, carrito)


class TestFacturaModel(SimpleTestCase):

    def test_tabla(self):
        from apps.facturacion.models import Factura
        self.assertEqual(Factura._meta.db_table, 'factura')

    def test_campo_vendedor_existe(self):
        from apps.facturacion.models import Factura
        self.assertIn('vendedor', {f.name for f in Factura._meta.get_fields()})

    def test_campo_vendedor_nullable(self):
        from apps.facturacion.models import Factura
        campo = Factura._meta.get_field('vendedor')
        self.assertTrue(campo.null)
        self.assertTrue(campo.blank)

    def test_campo_vendedor_fk(self):
        from django.conf import settings
        from apps.facturacion.models import Factura
        campo = Factura._meta.get_field('vendedor')
        self.assertEqual(campo.remote_field.model._meta.label, settings.AUTH_USER_MODEL)

    def test_related_name(self):
        from apps.facturacion.models import Factura
        self.assertEqual(Factura._meta.get_field('vendedor').remote_field.related_name, 'facturas_vendedor')

    def test_str_con_vendedor(self):
        from apps.facturacion.models import Factura
        from unittest.mock import PropertyMock
        with patch.object(Factura, 'usuario', new_callable=PropertyMock) as mock_u, \
             patch.object(Factura, 'vendedor', new_callable=PropertyMock) as mock_v:
            mock_u.return_value = MagicMock(correo='com@test.com')
            mock_v.return_value = MagicMock(correo='vend@test.com')
            f = Factura(id_factura=1, total=Decimal('100.00'))
            result = str(f)
        self.assertIn('vend@test.com', result)

    def test_str_sin_vendedor(self):
        from apps.facturacion.models import Factura
        from unittest.mock import PropertyMock
        with patch.object(Factura, 'usuario', new_callable=PropertyMock) as mock_u, \
             patch.object(Factura, 'vendedor', new_callable=PropertyMock) as mock_v:
            mock_u.return_value = MagicMock(correo='com@test.com')
            mock_v.return_value = None
            f = Factura(id_factura=1, total=Decimal('100.00'))
            result = str(f)
        self.assertIn('sin vendedor', result)


class TestItemFacturaModel(SimpleTestCase):

    def test_tabla(self):
        from apps.facturacion.models import ItemFactura
        self.assertEqual(ItemFactura._meta.db_table, 'item_factura')

    def test_campos(self):
        from apps.facturacion.models import ItemFactura
        campos = {f.name for f in ItemFactura._meta.get_fields()}
        for e in ['factura', 'producto', 'descripcion', 'cantidad', 'precio_unitario', 'subtotal']:
            self.assertIn(e, campos)
