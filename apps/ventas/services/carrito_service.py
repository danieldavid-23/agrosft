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

        for item in carrito.values():
            item['precio'] = Decimal(item['precio'])
            item['subtotal'] = item['precio'] * item['cantidad']
            yield item

    def get_total_precio(self):
        return sum(Decimal(item['precio']) * item['cantidad'] for item in self.carrito.values())
        
    def __len__(self):
        return sum(item['cantidad'] for item in self.carrito.values())