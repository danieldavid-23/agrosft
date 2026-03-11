from django.urls import path
from .controllers import venta_controller

app_name = 'ventas'

urlpatterns = [
    path('', venta_controller.listar_ventas, name='venta_list'),
    path('<int:pk>/', venta_controller.detalle_venta, name='venta_detail'),
    path('crear/', venta_controller.crear_venta, name='venta_create'),
]
