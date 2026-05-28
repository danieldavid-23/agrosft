import jwt
from django.conf import settings
from datetime import datetime, timedelta
from apps.usuarios.models import Tblusuarios  # Corregido el path del modelo
from django.contrib.auth.hashers import check_password


class CustomAuthentication:
    """
    Sistema de autenticación personalizado que no depende de las tablas del sistema de Django
    """
    
    @staticmethod
    def generate_token(user):
        """
        Genera un token JWT para un usuario
        """
        payload = {
            'user_id': user.id_users,
            'email': user.correo,
            'exp': datetime.utcnow() + timedelta(days=7),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        return token
    
    @staticmethod
    def verify_token(token):
        """
        Verifica un token JWT y devuelve el ID del usuario si es válido
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            if user_id:
                # Verificar que el usuario aún exista y esté activo
                try:
                    user = Tblusuarios.objects.get(id_users=user_id)
                    if user.estado == 'activo':
                        return user
                except Tblusuarios.DoesNotExist:
                    return None
            return None
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    @staticmethod
    def authenticate_user(username, password):
        """
        Autentica un usuario por nombre de usuario/correo y contraseña
        """
        try:
            # Buscar usuario por correo
            user = Tblusuarios.objects.get(correo=username)
            
            # Verificar si la cuenta está activa
            if user.estado != 'activo':
                return None
            
            # Verificar la contraseña
            if user.check_password(password):
                # Actualizar última conexión
                user.ultima_conexion = datetime.now()
                user.save(update_fields=['ultima_conexion'])
                
                return user
            else:
                return None
                
        except Tblusuarios.DoesNotExist:
            # Para seguridad, no revelar si el usuario existe o no
            return None
    
    @staticmethod
    def get_user_by_id(user_id):
        """
        Obtiene un usuario por ID
        """
        try:
            return Tblusuarios.objects.get(id_users=user_id)
        except Tblusuarios.DoesNotExist:
            return None