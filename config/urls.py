from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

def home_redirect(request):
    if request.user.is_authenticated:
        # Si está autenticado, verificar si aceptó términos
        from apps.usuarios.services.terminos_service import TerminosService
        if TerminosService.usuario_debe_aceptar_terminos(request.user):
            return redirect('usuarios:aceptar-terminos')
        return redirect('usuarios:perfil')  # O alguna página de inicio
    return redirect('usuarios:login')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_redirect, name='home'),
    path('usuarios/', include('apps.usuarios.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)