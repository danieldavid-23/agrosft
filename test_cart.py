import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from apps.ventas.controllers.carrito_controller import checkout_carrito
from apps.ventas.models.solicitud import SolicitudCompra
from apps.clientes.models import Cliente
from apps.usuarios.models.profile_model import Tblusuarios  # Changed to custom user model
from apps.inventario.models import Producto

def test():
    # Setup mock request
    rf = RequestFactory()
    
    # Create required objects
    # Using the custom user model instead of Django's default User
    user, _ = Tblusuarios.objects.get_or_create(
        correo='testuser@example.com',
        defaults={
            'nombres': 'Test',
            'apellidos': 'User',
            'telefono': '1234567890',
            'estado': 'activo'
        }
    )
    cliente, _ = Cliente.objects.get_or_create(nombre_completo='Test User', defaults={'telefono': '123456789'})

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
    # Assuming there's a product to add to cart
    # Note: This test may need further adjustment depending on the exact implementation
    
    # Call checkout
    response = checkout_carrito(request)
    print("Response status:", response.status_code)
    print("Response URL:", response.url if hasattr(response, 'url') else 'No URL')
    
    # Verify Solicitud
    solicitud = SolicitudCompra.objects.last()
    if solicitud:
        print("Solicitud ID:", solicitud.id)
        # detalles may not be available if not implemented yet
        print("Solicitud created successfully")
    else:
        print("No solicitud created!")
        from django.contrib.messages import get_messages
        for m in get_messages(request):
            print("Message:", m)

if __name__ == '__main__':
    test()