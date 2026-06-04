from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from apps.usuarios.models.profile_model import Tblusuarios
from apps.usuarios.utils.authentication import CustomAuthentication
import json

# Vista básica para la página de inicio con soporte para autenticación y plantilla


def home_page(request):
    """
    Maneja la vista de la página de inicio con soporte para autenticación
    """
    # Verificar si el usuario está autenticado
    if 'user_id' in request.session:
        user_id = request.session['user_id']
        try:
            user = Tblusuarios.objects.get(id_users=user_id)
            context = {
                'user': user,
                'is_authenticated': True,
            }
            return render(request, 'usuarios/home.html', context)
        except Tblusuarios.DoesNotExist:
            pass
    
    # Si no está autenticado, mostrar página de inicio básica
    context = {
        'is_authenticated': False,
    }
    return render(request, 'usuarios/home.html', context)


def login_view(request):
    """
    Maneja el proceso de inicio de sesión personalizado
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = CustomAuthentication.authenticate_user(email, password)
        
        if user:
            # Crear sesión personalizada
            request.session['user_id'] = user.id_users
            request.session['user_email'] = user.correo
            request.session['user_nombre'] = f"{user.nombres} {user.apellidos}"
            request.session['user_rol'] = user.rol
            
            # Opcional: también podríamos generar un token
            token = CustomAuthentication.generate_token(user)
            request.session['auth_token'] = token
            
            messages.success(request, f'Bienvenido, {user.nombres}!')
            
            # Redirigir según el rol
            if user.rol == 'admin':
                return redirect('admin_dashboard')  # Ruta personalizada
            elif user.rol == 'agricultor':
                return redirect('agricultor_dashboard')  # Ruta personalizada
            else:
                return redirect('cliente_dashboard')  # Ruta personalizada
        else:
            messages.error(request, 'Credenciales inválidas.')
    
    return render(request, 'usuarios/login.html')


def logout_view(request):
    """
    Maneja el proceso de cierre de sesión
    """
    # Limpiar la sesión personalizada
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'user_email' in request.session:
        del request.session['user_email']
    if 'user_nombre' in request.session:
        del request.session['user_nombre']
    if 'user_rol' in request.session:
        del request.session['user_rol']
    if 'auth_token' in request.session:
        del request.session['auth_token']
    
    messages.success(request, 'Sesión cerrada exitosamente.')
    return redirect('home')


def register_view(request):
    """
    Maneja el proceso de registro de nuevos usuarios
    """
    if request.method == 'POST':
        # Obtener datos del formulario
        nombres = request.POST.get('nombres')
        apellidos = request.POST.get('apellidos')
        email = request.POST.get('email')
        password = request.POST.get('password')
        telefono = request.POST.get('telefono', '')
        
        # Validar que el email no exista
        if Tblusuarios.objects.filter(correo=email).exists():
            messages.error(request, 'El correo electrónico ya está registrado.')
            return render(request, 'usuarios/register.html')
        
        # Crear nuevo usuario
        try:
            user = Tblusuarios(
                nombres=nombres,
                apellidos=apellidos,
                correo=email,
                telefono=telefono,
                estado='activo',
                rol='cliente'  # Por defecto
            )
            user.set_password(password)
            user.save()
            
            messages.success(request, 'Usuario registrado exitosamente. Ahora puedes iniciar sesión.')
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f'Error al registrar usuario: {str(e)}')
    
    return render(request, 'usuarios/register.html')


def is_user_logged_in(request):
    """
    Verifica si un usuario está actualmente autenticado
    """
    return 'user_id' in request.session and request.session['user_id'] is not None


def get_current_user(request):
    """
    Retorna el objeto del usuario actualmente autenticado o None si no hay uno
    """
    if is_user_logged_in(request):
        user_id = request.session['user_id']
        try:
            return Tblusuarios.objects.get(id_users=user_id)
        except Tblusuarios.DoesNotExist:
            return None
    return None


def profile_view(request):
    """
    Muestra el perfil del usuario actualmente autenticado
    """
    if not is_user_logged_in(request):
        return redirect('login')
    
    user = get_current_user(request)
    if not user:
        return redirect('login')
    
    context = {
        'user': user
    }
    return render(request, 'usuarios/profile.html', context)