import os
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.usuarios.models.profile_model import UserProfile

def cambiar_rol_y_contrasena():
    print("=== Cambiar Rol a Agricultor y Restablecer Contraseña ===")
    email = input("Introduce tu correo electrónico (ej. danibaron456@gmail.com): ").strip()
    
    try:
        # Buscar el usuario por correo
        user = User.objects.get(email=email)
        
        # 1. Cambiar el rol
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.rol = 'agricultor'
        profile.save()
        print(f"\n✅ El rol del usuario '{user.username}' ha sido cambiado a 'agricultor'.")
        
        # 2. Restablecer la contraseña
        print("\nComo no recuerdas tu contraseña, vamos a crear una nueva.")
        nueva_password = input("Introduce tu nueva contraseña: ").strip()
        
        if nueva_password:
            user.set_password(nueva_password)
            user.save()
            print(f"✅ ¡Éxito! Tu contraseña ha sido actualizada.")
        else:
            print("⚠️ No ingresaste una contraseña válida. La contraseña no fue cambiada.")
            
    except User.DoesNotExist:
        print(f"\n❌ Error: No se encontró ningún usuario con el correo '{email}'.")
    except User.MultipleObjectsReturned:
        print(f"\n❌ Error: Hay más de un usuario con el correo '{email}'. Por favor, contacta a un administrador.")
    except Exception as e:
        print(f"\n❌ Ha ocurrido un error inesperado: {str(e)}")

if __name__ == '__main__':
    cambiar_rol_y_contrasena()
