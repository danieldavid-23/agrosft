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
from apps.usuarios.controllers.admin_usuarios_controller import (
    # Gestión de usuarios
    admin_usuarios_list,
    admin_usuario_crear,
    admin_usuario_editar,
    admin_usuario_toggle_activo,
    # Estadísticas
    admin_estadisticas,
    # Moderación de productos
    admin_moderacion,
    admin_aprobar_producto,
    admin_rechazar_producto,
    # Categorías
    admin_categorias_list,
    admin_categoria_crear,
    admin_categoria_editar,
    admin_categoria_toggle,
    # Reportes CSV
    admin_reporte_usuarios_csv,
    admin_reporte_productos_csv,
    admin_reporte_ventas_csv,
    # Auditoría
    admin_audit_logs,
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
    
    # ── Gestión de Usuarios (Admin) ─────────────────────────────────────────
    path('admin-usuarios/', admin_usuarios_list, name='admin_usuarios_list'),
    path('admin-usuarios/crear/', admin_usuario_crear, name='admin_usuario_crear'),
    path('admin-usuarios/editar/<int:pk>/', admin_usuario_editar, name='admin_usuario_editar'),
    path('admin-usuarios/toggle-activo/<int:pk>/', admin_usuario_toggle_activo, name='admin_usuario_toggle_activo'),

    # ── Estadísticas ────────────────────────────────────────────────────────
    path('admin-estadisticas/', admin_estadisticas, name='admin_estadisticas'),

    # ── Moderación de Productos ─────────────────────────────────────────────
    path('admin-moderacion/', admin_moderacion, name='admin_moderacion'),
    path('admin-moderacion/aprobar/<int:pk>/', admin_aprobar_producto, name='admin_aprobar_producto'),
    path('admin-moderacion/rechazar/<int:pk>/', admin_rechazar_producto, name='admin_rechazar_producto'),

    # ── Gestión de Categorías ───────────────────────────────────────────────
    path('admin-categorias/', admin_categorias_list, name='admin_categorias_list'),
    path('admin-categorias/crear/', admin_categoria_crear, name='admin_categoria_crear'),
    path('admin-categorias/editar/<int:pk>/', admin_categoria_editar, name='admin_categoria_editar'),
    path('admin-categorias/toggle/<int:pk>/', admin_categoria_toggle, name='admin_categoria_toggle'),

    # ── Reportes CSV ────────────────────────────────────────────────────────
    path('admin-reporte/usuarios/', admin_reporte_usuarios_csv, name='admin_reporte_usuarios_csv'),
    path('admin-reporte/productos/', admin_reporte_productos_csv, name='admin_reporte_productos_csv'),
    path('admin-reporte/ventas/', admin_reporte_ventas_csv, name='admin_reporte_ventas_csv'),

    # ── Auditoría ───────────────────────────────────────────────────────────
    path('admin-auditoria/', admin_audit_logs, name='admin_audit_logs'),

    # Recuperación de contraseña
    path('password-reset/', UserPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', UserPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset-complete/', UserPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]