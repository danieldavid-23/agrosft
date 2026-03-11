from django.urls import path
from .controllers import cultivo_controller

app_name = 'cultivos'

urlpatterns = [
    path('', cultivo_controller.listar_cultivos, name='cultivo_list'),
    path('<int:pk>/', cultivo_controller.detalle_cultivo, name='cultivo_detail'),
    path('crear/', cultivo_controller.crear_cultivo, name='cultivo_create'),
]
