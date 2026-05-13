from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import Cliente
from ..forms import ClienteForm

@login_required
def listar_clientes(request):
    clientes = Cliente.objects.all()
    return render(request, 'clientes/cliente_list.html', {'clientes': clientes})

@login_required
def detalle_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    return render(request, 'clientes/cliente_detail.html', {'cliente': cliente})

@login_required
def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente creado exitosamente.')
            return redirect('cliente_list')
    else:
        form = ClienteForm()
    return render(request, 'clientes/cliente_form.html', {'form': form})