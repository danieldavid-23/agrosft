"""
Controlador para la gestión de productos, publicaciones y categorías
en el Panel de Administración.
"""
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count
from apps.inventario.models import Producto, ProductoUsuario, Categoria
from .admin_controller import admin_required, registrar_auditoria


@admin_required
def lista_productos(request):
    """Listado del catálogo de productos."""
    q = request.GET.get('q', '').strip()
    categoria = request.GET.get('categoria', '')
    eliminado = request.GET.get('eliminado', '')

    productos = Producto.objects.select_related('id_categoria').order_by('nombre')

    if q:
        productos = productos.filter(
            Q(nombre__icontains=q) | Q(descripcion__icontains=q)
        )
    if categoria:
        productos = productos.filter(id_categoria_id=categoria)
    if eliminado == '1':
        productos = productos.filter(eliminado=True)
    elif eliminado != '1':
        productos = productos.filter(eliminado=False)

    categorias = Categoria.objects.order_by('nombre')

    contexto = {
        'titulo': 'Productos',
        'productos': productos,
        'categorias': categorias,
        'q': q,
        'categoria': categoria,
        'eliminado': eliminado,
        'seccion_activa': 'productos',
    }
    return render(request, 'administracion/productos/lista.html', contexto)


@admin_required
def lista_publicaciones(request):
    """Listado de publicaciones (productos ofertados por usuarios)."""
    publicaciones = ProductoUsuario.objects.select_related(
        'id_producto', 'id_usuario'
    ).order_by('-fecha_creacion')

    contexto = {
        'titulo': 'Publicaciones',
        'publicaciones': publicaciones,
        'seccion_activa': 'productos',
    }
    return render(request, 'administracion/productos/publicaciones.html', contexto)


@admin_required
def lista_categorias(request):
    """Listado de categorías."""
    categorias = Categoria.objects.annotate(num_productos=Count('producto')).order_by('nombre')
    contexto = {
        'titulo': 'Categorías',
        'categorias': categorias,
        'seccion_activa': 'categorias',
    }
    return render(request, 'administracion/productos/categorias.html', contexto)


@admin_required
def eliminar_categoria(request, pk):
    """Elimina (lógicamente) una categoría."""
    categoria = get_object_or_404(Categoria, id_categoria=pk)
    if request.method == 'POST':
        categoria.activo = False
        categoria.save()
        registrar_auditoria(
            request.user, 'Desactivar categoría', objetivo=categoria.nombre, request=request,
        )
        messages.success(request, f'La categoría "{categoria.nombre}" fue desactivada.')
    return redirect('administracion:categorias')