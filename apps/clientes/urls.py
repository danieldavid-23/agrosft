from django.urls import path
from .controllers import cliente_controller

app_name = 'clientes'

urlpatterns = [
    # Historial de clientes con compras/procesos activos
    path('', cliente_controller.listar_clientes, name='cliente_list'),
    path('<int:pk>/', cliente_controller.detalle_cliente, name='cliente_detail'),
    path('<int:cliente_id>/historial-compras/', cliente_controller.historial_compras, name='historial_compras'),
]
