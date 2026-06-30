"""
Token generator personalizado para recuperación de contraseña de AgroSFT.

El default_token_generator de Django llama a user.get_email_field_name()
en PasswordResetTokenGenerator._make_hash_value(), método que solo existe
en AbstractBaseUser. El modelo Tblusuarios hereda de models.Model directamente,
por lo que no tiene ese método.

Esta implementación sobreescribe _make_hash_value() para usar directamente
los campos reales de Tblusuarios: user.correo y user.contraseña.
El token incluye:
- El PK del usuario
- El timestamp del momento de creación (para expiración)
- El hash actual de la contraseña (para invalidar si cambia)
- El correo del usuario (campo real: user.correo)

Esto garantiza exactamente las mismas propiedades de seguridad que el
token nativo de Django: expira en tiempo configurable y se invalida
automáticamente si se cambia la contraseña o el correo.
"""

from django.contrib.auth.tokens import PasswordResetTokenGenerator


class TblusuariosPasswordResetTokenGenerator(PasswordResetTokenGenerator):
    """
    Generador de tokens de recuperación de contraseña compatible con
    el modelo Tblusuarios (hereda de models.Model, no de AbstractBaseUser).
    """

    def _make_hash_value(self, user, timestamp):
        """
        Genera el valor hash para el token.
        
        Se adapta para usar los campos reales de Tblusuarios:
        - user.pk         → identificador único del usuario
        - user.contraseña → hash actual de contraseña (invalida el token si cambia)
        - user.correo     → campo de correo real del modelo
        - timestamp       → para expiración del token
        - user.is_active  → invalida si se desactiva la cuenta
        """
        # Obtener el correo y contraseña directamente de los campos del modelo
        correo = user.correo or ""
        contrasena = user.contraseña or ""
        return f"{user.pk}{timestamp}{contrasena}{correo}{user.is_active}"


# Instancia singleton, equivalente al default_token_generator de Django
agrosft_token_generator = TblusuariosPasswordResetTokenGenerator()
