from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from ..services.producto_service import ProductoService
from ..forms.producto_form import ProductoForm
from ..models import Categoria

service = ProductoService()

@login_required
def listar_productos(request):
    """Controlador para listar productos (RF-15)"""
    page = request.GET.get('page', 1)
    filters = {
        'estado': request.GET.get('estado', 'aprobado'),
        'categoria_id': request.GET.get('categoria'),
        'search': request.GET.get('q'),
    }
    
    # Si es agricultor, filtrar por sus productos
    if hasattr(request.user, 'userprofile') and request.user.userprofile.rol == 'agricultor' and request.GET.get('mis_productos'):
        filters['agricultor'] = request.user
    
    result = service.listar_productos(page, filters)
    
    context = {
        'productos': result['items'],
        'categorias': Categoria.objects.filter(activo=True),
        'pagination': {
            'page': result['page'],
            'has_next': result['has_next'],
            'has_prev': result['has_prev'],
        }
    }
    
    return render(request, 'inventario/producto_list.html', context)

@login_required
def detalle_producto(request, producto_id):
    """Controlador para ver detalle de producto"""
    producto = service.obtener_producto(producto_id)
    
    if not producto:
        messages.error(request, "Producto no encontrado")
        return redirect('inventario:listar')
    
    return render(request, 'inventario/producto_detail.html', {'producto': producto})

@login_required
def crear_producto(request):
    """Controlador para crear producto (RF-11)"""
    # Verificar rol (RF-11)
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.rol != 'agricultor':
        messages.error(request, "Solo agricultores pueden crear productos")
        return redirect('inventario:listar')
    
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            try:
                producto = service.crear_producto(
                    data=form.cleaned_data,
                    usuario=request.user
                )
                messages.success(request, "Producto creado exitosamente. Pendiente de aprobación.")
                return redirect('inventario:detalle', producto_id=producto.id)
            except Exception as e:
                messages.error(request, f"Error al crear producto: {str(e)}")
    else:
        form = ProductoForm()
    
    return render(request, 'inventario/producto_form.html', {'form': form, 'accion': 'crear'})

@login_required
def editar_producto(request, producto_id):
    """Controlador para editar producto (RF-12)"""
    producto = service.obtener_producto(producto_id)
    
    if not producto:
        messages.error(request, "Producto no encontrado")
        return redirect('inventario:listar')
    
    # Verificar permisos (RF-12)
    if producto.agricultor != request.user:
        messages.error(request, "No tienes permiso para editar este producto")
        return redirect('inventario:detalle', producto_id=producto_id)
    
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            try:
                producto_actualizado = service.actualizar_producto(
                    producto_id=producto_id,
                    data=form.cleaned_data,
                    usuario=request.user
                )
                messages.success(request, "Producto actualizado exitosamente")
                return redirect('inventario:detalle', producto_id=producto_actualizado.id)
            except Exception as e:
                messages.error(request, f"Error al actualizar: {str(e)}")
    else:
        # Cargar datos actuales
        initial_data = {
            'nombre': producto.nombre,
            'descripcion': producto.descripcion,
            'categoria': producto.categoria_id,
            'precio': producto.precio,
            'stock': producto.stock,
            'stock_minimo': producto.stock_minimo,
        }
        form = ProductoForm(initial=initial_data)
    
    return render(request, 'inventario/producto_form.html', {
        'form': form, 
        'accion': 'editar',
        'producto': producto
    })

@login_required
def eliminar_producto(request, producto_id):
    """Controlador para eliminar producto (RF-13)"""
    producto = service.obtener_producto(producto_id)
    
    if not producto:
        messages.error(request, "Producto no encontrado")
        return redirect('inventario:listar')
    
    # Verificar permisos
    if producto.agricultor_id != request.user.id:
        messages.error(request, "No tienes permiso para eliminar este producto")
        return redirect('inventario:detalle', producto_id=producto_id)
    
    if request.method == 'POST':
        try:
            service.eliminar_producto(producto_id, request.user.id)
            messages.success(request, "Producto eliminado exitosamente")
            return redirect('inventario:listar')
        except Exception as e:
            messages.error(request, f"Error al eliminar: {str(e)}")
    
    return render(request, 'inventario/producto_confirm_delete.html', {'producto': producto})

# API endpoints para AJAX
@login_required
def api_verificar_stock(request, producto_id):
    """API para verificar stock en tiempo real"""
    producto = service.obtener_producto(producto_id)
    if producto:
        return JsonResponse({
            'success': True,
            'stock': producto.stock,
            'agotado': producto.esta_agotado,
            'precio': producto.precio
        })
    return JsonResponse({'success': False, 'error': 'Producto no encontrado'})