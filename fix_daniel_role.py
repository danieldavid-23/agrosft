import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.usuarios.models.profile_model import UserProfile

def fix_user_role():
    try:
        user = User.objects.get(username='daniel')
        profile, created = UserProfile.objects.get_or_create(user=user)
        profile.rol = 'agricultor'
        profile.save()
        print(f"Successfully set role 'agricultor' for user 'daniel'.")
    except User.DoesNotExist:
        print("User 'daniel' does not exist.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    fix_user_role()
