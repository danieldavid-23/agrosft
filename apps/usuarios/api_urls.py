from django.urls import path
from apps.usuarios.controllers.api_auth_controller import (
    PasswordResetAPIView,
    PasswordResetValidateTokenAPIView,
    PasswordResetConfirmAPIView,
)

app_name = 'usuarios_api'

urlpatterns = [
    path('password-reset/', PasswordResetAPIView.as_view(), name='api_password_reset'),
    path('password-reset/validate/<uidb64>/<token>/', PasswordResetValidateTokenAPIView.as_view(), name='api_password_reset_validate'),
    path('password-reset/confirm/', PasswordResetConfirmAPIView.as_view(), name='api_password_reset_confirm'),
]
