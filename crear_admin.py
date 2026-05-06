import os
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.usuarios.models import UserProfile

def crear_administrador():
    username = 'admin'
    email = 'admin@agrosft.com'
    password = 'adminpassword123'

    print(f"Creando o actualizando usuario administrador: {username}...")
    
    # Crear o obtener el usuario
    user, created = User.objects.get_or_create(username=username)
    user.email = email
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.save()

    # Asegurar que tenga su perfil y rol de administrador
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.rol = 'admin'
    profile.save()

    if created:
        print("¡El administrador fue CREADO exitosamente!")
    else:
        print("¡La contraseña y permisos del administrador fueron ACTUALIZADOS exitosamente!")
        
    print("-" * 30)
    print("TUS CREDENCIALES:")
    print(f"Usuario: {username}")
    print(f"Contraseña: {password}")
    print("-" * 30)

if __name__ == '__main__':
    crear_administrador()
