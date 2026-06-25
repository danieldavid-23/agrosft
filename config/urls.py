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

# Personalización del panel de administración
admin.site.site_header = 'AgroSFT - Panel de Administración'
admin.site.site_title = 'AgroSFT Admin'
admin.site.index_title = 'Gestión de la Plataforma Agrícola'


def home_redirect(request):
    """Redirigir a la página de login en lugar de registro"""
    return redirect('usuarios:login')


urlpatterns = [
    path('', home_redirect, name='home'),
    path('usuarios/', include('apps.usuarios.urls', namespace='usuarios')),
    path('inventario/', include('apps.inventario.urls', namespace='inventario')),
    path('clientes/', include('apps.clientes.urls', namespace='clientes')),
    path('ventas/', include('apps.ventas.urls', namespace='ventas')),
    path('oauth/', include('social_django.urls', namespace='social')),
    path('admin/', admin.site.urls),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)