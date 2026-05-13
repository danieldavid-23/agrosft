import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from apps.ventas.controllers.carrito_controller import checkout_carrito
from apps.ventas.models.solicitud import SolicitudCompra
from apps.clientes.models import Cliente
from django.contrib.auth.models import User
from apps.inventario.models import Producto

def test():
    # Setup mock request
    rf = RequestFactory()
    
    # Create required objects
    user, _ = User.objects.get_or_create(username='testuser')
    cliente, _ = Cliente.objects.get_or_create(nombre='Test', apellidos='User', defaults={'documento':'123456789'})
    producto, _ = Producto.objects.get_or_create(nombre='Manzana', defaults={'precio': 1000, 'stock': 50})
    
    # Create POST request
    request = rf.post('/carrito/checkout/', {'cliente': cliente.id, 'observaciones': 'Test obs'})
    request.user = user
    
    # Add session middleware
    middleware = SessionMiddleware(lambda r: None)
    middleware.process_request(request)
    request.session.save()
    
    # Setup cart
    from apps.ventas.services.carrito_service import Carrito
    carrito = Carrito(request)
    carrito.agregar(producto, 2)
    
    # Call checkout
    response = checkout_carrito(request)
    print("Response status:", response.status_code)
    print("Response URL:", response.url if hasattr(response, 'url') else 'No URL')
    
    # Verify Solicitud
    solicitud = SolicitudCompra.objects.last()
    if solicitud:
        print("Solicitud ID:", solicitud.id)
        detalles = solicitud.detalles.all()
        print("Detalles count:", detalles.count())
        for d in detalles:
            print("  - Detalle:", d.producto.nombre, d.cantidad)
    else:
        print("No solicitud created!")
        from django.contrib.messages import get_messages
        for m in get_messages(request):
            print("Message:", m)

if __name__ == '__main__':
    test()
