from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import Venta, DetalleVenta
from ..forms import VentaForm
from apps.clientes.models import Cliente
from apps.inventario.models import Producto

@login_required
def listar_ventas(request):
    ventas = Venta.objects.all()
    return render(request, 'ventas/venta_list.html', {'ventas': ventas})

@login_required
def detalle_venta(request, pk):
    venta = get_object_or_404(Venta, pk=pk)
    detalles = venta.detalleventa_set.all()
    return render(request, 'ventas/venta_detail.html', {'venta': venta, 'detalles': detalles})

@login_required
def crear_venta(request):
    if request.method == 'POST':
        form = VentaForm(request.POST)
        if form.is_valid():
            venta = form.save(commit=False)
            venta.vendedor = request.user
            venta.save()
            # Aquí podrías agregar lógica para detalles
            messages.success(request, 'Venta creada exitosamente.')
            return redirect('venta_list')
    else:
        form = VentaForm()
    return render(request, 'ventas/venta_form.html', {'form': form})