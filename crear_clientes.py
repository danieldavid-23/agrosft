import os
import django

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.clientes.models import Cliente

def crear_clientes_prueba():
    clientes_data = [
        {"username": "juanp", "email": "juan@example.com", "nombre_completo": "Juan Pérez", "telefono": "123456789"},
        {"username": "mariag", "email": "maria@example.com", "nombre_completo": "María González", "telefono": "987654321"},
        {"username": "carlosr", "email": "carlos@example.com", "nombre_completo": "Carlos Rodríguez", "telefono": "555555555"}
    ]
    
    creados = 0
    for data in clientes_data:
        # Create user if it doesn't exist
        user, user_created = User.objects.get_or_create(
            username=data['username'],
            defaults={'email': data['email']}
        )
        if user_created:
            user.set_password('password123')
            user.save()
            
        # Create client if it doesn't exist
        cliente, cliente_created = Cliente.objects.get_or_create(
            user=user,
            defaults={
                'nombre_completo': data['nombre_completo'],
                'telefono': data['telefono'],
                'direccion': 'Dirección de prueba'
            }
        )
        if cliente_created:
            creados += 1
            print(f"✅ Cliente creado: {cliente.nombre_completo}")
        else:
            print(f"⚠️ El cliente {cliente.nombre_completo} ya existía.")

    print(f"\nProceso finalizado. Se crearon {creados} clientes nuevos.")

if __name__ == '__main__':
    crear_clientes_prueba()
