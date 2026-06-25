from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.utils import timezone
from django.core.cache import cache
from apps.inventario.models import Categoria, Producto, ProductoUsuario, Estado
from apps.inventario.forms.producto_form import ProductoForm
from apps.inventario.repositories.producto_repository import ProductoRepository
from apps.usuarios.models.profile_model import Tblusuarios
from apps.ventas.models.movimiento import TipoMovimiento, Movimiento, ProductoUsuarioMovimiento
from core.utils.helpers import EstadoProducto
import json
import logging

logger = logging.getLogger(__name__)


def get_categorias_cached():
    """Obtiene categorías con caché de 1 hora"""
    cache_key = 'categorias_activas'
    categorias = cache.get(cache_key)
    if categorias is None:
        categorias = list(Categoria.objects.filter(activo=True))
        cache.set(cache_key, categorias, 3600)  # 1 hora
    return categorias


def get_estados_cached():
    """Obtiene estados con caché de 1 hora"""
    cache_key = 'estados_producto'
    estados = cache.get(cache_key)
    if estados is None:
        estados = list(Estado.objects.all())
        cache.set(cache_key, estados, 3600)  # 1 hora
    return estados


@login_required
def listar_productos(request):
    """
    Vista del INVENTARIO PERSONAL - Muestra SOLO los productos del usuario actual
    Con botones de Editar y Eliminar
    """
    # Obtener SOLO los productos del usuario actual
    productos = ProductoUsuario.objects.filter(
        id_usuario=request.user
    ).select_related(
        'id_producto__id_categoria',
        'id_usuario',
        'id_estado'
    ).order_by('-id_producto_usuario')

    # Aplicar filtros si es AJAX
    q = request.GET.get('q')
    categoria_id = request.GET.get('categoria')
    orden = request.GET.get('orden', 'reciente')

    if q:
        productos = productos.filter(id_producto__nombre__icontains=q)
    if categoria_id:
        productos = productos.filter(id_producto__id_categoria=categoria_id)

    if orden == 'precio_asc':
        productos = productos.order_by('precio')
    elif orden == 'precio_desc':
        productos = productos.order_by('-precio')
    elif orden == 'nombre':
        productos = productos.order_by('id_producto__nombre')

    # Paginar resultados
    paginator = Paginator(productos, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Preparar datos de paginación para el template
    pagination = {
        'has_prev': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'page': page_obj.number,
    }

    from django.urls import reverse

    # Transformar productos para que sean compatibles con el template
    productos_transformados = []
    for pu in page_obj:
        producto_data = {
            'id': pu.id_producto_usuario,
            'nombre': pu.id_producto.nombre,
            'descripcion': pu.id_producto.descripcion or '',
            'precio': float(pu.precio),
            'stock': pu.obtener_stock(),
            'stock_minimo': pu.id_producto.stock_minimo,
            'estado': pu.id_estado.estado,
            'categoria_nombre': pu.id_producto.id_categoria.nombre,
            'agricultor_id': pu.id_usuario.id_users,
            'esta_agotado': pu.cantidad == 0,
            'imagen': None,
            'es_mi_producto': True,
            'editUrl': reverse('inventario:editar', args=[pu.id_producto_usuario]),
            'deleteUrl': reverse('inventario:eliminar', args=[pu.id_producto_usuario]),
        }
        productos_transformados.append(producto_data)

    # Si es AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'products': productos_transformados,
            'has_next': pagination['has_next'],
            'has_prev': pagination['has_prev'],
            'page': pagination['page'],
        })

    categorias = get_categorias_cached()
    estados = get_estados_cached()

    inventario_data = {
        'initialProducts': productos_transformados,
        'categories': [{'id': c.id_categoria, 'nombre': c.nombre} for c in categorias],
        'estados': [{'id': e.id_estado, 'nombre': e.estado} for e in estados],
        'urls': {
            'listar': reverse('inventario:listar'),
            'crear': reverse('inventario:crear'),
            'eliminar': reverse('inventario:eliminar', args=[0]),
            'titulo': 'Mi Inventario',
            'subtitulo': 'Gestiona tus productos registrados',
        }
    }

    return render(request, 'inventario/producto_list.html', {
        'productos': productos_transformados,
        'pagination': pagination,
        'vista': 'inventario',
        'titulo': 'Mi Inventario',
        'subtitulo': 'Gestiona tus productos registrados',
        'inventario_json': json.dumps(inventario_data),
        'categorias': categorias,
        'estados': estados,
    })


@login_required
def marketplace(request):
    """
    Vista del INICIO/MARKETPLACE - Muestra productos de OTROS usuarios
    Con botones de Agregar al carrito y Ver Detalle
    """
    # Obtener productos de OTROS usuarios (excluyendo los del usuario actual) y que estén aprobados
    estado_aprobado = EstadoProducto.APROBADO
    productos = ProductoUsuario.objects.exclude(
        id_usuario=request.user
    ).filter(
        id_estado__estado=estado_aprobado
    ).select_related(
        'id_producto__id_categoria',
        'id_usuario',
        'id_estado'
    ).order_by('-id_producto_usuario')
    
    # Aplicar filtros si es AJAX
    q = request.GET.get('q')
    categoria_id = request.GET.get('categoria')
    orden = request.GET.get('orden', 'reciente')

    if q:
        productos = productos.filter(id_producto__nombre__icontains=q)
    if categoria_id:
        productos = productos.filter(id_producto__id_categoria=categoria_id)

    if orden == 'precio_asc':
        productos = productos.order_by('precio')
    elif orden == 'precio_desc':
        productos = productos.order_by('-precio')
    elif orden == 'nombre':
        productos = productos.order_by('id_producto__nombre')

    # Debug: Ver cuántos productos hay
    total_productos = ProductoUsuario.objects.count()
    mis_productos = ProductoUsuario.objects.filter(id_usuario=request.user).count()
    otros_productos = productos.count()
    logger.info(f"Marketplace - Total: {total_productos}, Míos: {mis_productos}, De otros: {otros_productos}")

    # Paginar resultados
    paginator = Paginator(productos, 12)  # 12 productos por página para el marketplace
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Preparar datos de paginación para el template
    pagination = {
        'has_prev': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'page': page_obj.number,
    }

    from django.urls import reverse

    # Transformar productos para que sean compatibles con el template
    productos_transformados = []
    for pu in page_obj:
        producto_data = {
            'id': pu.id_producto_usuario,
            'nombre': pu.id_producto.nombre,
            'descripcion': pu.id_producto.descripcion or '',
            'precio': float(pu.precio),
            'stock': pu.obtener_stock(),
            'stock_minimo': pu.id_producto.stock_minimo,
            'estado': pu.id_estado.estado,
            'categoria_nombre': pu.id_producto.id_categoria.nombre,
            'agricultor_id': pu.id_usuario.id_users,
            'agricultor_nombre': f"{pu.id_usuario.nombres} {pu.id_usuario.apellidos}",
            'esta_agotado': pu.cantidad == 0,
            'imagen': None,
            'es_mi_producto': False,
            'detailUrl': reverse('inventario:detalle', args=[pu.id_producto_usuario]),
        }
        productos_transformados.append(producto_data)

    # Si es AJAX, devolver JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'products': productos_transformados,
            'has_next': pagination['has_next'],
            'has_prev': pagination['has_prev'],
            'page': pagination['page'],
        })

    categorias_list = get_categorias_cached()

    marketplace_data = {
        'initialProducts': productos_transformados,
        'categories': [{'id': c.id_categoria, 'nombre': c.nombre} for c in categorias_list],
        'urls': {
            'marketplace': reverse('inventario:marketplace'),
            'addToCart': reverse('ventas:carrito_agregar', args=[0]),
        }
    }

    return render(request, 'inventario/marketplace.html', {
        'productos': productos_transformados,
        'pagination': pagination,
        'vista': 'marketplace',
        'titulo': 'Marketplace',
        'subtitulo': 'Productos disponibles de otros agricultores',
        'marketplace_json': json.dumps(marketplace_data),
    })

# Eliminado, ya que se está usando la vista genérica de Django

@login_required
def crear_producto(request):
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            # Verificar si el producto ya existe en el catálogo maestro
            nombre_producto = form.cleaned_data['nombre']
            descripcion = form.cleaned_data['descripcion']
            id_categoria = form.cleaned_data['id_categoria']
            
            # Obtener stock_minimo del formulario o usar valor por defecto
            stock_minimo = form.cleaned_data.get('stock_minimo', 5)
            if stock_minimo is None:
                stock_minimo = 5
            
            # Buscar si ya existe un producto con el mismo nombre
            producto_existente, created = Producto.objects.get_or_create(
                nombre=nombre_producto,
                defaults={
                    'descripcion': descripcion,
                    'id_categoria': id_categoria,
                    'cantidad': 0,  # Valor predeterminado
                    'stock_minimo': stock_minimo,
                    'estado': EstadoProducto.PENDIENTE.lower()  # Valor predeterminado
                }
            )
            
            # Si el producto ya existe y es admin, actualizar stock_minimo
            if not created and (request.user.is_staff or request.user.is_superuser):
                producto_existente.stock_minimo = stock_minimo
                producto_existente.save()
            
            # Crear la relación específica del usuario con el producto (producto_usuario)
            producto_usuario = ProductoUsuario()
            producto_usuario.id_producto = producto_existente
            # Corrección: usar directamente request.user, que ya es un objeto Tblusuarios
            producto_usuario.id_usuario = request.user
            # NOTA: cantidad se inicializa en 0, el trigger de BD la actualizará al insertar el movimiento
            producto_usuario.cantidad = 0
            producto_usuario.precio = form.cleaned_data['precio']
            producto_usuario.id_estado = Estado.objects.get(estado=EstadoProducto.PENDIENTE)  # Estado inicial
            producto_usuario.save()
            
            # Registrar el movimiento inicial de stock (abastecimiento/venta)
            cantidad_inicial = form.cleaned_data['cantidad']
            if cantidad_inicial > 0:
                tipo_venta, _ = TipoMovimiento.objects.get_or_create(tipo='venta')
                movimiento = Movimiento.objects.create(
                    id_tipo_movimiento=tipo_venta,
                    id_usuario=request.user
                )
                ProductoUsuarioMovimiento.objects.create(
                    id_movimiento=movimiento,
                    id_producto_usuario=producto_usuario,
                    cantidad=cantidad_inicial
                )
            
            logger.info(f"Product created by user {request.user.pk}: {producto_existente.nombre}")
            messages.success(request, '¡Producto creado exitosamente!')
            return redirect('inventario:listar')
    else:
        form = ProductoForm()

    categorias = get_categorias_cached()
    estados = get_estados_cached()
    
    return render(request, 'inventario/crear_producto.html', {
        'form': form,
        'categorias': categorias,
        'estados': estados
    })

@login_required
def editar_producto(request, pk):
    producto_usuario = get_object_or_404(
        ProductoUsuario.objects.select_related('id_producto', 'id_usuario'),
        id_producto_usuario=pk
    )
    
    # Verificar que el usuario sea el dueño o admin
    if producto_usuario.id_usuario != request.user and not request.user.is_staff:
        messages.error(request, 'No tienes permiso para editar este producto.')
        return redirect('inventario:listar')
    
    if request.method == 'POST':
        form = ProductoForm(request.POST)  # Eliminar instance= que no es válido para forms.Form
        if form.is_valid():
            with transaction.atomic():
                # Actualizar campos del producto maestro (tblproducto)
                producto = producto_usuario.id_producto
                producto.nombre = form.cleaned_data['nombre']
                producto.descripcion = form.cleaned_data['descripcion']
                producto.id_categoria = form.cleaned_data['id_categoria']
                
                # TODOS los usuarios pueden editar stock_minimo
                stock_minimo_value = form.cleaned_data.get('stock_minimo')
                if stock_minimo_value is not None:
                    producto.stock_minimo = stock_minimo_value
                
                producto.save()
                logger.info(f"Producto maestro actualizado: {producto.nombre}, stock_minimo: {producto.stock_minimo}")
                
                # Calcular diferencia para el movimiento de stock antes de actualizar
                diferencia_stock = form.cleaned_data['cantidad'] - producto_usuario.cantidad
                
                # Actualizar campos específicos del usuario (tblproductos_has_tblusuarios)
                # NOTA: No se actualiza 'cantidad' aquí para evitar conflictos con el trigger de BD
                producto_usuario.precio = form.cleaned_data['precio']
                
                # Cualquier usuario puede cambiar el estado de su producto
                if form.cleaned_data.get('id_estado'):
                    producto_usuario.id_estado = form.cleaned_data['id_estado']
                
                producto_usuario.save()
                
                # Registrar el movimiento de stock si hubo cambio
                if diferencia_stock != 0:
                    tipo_venta, _ = TipoMovimiento.objects.get_or_create(tipo='venta')
                    movimiento = Movimiento.objects.create(
                        id_tipo_movimiento=tipo_venta,
                        id_usuario=request.user
                    )
                    ProductoUsuarioMovimiento.objects.create(
                        id_movimiento=movimiento,
                        id_producto_usuario=producto_usuario,
                        cantidad=diferencia_stock
                    )
                
                logger.info(f"ProductoUsuario actualizado: cantidad={producto_usuario.cantidad}, precio={producto_usuario.precio}")
                
                messages.success(request, '¡Producto actualizado exitosamente!')
                return redirect('inventario:listar')
        else:
            # Log de errores de validación para debugging
            logger.error(f"Errores de validación del formulario: {form.errors}")
            messages.error(request, f'Error al validar el formulario: {form.errors}')
    else:
        # Preparar datos para el formulario
        initial_data = {
            'nombre': producto_usuario.id_producto.nombre,
            'descripcion': producto_usuario.id_producto.descripcion,
            'id_categoria': producto_usuario.id_producto.id_categoria,
            'stock_minimo': producto_usuario.id_producto.stock_minimo,
            'cantidad': producto_usuario.cantidad,  # Ahora es Decimal, no necesita conversión
            'precio': producto_usuario.precio,
            'id_estado': producto_usuario.id_estado,
        }
        form = ProductoForm(initial=initial_data)
        # TODOS los usuarios pueden editar stock_minimo (sin restricciones)

    categorias = get_categorias_cached()
    estados = get_estados_cached()
    
    # Usar producto_form.html que ya existe
    return render(request, 'inventario/producto_form.html', {
        'form': form,
        'producto_usuario': producto_usuario,
        'producto': producto_usuario.id_producto,  # El template usa producto.nombre
        'categorias': categorias,
        'estados': estados,
        'titulo': 'Editar Producto',
        'accion': 'editar'
    })

@login_required
def eliminar_producto(request, pk):
    producto_usuario = get_object_or_404(
        ProductoUsuario.objects.select_related('id_producto'),
        id_producto_usuario=pk
    )
    
    # Verificar que el usuario sea el dueño o admin
    if producto_usuario.id_usuario != request.user and not request.user.is_staff:
        msg = 'No tienes permiso para eliminar este producto.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': msg})
        messages.error(request, msg)
        return redirect('inventario:listar')
    
    if request.method == 'POST':
        producto_nombre = producto_usuario.id_producto.nombre
        producto_usuario.delete()
        
        logger.info(f"ProductoUsuario {pk} eliminado: {producto_nombre} por user {request.user.pk}")
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'producto_id': pk})
        messages.success(request, '¡Producto eliminado exitosamente!')
        return redirect('inventario:listar')
    
    return render(request, 'inventario/producto_confirm_delete.html', {
        'producto_usuario': producto_usuario,
        'producto': producto_usuario.id_producto
    })

# Nuevas funcionalidades para aprobar y rechazar productos
@login_required
def aprobar_producto(request, producto_id):
    producto_usuario = get_object_or_404(ProductoUsuario, id_producto_usuario=producto_id)
    
    if not request.user.is_staff:
        logger.warning(f"Permission denied: user {request.user.pk} attempted to approve product {producto_id}")
        messages.error(request, 'No tienes permiso para aprobar este producto.')
        return redirect('inventario:listar')
    
    # Cambiar el estado en el modelo ProductoUsuario
    estado_aprobado = Estado.objects.get(estado=EstadoProducto.APROBADO)
    producto_usuario.id_estado = estado_aprobado
    producto_usuario.save()
    
    # Registrar en historial
    ProductoRepository.log_action(
        producto_id=producto_usuario.id_producto_usuario,
        user_id=request.user.id_users,  # Usar id_users para el modelo Tblusuarios
        action='aprobacion'
    )
    
    logger.info(f"Product {producto_id} approved by user {request.user.pk}")
    messages.success(request, 'Producto aprobado exitosamente.')
    return redirect('inventario:listar')


@login_required
def rechazar_producto(request, producto_id):
    producto_usuario = get_object_or_404(ProductoUsuario, id_producto_usuario=producto_id)
    
    if not request.user.is_staff:
        logger.warning(f"Permission denied: user {request.user.pk} attempted to reject product {producto_id}")
        messages.error(request, 'No tienes permiso para rechazar este producto.')
        return redirect('inventario:listar')
    
    # Cambiar el estado en el modelo ProductoUsuario
    estado_rechazado = Estado.objects.get(estado=EstadoProducto.RECHAZADO)
    producto_usuario.id_estado = estado_rechazado
    producto_usuario.save()
    
    # Registrar en historial
    ProductoRepository.log_action(
        producto_id=producto_usuario.id_producto_usuario,
        user_id=request.user.id_users,  # Usar id_users para el modelo Tblusuarios
        action='rechazo'
    )
    
    logger.info(f"Product {producto_id} rejected by user {request.user.pk}")
    messages.success(request, 'Producto rechazado exitosamente.')
    return redirect('inventario:listar')


def api_verificar_stock(request, producto_id):
    """API endpoint para verificar el stock de un producto"""
    from django.http import JsonResponse
    producto = get_object_or_404(Producto, id_producto=producto_id)
    
    data = {
        'producto_id': producto.id_producto,
        'nombre': producto.nombre,
        'stock': producto.cantidad,  # Cambiado de 'stock' a 'cantidad'
        'disponible': producto.cantidad > 0,  # Cambiado de 'stock' a 'cantidad'
        'stock_minimo': producto.stock_minimo,
        'agotado': producto.cantidad == 0,  # Cambiado de 'stock' a 'cantidad'
    }
    
    return JsonResponse(data)