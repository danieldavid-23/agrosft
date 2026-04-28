from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.views.generic import RedirectView

def home_redirect(request):
    if request.user.is_authenticated:
        # Si está autenticado, verificar si aceptó términos
        from apps.usuarios.services.terminos_service import TerminosService
        if TerminosService.usuario_debe_aceptar_terminos(request.user):
            return redirect('usuarios:aceptar-terminos')
        return redirect('inventario:listar')  # Redirige a productos
    return redirect('usuarios:login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_redirect, name='home'),
    path('usuarios/', include('apps.usuarios.urls')),
    path('inventario/', include('apps.inventario.urls')),
    path('clientes/', include('apps.clientes.urls')),
    path('ventas/', include('apps.ventas.urls')),
    path('cultivos/', include('apps.cultivos.urls')),
    path('accounts/login/', RedirectView.as_view(url='/usuarios/login/', query_string=True)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)