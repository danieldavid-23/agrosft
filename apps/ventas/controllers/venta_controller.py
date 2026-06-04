from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# NOTA: Estas tablas no existen en la BD actual
# from ..models import Venta, DetalleVenta
# from ..forms import VentaForm
# from apps.clientes.models import Cliente
# from apps.inventario.models import Producto

@login_required
def listar_ventas(request):
    """
    Módulo de Ventas - TEMPORALMENTE DESHABILITADO
    Las tablas necesarias no existen en la base de datos actual
    """
    messages.info(request, 'El módulo de Ventas estará disponible próximamente. Las tablas de base de datos necesarias están en desarrollo.')
    return redirect('inventario:marketplace')

@login_required
def detalle_venta(request, pk):
    messages.info(request, 'El módulo de Ventas estará disponible próximamente.')
    return redirect('inventario:marketplace')

@login_required
def crear_venta(request):
    messages.info(request, 'El módulo de Ventas estará disponible próximamente.')
    return redirect('inventario:marketplace')