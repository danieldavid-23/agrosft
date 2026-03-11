from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from ..models import Producto, Categoria
from ..forms import ProductoForm

@login_required
def producto_list(request):
    productos = Producto.objects.filter(eliminado=False)
    rol = None
    if hasattr(request.user, 'userprofile'):
        rol = request.user.userprofile.rol
    return render(request, 'inventario/producto_list.html', {'productos': productos, 'rol': rol})

@login_required
def producto_detail(request, pk):
    producto = get_object_or_404(Producto, pk=pk, eliminado=False)
    rol = None
    if hasattr(request.user, 'userprofile'):
        rol = request.user.userprofile.rol
    return render(request, 'inventario/producto_detail.html', {'producto': producto, 'rol': rol})

@login_required
def producto_create(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            producto = form.save(commit=False)
            producto.agricultor = request.user
            producto.save()
            messages.success(request, 'Producto creado exitosamente.')
            return redirect('inventario:listar')
    else:
        form = ProductoForm()
    return render(request, 'inventario/producto_form.html', {'form': form})

@login_required
def producto_update(request, pk):
    producto = get_object_or_404(Producto, pk=pk, eliminado=False)
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado exitosamente.')
            return redirect('inventario:detalle', pk=pk)
    else:
        form = ProductoForm(instance=producto)
    return render(request, 'inventario/producto_form.html', {'form': form})

@login_required
def producto_delete(request, pk):
    producto = get_object_or_404(Producto, pk=pk, eliminado=False)
    if request.method == 'POST':
        producto.soft_delete(user_id=request.user.id)
        messages.success(request, 'Producto eliminado exitosamente.')
        return redirect('inventario:listar')
    return render(request, 'inventario/producto_confirm_delete.html', {'producto': producto})