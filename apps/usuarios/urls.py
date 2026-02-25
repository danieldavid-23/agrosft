from django.urls import path
from apps.usuarios.controllers.terminos_controller import (
    TerminosView, 
    AceptarTerminosView, 
    HistorialTerminosView
)
from apps.usuarios.controllers.auth_controller import (
    RegistroView,
    LoginView,
    LogoutView,
    PerfilView,
    CambiarPasswordView
)

app_name = 'usuarios'

urlpatterns = [
    # Términos y condiciones
    path('terminos/', TerminosView.as_view(), name='terminos'),
    path('aceptar-terminos/', AceptarTerminosView.as_view(), name='aceptar-terminos'),
    path('historial/', HistorialTerminosView.as_view(), name='historial'),
    
    # Autenticación
    path('registro/', RegistroView.as_view(), name='registro'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('perfil/', PerfilView.as_view(), name='perfil'),
    path('cambiar-password/', CambiarPasswordView.as_view(), name='cambiar_password'),
]