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
    CambiarPasswordView,
    UserPasswordResetView,
    UserPasswordResetDoneView,
    UserPasswordResetConfirmView,
    UserPasswordResetCompleteView
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
    
    # Recuperación de contraseña
    path('password-reset/', UserPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', UserPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', UserPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]