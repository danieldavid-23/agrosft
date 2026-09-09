from django.urls import path
from .controllers import (
    admin_controller,
    admin_usuarios_controller,
    admin_productos_controller,
    admin_ventas_controller,
    admin_auditoria_controller,
    admin_clientes_controller,
)

app_name = 'administracion'

urlpatterns = [
    # Dashboard
    path('', admin_controller.dashboard, name='dashboard'),

    # Usuarios
    path('usuarios/', admin_usuarios_controller.lista_usuarios, name='usuarios'),
    path('usuarios/<int:pk>/', admin_usuarios_controller.detalle_usuario, name='usuario_detalle'),
    path('usuarios/<int:pk>/estado/', admin_usuarios_controller.cambiar_estado_usuario, name='usuario_estado'),

    # Productos
    path('productos/', admin_productos_controller.lista_productos, name='productos'),
    path('productos/publicaciones/', admin_productos_controller.lista_publicaciones, name='publicaciones'),
    path('productos/categorias/', admin_productos_controller.lista_categorias, name='categorias'),
    path('productos/categorias/<int:pk>/eliminar/', admin_productos_controller.eliminar_categoria, name='categoria_eliminar'),

    # Movimientos / Ventas
    path('movimientos/', admin_ventas_controller.lista_movimientos, name='movimientos'),
    path('movimientos/<int:pk>/', admin_ventas_controller.detalle_movimiento, name='movimiento_detalle'),

    # Facturas
    path('facturas/', admin_ventas_controller.lista_facturas, name='facturas'),
    path('facturas/<int:pk>/', admin_ventas_controller.detalle_factura, name='factura_detalle'),

    # Clientes
    path('clientes/', admin_clientes_controller.lista_clientes, name='clientes'),

    # Auditoría
    path('auditoria/', admin_auditoria_controller.lista_auditoria, name='auditoria'),
    path('auditoria/limpiar/', admin_auditoria_controller.limpiar_auditoria, name='auditoria_limpiar'),
]