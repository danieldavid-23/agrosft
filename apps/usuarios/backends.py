from django.contrib.auth.backends import BaseBackend
from .models import Tblusuarios
from django.contrib.auth.hashers import check_password
from django.db import connection


class TblusuariosAuthBackend(BaseBackend):
    """
    Backend de autenticación personalizado para usar el modelo Tblusuarios
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Autentica un usuario basado en correo y contraseña
        """
        if username is None or password is None:
            return None
        
        try:
            # Verificar si la tabla existe y tiene la estructura correcta
            if not self.tabla_existe('tblusuarios'):
                return None
            
            # Verificar si la columna contraseña existe (con tilde, según la base de datos real)
            if not self.columna_existe('tblusuarios', 'contraseña'):
                return None
            
            # Buscar usuario por correo (o nombre de usuario si aplica)
            user = Tblusuarios.objects.get(correo=username)
            
            # Verificar si la cuenta está activa usando el campo is_active
            if not user.is_active:
                return None
            
            # Verificar la contraseña
            if user.check_password(password):
                return user
            else:
                return None
                
        except Tblusuarios.DoesNotExist:
            # Run the default password hasher once to reduce timing difference
            # between an existing and a non-existing user (#20760).
            check_password(password, "")
            return None
        except Exception as e:
            # Log the error for debugging
            print(f"Error en autenticación: {e}")
            return None

    def get_user(self, user_id):
        """
        Obtiene un usuario por ID
        """
        try:
            # Verificar si la tabla existe y tiene la estructura correcta
            if not self.tabla_existe('tblusuarios'):
                return None
            
            # Verificar si la columna contraseña existe (con tilde, según la base de datos real)
            if not self.columna_existe('tblusuarios', 'contraseña'):
                return None
            
            return Tblusuarios.objects.get(id_users=user_id)
        except Tblusuarios.DoesNotExist:
            return None

    def tabla_existe(self, table_name):
        """Verifica si una tabla existe en la base de datos"""
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT 1 FROM {table_name} LIMIT 1")
            return True
        except:
            return False

    def columna_existe(self, table_name, column_name):
        """Verifica si una columna existe en una tabla"""
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"DESCRIBE {table_name}")
                columns = [row[0] for row in cursor.fetchall()]
                return column_name in columns
        except:
            return False

    def get_user_permissions(self, user_obj, obj=None):
        """
        Retorna los permisos de usuario (vacío para este backend simple)
        """
        return set()

    def get_group_permissions(self, user_obj, obj=None):
        """
        Retorna los permisos de grupo (vacío para este backend simple)
        """
        return set()

    def get_all_permissions(self, user_obj, obj=None):
        """
        Retorna todos los permisos (vacío para este backend simple)
        """
        return set()

    def has_perm(self, user_obj, perm, obj=None):
        """
        Verifica si el usuario tiene un permiso específico (siempre True para este backend simple)
        """
        return True

    def has_module_perms(self, user_obj, app_label):
        """
        Verifica si el usuario tiene permisos para una aplicación específica (siempre True para este backend simple)
        """
        return True