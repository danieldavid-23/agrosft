from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.views.generic import CreateView, FormView, View
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView as DjangoLogoutView
from django.contrib.auth import get_user_model
from apps.usuarios.forms.auth_forms import RegistroForm, LoginForm, PerfilForm
from apps.usuarios.models.profile_model import Tblusuarios
from django.db import connection
from django.contrib.auth import logout
from django.http import JsonResponse
from apps.usuarios.services.terminos_service import TerminosService
from core.controllers.base_controller import BaseController
from django.utils import timezone
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.contrib.auth.hashers import make_password
import json
import urllib.request
import urllib.parse


def tabla_existe(table_name):
    """Verifica si una tabla existe en la base de datos"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT 1 FROM {table_name} LIMIT 1")
        return True
    except:
        return False

def columna_existe(table_name, column_name):
    """Verifica si una columna existe en una tabla"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"DESCRIBE {table_name}")
            columns = [row[0] for row in cursor.fetchall()]
            return column_name in columns
    except:
        return False


class RegistroView(View):
    """Vista para el registro de nuevos usuarios"""
    template_name = 'usuarios/registro.html'
    form_class = RegistroForm
    success_url = reverse_lazy('usuarios:login')
    
    def get(self, request):
        form = self.form_class()
        context = {
            'form': form,
            'titulo': 'Registro de Usuario'
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        form = self.form_class(request.POST)
        context = {
            'form': form,
            'titulo': 'Registro de Usuario'
        }
        
        # Verificar si la tabla existe antes de intentar registrar
        if not tabla_existe('tblusuarios'):
            messages.error(request, "La tabla de usuarios no existe en la base de datos.")
            return render(request, self.template_name, context)
        
        # Verificar si las columnas necesarias existen
        if not columna_existe('tblusuarios', 'contraseña'):
            messages.error(request, "La columna de contraseña no existe en la base de datos.")
            return render(request, self.template_name, context)
        
        if form.is_valid():
            try:
                # Proceder con el registro normal
                user = form.save()
                messages.success(request, 'Usuario registrado exitosamente. Puedes iniciar sesión.')
                return redirect(self.success_url)
            except Exception as e:
                messages.error(request, f'Error al registrar usuario: {str(e)}')
                return render(request, self.template_name, context)
        else:
            return render(request, self.template_name, context)


@method_decorator(never_cache, name='dispatch')
class LoginView(View):
    """Vista para el inicio de sesión de usuarios"""
    template_name = 'usuarios/login.html'
    form_class = LoginForm
    next_page = 'home'
    
    def dispatch(self, request, *args, **kwargs):
        # Si el usuario ya está autenticado, redirigir al inventario
        if request.user.is_authenticated:
            return redirect(reverse_lazy('inventario:listar'))
        response = super().dispatch(request, *args, **kwargs)
        # Anti-cache: forzar que el navegador no guarde esta página en caché
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response

    def get(self, request):
        form = self.form_class()
        context = {
            'form': form,
            'titulo': 'Iniciar Sesión',
            'GOOGLE_CLIENT_ID': getattr(settings, 'GOOGLE_CLIENT_ID', ''),
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        form = self.form_class(request.POST)
        context = {
            'form': form,
            'titulo': 'Iniciar Sesión'
        }
        
        # Verificar si la tabla existe antes de intentar iniciar sesión
        if not tabla_existe('tblusuarios'):
            messages.error(request, "La tabla de usuarios no existe en la base de datos.")
            return render(request, self.template_name, context)
        
        # Verificar si las columnas necesarias existen
        if not columna_existe('tblusuarios', 'contraseña'):
            messages.error(request, "La columna de contraseña no existe en la base de datos.")
            return render(request, self.template_name, context)
        
        if form.is_valid():
            # Obtener credenciales
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # Intentar autenticar usando el backend personalizado
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    login(request, user)
                    
                    # Actualizar última conexión
                    try:
                        user.ultima_conexion = timezone.now()
                        user.save(update_fields=['ultima_conexion'])
                    except:
                        pass  # No actualizar si no existe el campo
                    
                    messages.success(request, f'Bienvenido, {user.get_full_name()}!')
                    
                    # Redirigir según corresponda
                    next_url = self.next_page
                    if next_url == 'home':
                        next_url = reverse_lazy('inventario:listar')
                    
                    return redirect(next_url)
                else:
                    messages.error(request, 'Tu cuenta está inactiva.')
                    return render(request, self.template_name, context)
            else:
                messages.error(request, 'Credenciales inválidas.')
                return render(request, self.template_name, context)
        else:
            return render(request, self.template_name, context)
    
    def get_context_data(self, **kwargs):
        context = kwargs
        context['titulo'] = 'Iniciar Sesión'
        return context


@method_decorator(never_cache, name='dispatch')
class LogoutView(DjangoLogoutView):
    """Vista para cerrar sesión de usuarios"""
    next_page = 'usuarios:login'  # Redirigir al login después de cerrar sesión
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, 'Has cerrado sesión exitosamente.')
        response = super().dispatch(request, *args, **kwargs)
        # Anti-cache estricto para que el botón "atrás" no restaure la sesión
        if hasattr(response, '__setitem__'):
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        return response


class GoogleAuthView(View):
    """Vista para autenticación con Google OAuth2"""
    
    def post(self, request):
        try:
            data = json.loads(request.body)
            credential = data.get('credential')
            
            if not credential:
                return JsonResponse({'success': False, 'error': 'Token no proporcionado'}, status=400)
            
            # Verificar el token de Google
            google_client_id = getattr(settings, 'GOOGLE_CLIENT_ID', '')
            verify_url = f'https://oauth2.googleapis.com/tokeninfo?id_token={credential}'
            
            try:
                with urllib.request.urlopen(verify_url, timeout=10) as response:
                    payload = json.loads(response.read().decode())
            except Exception as e:
                return JsonResponse({'success': False, 'error': 'Token de Google inválido'}, status=400)
            
            # Verificar que el audience coincida
            if payload.get('aud') != google_client_id:
                return JsonResponse({'success': False, 'error': 'Token no válido para esta aplicación'}, status=400)
            
            # Obtener datos del usuario desde Google
            google_email = payload.get('email', '')
            google_nombre = payload.get('given_name', '')
            google_apellido = payload.get('family_name', '')
            google_id = payload.get('sub', '')
            email_verified = payload.get('email_verified', 'false')
            
            if not google_email:
                return JsonResponse({'success': False, 'error': 'No se pudo obtener el correo de Google'}, status=400)
            
            # Buscar si el usuario ya existe por correo
            try:
                user = Tblusuarios.objects.get(correo=google_email)
                # Usuario ya existe - iniciar sesión
                login(request, user, backend='apps.usuarios.backends.TblusuariosAuthBackend')
                try:
                    user.ultima_conexion = timezone.now()
                    user.save(update_fields=['ultima_conexion'])
                except:
                    pass
                messages.success(request, f'¡Bienvenido, {user.get_full_name() or google_nombre}!')
                return JsonResponse({
                    'success': True, 
                    'redirect': str(reverse_lazy('inventario:listar')),
                    'message': 'Sesión iniciada correctamente'
                })
            except Tblusuarios.DoesNotExist:
                # Usuario nuevo - registrar automáticamente
                try:
                    import secrets
                    temp_password = secrets.token_urlsafe(32)
                    user = Tblusuarios(
                        correo=google_email,
                        nombres=google_nombre or google_email.split('@')[0],
                        apellidos=google_apellido or '',
                        contraseña=make_password(temp_password),
                        is_active=True,
                    )
                    user.save()
                    login(request, user, backend='apps.usuarios.backends.TblusuariosAuthBackend')
                    messages.success(request, f'¡Cuenta creada con Google! Bienvenido, {user.get_full_name() or google_nombre}.')
                    return JsonResponse({
                        'success': True, 
                        'redirect': str(reverse_lazy('inventario:listar')),
                        'message': 'Cuenta creada e ingresado correctamente'
                    })
                except Exception as e:
                    return JsonResponse({'success': False, 'error': f'Error al crear usuario: {str(e)}'}, status=500)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Datos inválidos'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)


class PerfilView(View):
    """Vista para ver y editar el perfil del usuario"""
    
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('usuarios:login')
        
        # Verificar si la tabla existe antes de intentar acceder al perfil
        if not tabla_existe('tblusuarios'):
            messages.error(request, "La tabla de usuarios no existe en la base de datos.")
            return redirect('usuarios:login')
        
        # Verificar si las columnas necesarias existen
        if not columna_existe('tblusuarios', 'contraseña'):
            messages.error(request, "La columna de contraseña no existe en la base de datos.")
            return redirect('usuarios:login')
        
        form = PerfilForm(instance=request.user)
        context = {
            'form': form,
            'titulo': 'Mi Perfil'
        }
        return render(request, 'usuarios/perfil.html', context)
    
    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('usuarios:login')
        
        # Verificar si la tabla existe antes de intentar actualizar el perfil
        if not tabla_existe('tblusuarios'):
            messages.error(request, "La tabla de usuarios no existe en la base de datos.")
            return redirect('usuarios:login')
        
        form = PerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('usuarios:perfil')
        else:
            context = {
                'form': form,
                'titulo': 'Mi Perfil'
            }
            return render(request, 'usuarios/perfil.html', context)


from django.urls import reverse_lazy


class CambiarPasswordView(View):
    """Vista para cambiar la contraseña del usuario"""
    
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('usuarios:login')
        
        # Verificar si la tabla existe antes de intentar cambiar contraseña
        if not tabla_existe('tblusuarios'):
            messages.error(request, "La tabla de usuarios no existe en la base de datos.")
            return redirect('usuarios:login')
        
        # Verificar si las columnas necesarias existen
        if not columna_existe('tblusuarios', 'contraseña'):
            messages.error(request, "La columna de contraseña no existe en la base de datos.")
            return redirect('usuarios:login')
        
        context = {
            'titulo': 'Cambiar Contraseña'
        }
        return render(request, 'usuarios/cambiar_password.html', context)
    
    def post(self, request):
        if not request.user.is_authenticated:
            return redirect('usuarios:login')
        
        # Verificar si la tabla existe antes de intentar cambiar contraseña
        if not tabla_existe('tblusuarios'):
            messages.error(request, "La tabla de usuarios no existe en la base de datos.")
            return redirect('usuarios:login')
        
        # Verificar si las columnas necesarias existen
        if not columna_existe('tblusuarios', 'contraseña'):
            messages.error(request, "La columna de contraseña no existe en la base de datos.")
            return redirect('usuarios:login')
        
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Verificar contraseña actual
        if not request.user.check_password(current_password):
            messages.error(request, 'La contraseña actual es incorrecta.')
            return self.get(request)
        
        # Verificar que las nuevas contraseñas coincidan
        if new_password != confirm_password:
            messages.error(request, 'Las nuevas contraseñas no coinciden.')
            return self.get(request)
        
        # Cambiar la contraseña
        request.user.set_password(new_password)
        request.user.save()
        
        messages.success(request, 'Contraseña cambiada exitosamente.')
        return redirect('usuarios:perfil')


class UserPasswordResetView(View):
    """Vista para restablecer la contraseña"""
    
    def get(self, request):
        context = {
            'titulo': 'Restablecer Contraseña'
        }
        return render(request, 'usuarios/password_reset.html', context)
    
    def post(self, request):
        email = request.POST.get('email')
        # Lógica para enviar correo de restablecimiento de contraseña
        messages.success(request, 'Instrucciones para restablecer la contraseña enviadas a su correo.')
        return redirect('usuarios:login')


class UserPasswordResetDoneView(View):
    """Vista para confirmar que se envió el correo de restablecimiento"""
    
    def get(self, request):
        context = {
            'titulo': 'Correo de Restablecimiento Enviado'
        }
        return render(request, 'usuarios/password_reset_done.html', context)


class UserPasswordResetConfirmView(View):
    """Vista para confirmar el restablecimiento de contraseña"""
    
    def get(self, request, uidb64, token):
        context = {
            'titulo': 'Confirmar Restablecimiento de Contraseña',
            'uidb64': uidb64,
            'token': token
        }
        return render(request, 'usuarios/password_reset_confirm.html', context)
    
    def post(self, request, uidb64, token):
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if new_password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden.')
            return self.get(request, uidb64, token)
        
        # Lógica para confirmar el restablecimiento de contraseña
        messages.success(request, 'Contraseña restablecida exitosamente.')
        return redirect('usuarios:login')


class UserPasswordResetCompleteView(View):
    """Vista para confirmar que se completó el restablecimiento de contraseña"""
    
    def get(self, request):
        context = {
            'titulo': 'Restablecimiento de Contraseña Completado'
        }
        return render(request, 'usuarios/password_reset_complete.html', context)