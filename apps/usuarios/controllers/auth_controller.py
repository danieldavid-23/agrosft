from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.views.generic import CreateView, FormView, View
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView as DjangoLoginView, LogoutView as DjangoLogoutView
from django.contrib.auth import get_user_model
from apps.usuarios.forms.auth_forms import RegistroForm, LoginForm, PerfilForm, PasswordResetRequestForm
from apps.usuarios.models.profile_model import Tblusuarios, UserProfile
from django.db import connection
from django.contrib.auth import logout
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse
from apps.usuarios.services.email_service import send_password_reset_email
from apps.usuarios.utils.password_reset_tokens import agrosft_token_generator
from apps.usuarios.forms.auth_forms import NuevaPasswordForm
from django.http import JsonResponse
from apps.usuarios.services.terminos_service import TerminosService
from core.controllers.base_controller import BaseController
from django.utils import timezone
import os


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


class LoginView(View):
    """Vista para el inicio de sesión de usuarios"""
    template_name = 'usuarios/login.html'
    form_class = LoginForm
    
    def get(self, request):
        form = self.form_class()
        context = {
            'form': form,
            'titulo': 'Iniciar Sesión'
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
                    
                    # Redirigir al marketplace (página principal)
                    next_url = request.GET.get('next', None)
                    if next_url:
                        return redirect(next_url)
                    return redirect('inventario:marketplace')
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


class LogoutView(DjangoLogoutView):
    """Vista para cerrar sesión de usuarios"""
    next_page = 'usuarios:login'  # Redirigir al login después de cerrar sesión
    http_method_names = ['get', 'post', 'head', 'options']  # Permitir GET para enlaces <a>
    
    def get(self, request, *args, **kwargs):
        """Soporte para cierre de sesión mediante GET (para enlaces directos <a>)"""
        logout(request)
        messages.info(request, 'Has cerrado sesión exitosamente.')
        return redirect(self.next_page)

    def post(self, request, *args, **kwargs):
        """Cierre de sesión mediante POST"""
        logout(request)
        messages.info(request, 'Has cerrado sesión exitosamente.')
        return redirect(self.next_page)


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
        
        # Obtener perfil con imagen
        profile = UserProfile.get_or_create_for_user(request.user)
        
        context = {
            'form': form,
            'titulo': 'Mi Perfil',
            'profile': profile,
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
            
            # Manejar subida de imagen de perfil
            imagen = request.FILES.get('imagen_perfil')
            if imagen:
                profile = UserProfile.get_or_create_for_user(request.user)
                if profile is not None:
                    # Eliminar imagen anterior si existe
                    if profile.imagen_perfil:
                        try:
                            old_path = profile.imagen_perfil.path
                            if os.path.isfile(old_path):
                                os.remove(old_path)
                        except (ValueError, OSError):
                            pass
                    profile.imagen_perfil = imagen
                    profile.save()
            
            # Manejar eliminación de imagen de perfil
            if request.POST.get('remove_photo') == 'true':
                profile = UserProfile.get_or_create_for_user(request.user)
                if profile is not None and profile.imagen_perfil:
                    try:
                        old_path = profile.imagen_perfil.path
                        if os.path.isfile(old_path):
                            os.remove(old_path)
                    except (ValueError, OSError):
                        pass
                    profile.imagen_perfil = None
                    profile.save()
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True})
            
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('usuarios:perfil')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
            profile = UserProfile.get_or_create_for_user(request.user)
            context = {
                'form': form,
                'titulo': 'Mi Perfil',
                'profile': profile,
            }
            return render(request, 'usuarios/perfil.html', context)


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
        form = PasswordResetRequestForm()
        context = {
            'form': form,
            'titulo': 'Restablecer Contraseña'
        }
        return render(request, 'usuarios/password_reset_form.html', context)
    
    def post(self, request):
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            try:
                user = Tblusuarios.objects.get(correo__iexact=email, is_active=True)
                # Generar token y uid
                token = agrosft_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                # Construir link absoluto
                domain = request.get_host()
                protocol = 'https' if request.is_secure() else 'http'
                confirm_url = reverse('usuarios:password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
                reset_link = f"{protocol}://{domain}{confirm_url}"
                
                # Nombre del destinatario
                to_name = user.get_full_name()
                
                # Enviar correo
                send_password_reset_email(user.correo, to_name, reset_link)
            except Tblusuarios.DoesNotExist:
                # Evitar enumeración de usuarios
                pass
            except Exception as e:
                import logging
                logger = logging.getLogger('apps.usuarios.controllers.auth_controller')
                logger.error(f"Error en proceso de password_reset: {str(e)}")
            
            return redirect('usuarios:password_reset_done')
        
        context = {
            'form': form,
            'titulo': 'Restablecer Contraseña'
        }
        return render(request, 'usuarios/password_reset_form.html', context)


class UserPasswordResetDoneView(View):
    """Vista para confirmar que se envió el correo de restablecimiento"""
    
    def get(self, request):
        context = {
            'titulo': 'Correo de Restablecimiento Enviado'
        }
        return render(request, 'usuarios/password_reset_done.html', context)


class UserPasswordResetConfirmView(View):
    """Vista para confirmar el restablecimiento de contraseña"""
    
    def get_user(self, uidb64):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            return Tblusuarios.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Tblusuarios.DoesNotExist):
            return None
    
    def get(self, request, uidb64, token):
        user = self.get_user(uidb64)
        validlink = False
        form = None
        
        if user is not None and agrosft_token_generator.check_token(user, token):
            validlink = True
            form = NuevaPasswordForm()
            
        context = {
            'titulo': 'Confirmar Restablecimiento de Contraseña',
            'validlink': validlink,
            'form': form,
            'uidb64': uidb64,
            'token': token
        }
        return render(request, 'usuarios/password_reset_confirm.html', context)
    
    def post(self, request, uidb64, token):
        user = self.get_user(uidb64)
        if user is None or not agrosft_token_generator.check_token(user, token):
            context = {
                'titulo': 'Confirmar Restablecimiento de Contraseña',
                'validlink': False,
                'form': None,
                'uidb64': uidb64,
                'token': token
            }
            return render(request, 'usuarios/password_reset_confirm.html', context)
            
        form = NuevaPasswordForm(request.POST)
        if form.is_valid():
            # Guardar usando exactamente el mismo mecanismo que el resto del proyecto:
            # set_password() aplica make_password() al campo contraseña,
            # luego save() persiste en BD con update_fields para mayor seguridad.
            user.set_password(form.cleaned_data['new_password1'])
            user.save(update_fields=['contraseña'])
            messages.success(request, 'Tu contraseña ha sido restablecida exitosamente.')
            return redirect('usuarios:password_reset_complete')
            
        context = {
            'titulo': 'Confirmar Restablecimiento de Contraseña',
            'validlink': True,
            'form': form,
            'uidb64': uidb64,
            'token': token
        }
        return render(request, 'usuarios/password_reset_confirm.html', context)


class UserPasswordResetCompleteView(View):
    """Vista para confirmar que se completó el restablecimiento de contraseña"""
    
    def get(self, request):
        context = {
            'titulo': 'Restablecimiento de Contraseña Completado'
        }
        return render(request, 'usuarios/password_reset_complete.html', context)