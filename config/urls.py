"""
URL configuration for agrosft project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from django.shortcuts import redirect
from django.contrib import admin

def home_redirect(request):
    """Redirigir a la página de login en lugar de registro"""
    return redirect('usuarios:login')  # Cambiado de 'usuarios:registro' a 'usuarios:login'

urlpatterns = [
    path('', home_redirect, name='home'),  # Mantener la redirección pero al login
    path('usuarios/', include('apps.usuarios.urls', namespace='usuarios')),
    path('inventario/', include('apps.inventario.urls', namespace='inventario')),
    path('clientes/', include('apps.clientes.urls', namespace='clientes')),
    path('ventas/', include('apps.ventas.urls', namespace='ventas')),
    path('oauth/', include('social_django.urls', namespace='social')),  # Rutas de Google OAuth
    # Eliminamos todas las rutas que dependen de componentes del sistema
    # path('admin/', admin.site.urls),
    path('admin/', admin.site.urls),
]