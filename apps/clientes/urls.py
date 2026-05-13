from django.urls import path
from .controllers import cliente_controller

app_name = 'clientes'

urlpatterns = [
    path('', cliente_controller.listar_clientes, name='cliente_list'),
    path('<int:pk>/', cliente_controller.detalle_cliente, name='cliente_detail'),
    path('crear/', cliente_controller.crear_cliente, name='cliente_create'),
]
