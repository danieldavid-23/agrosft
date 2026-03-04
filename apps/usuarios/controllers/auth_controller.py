from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.views import View
from django.utils.decorators import method_decorator
from core.controllers.base_controller import BaseController
from apps.usuarios.forms.auth_forms import RegistroForm, LoginForm, PerfilForm
from apps.usuarios.services.terminos_service import TerminosService


class RegistroView(BaseController, View):
    """Vista para registro de nuevos usuarios"""
    
    def get(self, request):
        # Si ya está autenticado, redirigir
        if request.user.is_authenticated:
            return redirect('home')
        
        form = RegistroForm()
        terminos = TerminosService.obtener_terminos_activos()
        
        return render(request, 'usuarios/registro.html', {
            'form': form,
            'terminos': terminos
        })
    
    def post(self, request):
        form = RegistroForm(request.POST)
        acepto_terminos = request.POST.get('acepto_terminos')
        
        if form.is_valid() and acepto_terminos:
            user = form.save()
            
            # Autenticar y loguear automáticamente
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1']
            )
            
            if user:
                login(request, user)
                
                # Registrar aceptación de términos
                termino_activo = TerminosService.obtener_terminos_activos()
                if termino_activo:
                    TerminosService.aceptar_terminos(user, request)
                
                messages.success(request, f"¡Bienvenido {user.username}! Te has registrado exitosamente.")
                
                # Redirigir a completar perfil o al inicio
                return redirect('usuarios:perfil')
        
        if not acepto_terminos:
            messages.error(request, "Debes aceptar los términos y condiciones")
        
        terminos = TerminosService.obtener_terminos_activos()
        return render(request, 'usuarios/registro.html', {
            'form': form,
            'terminos': terminos
        })


class LoginView(BaseController, View):
    """Vista para inicio de sesión"""
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('home')
        
        form = LoginForm()
        return render(request, 'usuarios/login.html', {'form': form})
    
    def post(self, request):
        form = LoginForm(request.POST)
        
        if form.is_valid():
            user = form.user
            login(request, user)
            
            messages.success(request, f"¡Bienvenido de nuevo {user.username}!")
            
            # Redirigir a la página solicitada o al inicio
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        
        return render(request, 'usuarios/login.html', {'form': form})


class LogoutView(BaseController, View):
    """Vista para cerrar sesión"""
    
    def get(self, request):
        logout(request)
        messages.info(request, "Has cerrado sesión correctamente")
        return redirect('usuarios:login')


@method_decorator(login_required, name='dispatch')
class PerfilView(BaseController, View):
    """Vista para ver y editar perfil de usuario"""
    
    def get(self, request):
        form = PerfilForm(instance=request.user)
        return render(request, 'usuarios/perfil.html', {
            'form': form,
            'user': request.user
        })
    
    def post(self, request):
        form = PerfilForm(request.POST, instance=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Tu perfil ha sido actualizado correctamente")
            return redirect('usuarios:perfil')
        
        return render(request, 'usuarios/perfil.html', {
            'form': form,
            'user': request.user
        })


@method_decorator(login_required, name='dispatch')
class CambiarPasswordView(BaseController, View):
    """Vista para cambiar contraseña"""
    
    def get(self, request):
        form = PasswordChangeForm(user=request.user)
        return render(request, 'usuarios/cambiar_password.html', {'form': form})
    
    def post(self, request):
        form = PasswordChangeForm(user=request.user, data=request.POST)
        
        if form.is_valid():
            user = form.save()
            # Mantener la sesión activa después de cambiar contraseña
            update_session_auth_hash(request, user)
            messages.success(request, "Tu contraseña ha sido cambiada exitosamente")
            return redirect('usuarios:perfil')
        
        return render(request, 'usuarios/cambiar_password.html', {'form': form})