import json
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

User = get_user_model()


@method_decorator(csrf_exempt, name='dispatch')
class PasswordResetAPIView(View):
    """
    API endpoint para solicitar recuperación de contraseña.
    POST /api/auth/password-reset/
    Body: {"email": "usuario@ejemplo.com"}
    """

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Formato JSON inválido'
            }, status=400)

        email = data.get('email', '').strip().lower()

        if not email:
            return JsonResponse({
                'success': False,
                'error': 'El correo electrónico es obligatorio'
            }, status=400)

        # Buscar usuarios con este email
        users = User.objects.filter(email__iexact=email)

        if users.exists():
            for user in users:
                # Generar token y uid
                token = default_token_generator.make_token(user)
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

                # Preparar contexto para el email
                domain = getattr(settings, 'DEFAULT_DOMAIN', 'localhost:8000')
                protocol = getattr(settings, 'DEFAULT_PROTOCOL', 'http')

                context = {
                    'email': user.email,
                    'domain': domain,
                    'site_name': 'AgroSFT',
                    'uid': uidb64,
                    'user': user,
                    'token': token,
                    'protocol': protocol,
                }

                # Renderizar mensaje de email en texto plano y HTML
                subject = 'Recuperación de contraseña - AgroSFT'
                email_body_txt = render_to_string(
                    'usuarios/password_reset_email.txt',
                    context
                )
                email_body_html = render_to_string(
                    'usuarios/password_reset_email.html',
                    context
                )

                # Enviar email (se imprime en consola o se envía por SMTP real según la configuración)
                send_mail(
                    subject=subject,
                    message=email_body_txt,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False,
                    html_message=email_body_html,
                )

        # Siempre devolver éxito para no revelar si el email existe o no
        return JsonResponse({
            'success': True,
            'message': 'Si existe una cuenta con ese correo, hemos enviado las instrucciones para recuperar tu contraseña.'
        })


@method_decorator(csrf_exempt, name='dispatch')
class PasswordResetValidateTokenAPIView(View):
    """
    API endpoint para validar si un token de recuperación es válido.
    GET /api/auth/password-reset/validate/<uidb64>/<token>/
    """

    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return JsonResponse({
                'valid': False,
                'error': 'Token inválido o expirado'
            }, status=400)

        if user is not None and default_token_generator.check_token(user, token):
            return JsonResponse({
                'valid': True,
                'uidb64': uidb64,
                'token': token,
                'message': 'El token es válido'
            })

        return JsonResponse({
            'valid': False,
            'error': 'Token inválido o expirado'
        }, status=400)


@method_decorator(csrf_exempt, name='dispatch')
class PasswordResetConfirmAPIView(View):
    """
    API endpoint para confirmar el restablecimiento de contraseña.
    POST /api/auth/password-reset/confirm/
    Body: {"uidb64": "...", "token": "...", "new_password": "...", "new_password2": "..."}
    """

    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Formato JSON inválido'
            }, status=400)

        uidb64 = data.get('uidb64', '')
        token = data.get('token', '')
        new_password = data.get('new_password', '')
        new_password2 = data.get('new_password2', '')

        # Validaciones básicas
        if not all([uidb64, token, new_password, new_password2]):
            return JsonResponse({
                'success': False,
                'error': 'Todos los campos son obligatorios: uidb64, token, new_password, new_password2'
            }, status=400)

        if new_password != new_password2:
            return JsonResponse({
                'success': False,
                'error': 'Las contraseñas no coinciden'
            }, status=400)

        # Validar complejidad de contraseña
        try:
            validate_password(new_password)
        except ValidationError as e:
            return JsonResponse({
                'success': False,
                'error': ' '.join(e.messages)
            }, status=400)

        # Validar usuario y token
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return JsonResponse({
                'success': False,
                'error': 'Enlace de recuperación inválido o expirado'
            }, status=400)

        if user is None or not default_token_generator.check_token(user, token):
            return JsonResponse({
                'success': False,
                'error': 'Enlace de recuperación inválido o expirado'
            }, status=400)

        # Cambiar contraseña
        user.set_password(new_password)
        user.save()

        return JsonResponse({
            'success': True,
            'message': 'Tu contraseña ha sido restablecida exitosamente. Ya puedes iniciar sesión con tu nueva contraseña.'
        })
