from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import Cultivo, UsoProductoCultivo
from ..forms import CultivoForm
from apps.inventario.models import Producto

@login_required
def listar_cultivos(request):
    cultivos = Cultivo.objects.filter(agricultor=request.user)
    return render(request, 'cultivos/cultivo_list.html', {'cultivos': cultivos})

@login_required
def detalle_cultivo(request, pk):
    cultivo = get_object_or_404(Cultivo, pk=pk, agricultor=request.user)
    usos = cultivo.usoproductocultivo_set.all()
    return render(request, 'cultivos/cultivo_detail.html', {'cultivo': cultivo, 'usos': usos})

@login_required
def crear_cultivo(request):
    if request.method == 'POST':
        form = CultivoForm(request.POST)
        if form.is_valid():
            cultivo = form.save(commit=False)
            cultivo.agricultor = request.user
            cultivo.save()
            messages.success(request, 'Cultivo creado exitosamente.')
            return redirect('cultivo_list')
    else:
        form = CultivoForm()
    return render(request, 'cultivos/cultivo_form.html', {'form': form})