from decimal import Decimal
from apps.inventario.models import ProductoUsuario  # Cambiado de Producto a ProductoUsuario

class Carrito:
    def __init__(self, request):
        self.session = request.session
        carrito = self.session.get('carrito')
        if not carrito:
            carrito = self.session['carrito'] = {}
        self.carrito = carrito

    def agregar(self, producto, cantidad=1):
        producto_id = str(producto.id_producto_usuario)  # Usar id_producto_usuario de ProductoUsuario
        if producto_id not in self.carrito:
            self.carrito[producto_id] = {
                'cantidad': 0,
                'precio': str(producto.precio)
            }
        self.carrito[producto_id]['cantidad'] += int(cantidad)
        self.guardar()

    def guardar(self):
        self.session.modified = True

    def eliminar(self, producto_id):
        producto_id = str(producto_id)
        if producto_id in self.carrito:
            del self.carrito[producto_id]
            self.guardar()

    def actualizar(self, producto_id, cantidad):
        producto_id = str(producto_id)
        cantidad = int(cantidad)
        if cantidad <= 0:
            self.eliminar(producto_id)
        else:
            if producto_id in self.carrito:
                self.carrito[producto_id]['cantidad'] = cantidad
                self.guardar()

    def limpiar(self):
        self.session['carrito'] = {}
        self.session.modified = True

    def __iter__(self):
        producto_ids = self.carrito.keys()
        # Filtrar productos de la tabla ProductoUsuario en lugar de Producto
        productos = ProductoUsuario.objects.filter(id_producto_usuario__in=producto_ids)
        carrito = self.carrito.copy()
        
        for producto in productos:
            carrito[str(producto.id_producto_usuario)]['producto'] = producto

        for item in list(carrito.values()):
            if 'producto' in item:
                precio_dec = Decimal(str(item['precio']))
                item['precio'] = int(precio_dec) if precio_dec % 1 == 0 else precio_dec
                subtotal_dec = item['precio'] * item['cantidad']
                item['subtotal'] = int(subtotal_dec) if subtotal_dec % 1 == 0 else subtotal_dec
                yield item

    def get_total_precio(self):
        total = sum(item['subtotal'] for item in self)
        if isinstance(total, (int, float, Decimal)) and total % 1 == 0:
            return int(total)
        return total

    def __len__(self):
        return sum(item['cantidad'] for item in self)