"""
Controlador para la gestión de clientes en el Panel de Administración.
"""
from django.shortcuts import render
from apps.clientes.models import Cliente
from .admin_controller import admin_required


@admin_required
def lista_clientes(request):
    """Listado de clientes registrados."""
    clientes = Cliente.objects.select_related('usuario').order_by('-fecha_registro')
    contexto = {
        'titulo': 'Clientes',
        'clientes': clientes,
        'seccion_activa': 'clientes',
    }
    return render(request, 'administracion/clientes/lista.html', contexto)