from django.urls import path
from .views.producto_views import (
    producto_list, producto_detail, producto_create, producto_update, producto_delete, venta_directa
)
from .controllers.producto_controller import (
    api_verificar_stock, marketplace, eliminar_imagen_producto,
    api_crear_categoria, api_nombres_producto
)

app_name = 'inventario'

urlpatterns = [
    # URLs principales
    path('', producto_list, name='listar'),  # Mi Inventario
    path('marketplace/', marketplace, name='marketplace'),  # Inicio - Productos de otros
    path('producto/<int:pk>/', producto_detail, name='detalle'),
    path('producto/nuevo/', producto_create, name='crear'),
    path('venta-directa/', venta_directa, name='venta_directa'),
    path('producto/<int:pk>/editar/', producto_update, name='editar'),
    path('producto/<int:pk>/eliminar/', producto_delete, name='eliminar'),
    path('producto/<int:pk>/eliminar-imagen/<str:img_id>/', eliminar_imagen_producto, name='eliminar_imagen'),
    
    # API endpoints
    path('api/producto/<int:producto_id>/stock/', api_verificar_stock, name='api_stock'),
    path('api/categorias/crear/', api_crear_categoria, name='api_crear_categoria'),
    path('api/productos/nombres/', api_nombres_producto, name='api_nombres_producto'),
]