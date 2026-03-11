from django.urls import path
from .views.producto_views import (
    producto_list, producto_detail, producto_create, producto_update, producto_delete
)
from .controllers.producto_controller import api_verificar_stock

app_name = 'inventario'

urlpatterns = [
    # URLs principales
    path('', producto_list, name='listar'),
    path('producto/<int:pk>/', producto_detail, name='detalle'),
    path('producto/nuevo/', producto_create, name='crear'),
    path('producto/<int:pk>/editar/', producto_update, name='editar'),
    path('producto/<int:pk>/eliminar/', producto_delete, name='eliminar'),
    
    # API endpoints
    path('api/producto/<int:producto_id>/stock/', api_verificar_stock, name='api_stock'),
]