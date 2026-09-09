from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.utils import timezone
from django.core.cache import cache
from decimal import Decimal
from apps.inventario.models import Categoria, Producto, ProductoImagen, ProductoUsuario
from apps.inventario.forms.producto_form import ProductoForm
from apps.inventario.repositories.producto_repository import ProductoRepository
from apps.usuarios.models.profile_model import Tblusuarios
from core.utils.helpers import formatear_errores_form
from apps.ventas.models.movimiento import TipoMovimiento, Movimiento, ProductoUsuarioMovimiento
import json
import logging

logger = logging.getLogger(__name__)


@login_required
def api_crear_categoria(request):
    """
    API AJAX para crear una nueva categoría.
    POST JSON: {"nombre": "Hierbas aromáticas"}
    Retorna JSON con la categoría creada o error de validación.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido.'}, status=405)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        # Fallback a form-encoded
        data = {'nombre': request.POST.get('nombre', '')}

    nombre = (data.get('nombre') or '').strip()

    # Validaciones
    if not nombre:
        return JsonResponse({'success': False, 'error': 'El nombre de la categoría no puede estar vacío.'}, status=400)

    if len(nombre) > 45:
        return JsonResponse({'success': False, 'error': 'El nombre no puede superar los 45 caracteres.'}, status=400)

    # Verificar duplicado (case-insensitive)
    if Categoria.objects.filter(nombre__iexact=nombre, activo=True).exists():
        existente = Categoria.objects.filter(nombre__iexact=nombre, activo=True).first()
        return JsonResponse({
            'success': False,
            'error': f'La categoría "{existente.nombre}" ya existe.',
            'duplicado': True,
            'id': existente.id_categoria,
            'nombre': existente.nombre,
        }, status=409)

    try:
        categoria = Categoria.objects.create(
            nombre=nombre,
            activo=True
        )
        # Invalidar caché de categorías
        cache.delete('categorias_activas')

        logger.info(f"Nueva categoría creada vía AJAX: '{nombre}' (id={categoria.id_categoria}) por user {request.user.pk}")
        return JsonResponse({
            'success': True,
            'id': categoria.id_categoria,
            'nombre': categoria.nombre,
        })
    except Exception as e:
        logger.exception("Error al crear categoría vía AJAX")
        return JsonResponse({'success': False, 'error': f'Error al guardar: {str(e)}'}, status=500)


@login_required
def api_nombres_producto(request):
    """
    API AJAX para obtener nombres únicos de productos existentes (no eliminados).
    GET → JSON: {"nombres": ["Cebolla", "Papa", "Tomate"]}
    """
    nombres_qs = Producto.objects.filter(
        eliminado=False
    ).exclude(
        nombre__isnull=True
    ).exclude(
        nombre=''
    ).values_list('nombre', flat=True).distinct().order_by('nombre')

    # Deduplicar preservando orden alfabético
    nombres = sorted(list(set(n.strip() for n in nombres_qs if n and n.strip())))

    return JsonResponse({'nombres': nombres})




def get_categorias_cached():
    """Obtiene categorías con caché de 1 hora"""
    cache_key = 'categorias_activas'
    categorias = cache.get(cache_key)
    if categorias is None:
        categorias = list(Categoria.objects.filter(activo=True))
        cache.set(cache_key, categorias, 3600)  # 1 hora
    return categorias


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
        'id_usuario'
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
        imagenes = pu.id_producto.get_imagenes()
        producto_data = {
            'id': pu.id_producto_usuario,
            'nombre': pu.id_producto.nombre,
            'descripcion': pu.id_producto.descripcion or '',
            'precio': float(pu.precio),
            'stock': pu.obtener_stock(),
            'stock_minimo': pu.id_producto.stock_minimo,
            'categoria_nombre': pu.id_producto.id_categoria.nombre,
            'agricultor_id': pu.id_usuario.id_users,
            'esta_agotado': pu.cantidad <= 0,
            'imagen': imagenes[0] if imagenes else None,
            'imagenes': imagenes,
            'es_mi_producto': True,
            'detailUrl': reverse('inventario:detalle', args=[pu.id_producto_usuario]),
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

    inventario_data = {
        'initialProducts': productos_transformados,
        'categories': [{'id': c.id_categoria, 'nombre': c.nombre} for c in categorias],
        'urls': {
            'listar': reverse('inventario:listar'),
            'crear': reverse('inventario:crear'),
            'venta_directa': reverse('inventario:venta_directa'),
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
        'inventario_json': inventario_data,
        'categorias': categorias,
    })


@login_required
def marketplace(request):
    """
    Vista del INICIO/MARKETPLACE - Muestra productos de OTROS usuarios
    Con botones de Agregar al carrito y Ver Detalle
    """
    # Obtener productos de OTROS usuarios (excluyendo los del usuario actual)
    productos = ProductoUsuario.objects.exclude(
        id_usuario=request.user
    ).select_related(
        'id_producto__id_categoria',
        'id_usuario'
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
        imagenes = pu.id_producto.get_imagenes()
        producto_data = {
            'id': pu.id_producto_usuario,
            'nombre': pu.id_producto.nombre,
            'descripcion': pu.id_producto.descripcion or '',
            'precio': float(pu.precio),
            'stock': pu.obtener_stock(),
            'stock_minimo': pu.id_producto.stock_minimo,
            'categoria_nombre': pu.id_producto.id_categoria.nombre,
            'agricultor_id': pu.id_usuario.id_users,
            'agricultor_nombre': f"{pu.id_usuario.nombres} {pu.id_usuario.apellidos}",
            'esta_agotado': pu.cantidad <= 0,
            'imagen': imagenes[0] if imagenes else None,
            'imagenes': imagenes,
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

    # ---- Estadísticas para el banner (HÉROE) del inicio ----
    # Se calculan sobre el queryset ya filtrado para mostrar cifras reales.
    try:
        num_agricultores = productos.values('id_usuario').distinct().count()
    except Exception:
        num_agricultores = 0
    num_categorias = len(categorias_list) if categorias_list else 0
    num_productos = productos.count()

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
        'marketplace_json': marketplace_data,
        # Datos para el HÉROE: estadísticas reales del marketplace
        'num_productos': num_productos,
        'num_agricultores': num_agricultores,
        'num_categorias': num_categorias,
    })


@login_required
def crear_producto(request):
    """
    Vista para registrar un nuevo producto agrícola en el catálogo y en el inventario del usuario.
    Usa el formulario ProductoForm y la plantilla producto_form.html.
    """
    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, requerir_imagen=True)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Obtener todos los archivos de imagen enviados
                    archivos_imagen = request.FILES.getlist('imagen')
                    primera_imagen = archivos_imagen[0] if archivos_imagen else None

                    # 1. Crear producto maestro en tblproducto
                    producto = Producto.objects.create(
                        nombre=form.cleaned_data['nombre'],
                        descripcion=form.cleaned_data.get('descripcion') or '',
                        id_categoria=form.cleaned_data['id_categoria'],
                        cantidad=form.cleaned_data['cantidad'],
                        stock_minimo=form.cleaned_data.get('stock_minimo') or 5,
                        imagen=primera_imagen
                    )

                    # Guardar imágenes secundarias en tblproducto_imagenes (a partir de la segunda)
                    if len(archivos_imagen) > 1:
                        for idx, img_file in enumerate(archivos_imagen[1:], start=1):
                            ProductoImagen.objects.create(
                                id_producto=producto,
                                imagen=img_file,
                                orden=idx
                            )

                    # 2. Crear relación en tblproductos_has_tblusuarios (ProductoUsuario)
                    precio_val = form.cleaned_data.get('precio')
                    if precio_val is None:
                        precio_val = Decimal('0.00')

                    pu = ProductoUsuario.objects.create(
                        id_producto=producto,
                        id_usuario=request.user,
                        cantidad=Decimal(str(form.cleaned_data['cantidad'])),
                        precio=precio_val
                    )

                    # 3. Registrar movimiento inicial de ingreso
                    try:
                        tipo_ingreso = TipoMovimiento.objects.filter(tipo__in=['compra', 'ingreso']).first()
                        if not tipo_ingreso:
                            tipo_ingreso, _ = TipoMovimiento.objects.get_or_create(tipo='compra')
                        movimiento = Movimiento.objects.create(
                            id_tipo_movimiento=tipo_ingreso,
                            id_usuario=request.user
                        )
                        ProductoUsuarioMovimiento.objects.create(
                            id_movimiento=movimiento,
                            id_producto_usuario=pu,
                            cantidad=form.cleaned_data['cantidad']
                        )
                    except Exception as e_mov:
                        logger.warning(f"No se pudo registrar movimiento inicial: {e_mov}")

                    messages.success(
                        request,
                        f'¡Producto "{producto.nombre}" registrado exitosamente en tu inventario!'
                    )
                    return redirect('inventario:listar')

            except Exception as e:
                logger.exception("Error al crear producto")
                messages.error(request, f'Error al registrar el producto: {str(e)}')
        else:
            logger.error(f"Errores de validación al crear producto: {form.errors}")
            messages.error(request, 'Por favor corrige los errores indicados en el formulario.')
    else:
        form = ProductoForm(initial={'stock_minimo': 5, 'cantidad': 1}, requerir_imagen=True)

    categorias = get_categorias_cached()

    return render(request, 'inventario/producto_form.html', {
        'form': form,
        'accion': 'crear',
        'categorias': categorias,
    })


@login_required
def venta_directa(request):
    """
    Vista de Venta Directa: Permite a un productor registrar una venta directa
    de productos de su inventario, descontando stock real y registrando el movimiento.
    """
    if request.method == 'POST':
        producto_usuario_id = request.POST.get('producto_usuario_id')
        cantidad_raw = request.POST.get('cantidad', 1)
        precio_raw = request.POST.get('precio')
        cliente_id = request.POST.get('cliente_id')
        nombre_producto = request.POST.get('nombre', '').strip()
        
        try:
            cantidad = int(cantidad_raw)
            if cantidad <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            messages.error(request, 'La cantidad a vender debe ser un número entero mayor a 0.')
            return redirect('inventario:venta_directa')

        pu = None
        # 1. Buscar el ProductoUsuario en el inventario del vendedor
        if producto_usuario_id:
            pu = ProductoUsuario.objects.filter(
                id_producto_usuario=producto_usuario_id,
                id_usuario=request.user
            ).select_related('id_producto', 'id_producto__id_categoria').first()

        if not pu and nombre_producto:
            pu = ProductoUsuario.objects.filter(
                id_producto__nombre__iexact=nombre_producto,
                id_usuario=request.user
            ).select_related('id_producto', 'id_producto__id_categoria').first()

        # Si aún no existe en el inventario del usuario pero existe en el catálogo maestro
        if not pu:
            categoria_id = request.POST.get('id_categoria')
            categoria = Categoria.objects.filter(pk=categoria_id).first() or Categoria.objects.first()
            prod_master, _ = Producto.objects.get_or_create(
                nombre=nombre_producto or 'Producto Agrícola',
                defaults={
                    'id_categoria': categoria,
                    'cantidad': 0,
                    'stock_minimo': 5,
                }
            )
            precio_val = Decimal(str(precio_raw)) if precio_raw else Decimal('0.00')
            pu = ProductoUsuario.objects.create(
                id_producto=prod_master,
                id_usuario=request.user,
                cantidad=Decimal(str(cantidad)), # Le asignamos la cantidad para que pueda venderse
                precio=precio_val
            )

        # 2. Validar stock disponible
        stock_actual = int(pu.cantidad)
        if cantidad > stock_actual:
            messages.error(
                request,
                f'Stock insuficiente para "{pu.id_producto.nombre}". '
                f'Stock disponible: {stock_actual} unidad(es), intentas vender: {cantidad}.'
            )
            return redirect('inventario:venta_directa')

        # 3. Actualizar precio si se ingresó uno específico
        if precio_raw:
            try:
                precio_ingresado = Decimal(str(precio_raw))
                if precio_ingresado > 0 and precio_ingresado != pu.precio:
                    pu.precio = precio_ingresado
                    pu.save(update_fields=['precio'])
            except Exception:
                pass

        # 4. Determinar el cliente comprador
        comprador = None
        if cliente_id:
            comprador = Tblusuarios.objects.filter(pk=cliente_id).first()
        if not comprador:
            # Selecciona un cliente registrado distinto al vendedor, o el propio usuario como venta directa mostrador
            comprador = Tblusuarios.objects.exclude(pk=request.user.pk).first() or request.user

        # 5. Registrar la transacción de venta directa
        try:
            with transaction.atomic():
                # Movimiento inicial como venta
                tipo_venta, _ = TipoMovimiento.objects.get_or_create(tipo='venta')
                movimiento = Movimiento.objects.create(
                    id_tipo_movimiento=tipo_venta,
                    id_usuario=comprador
                )

                # Detalle con cantidad negativa (según diseño BD para salidas/ventas)
                ProductoUsuarioMovimiento.objects.create(
                    id_movimiento=movimiento,
                    id_producto_usuario=pu,
                    cantidad=-cantidad
                )

                # Cambiar a 'vendida' para activar trigger trg_descontar_stock_vendida
                tipo_vendida, _ = TipoMovimiento.objects.get_or_create(tipo='vendida')
                movimiento.id_tipo_movimiento = tipo_vendida
                movimiento.save()

            messages.success(
                request,
                f'¡Venta Directa #{movimiento.id_movimiento} registrada con éxito! '
                f'Se vendieron {cantidad} unidad(es) de "{pu.id_producto.nombre}".'
            )
            return redirect('ventas:venta_detail', pk=movimiento.id_movimiento)

        except Exception as e:
            logger.exception("Error al registrar venta directa")
            messages.error(request, f'Error al procesar la venta directa: {str(e)}')
            return redirect('inventario:venta_directa')

    # GET: Cargar datos para el formulario de Venta Directa
    form = ProductoForm()
    categorias = get_categorias_cached()
    
    # Productos del inventario del propio vendedor (con stock disponible)
    mis_productos = ProductoUsuario.objects.filter(
        id_usuario=request.user,
        id_producto__eliminado=False
    ).select_related('id_producto', 'id_producto__id_categoria').order_by('id_producto__nombre')

    # Clientes disponibles para asignar la venta
    clientes_disponibles = Tblusuarios.objects.exclude(
        pk=request.user.pk
    ).order_by('nombres', 'apellidos')

    # Catálogo general de respaldo
    productos_existentes = Producto.objects.filter(
        eliminado=False
    ).select_related('id_categoria').order_by('nombre')
    
    return render(request, 'inventario/crear_producto.html', {
        'form': form,
        'categorias': categorias,
        'mis_productos': mis_productos,
        'clientes_disponibles': clientes_disponibles,
        'productos_existentes': productos_existentes
    })


@login_required
def editar_producto(request, pk):
    producto_usuario = get_object_or_404(
        ProductoUsuario.objects.select_related('id_producto', 'id_usuario'),
        id_producto_usuario=pk
    )
    
    # Verificar que el usuario sea el dueño o admin
    if producto_usuario.id_usuario != request.user and not (request.user.is_staff or request.user.is_superuser):
        messages.error(request, 'No tienes permiso para editar este producto.')
        return redirect('inventario:listar')
    
    # Stock actual de la publicación (entero, unidades no fraccionables)
    stock_actual = int(producto_usuario.cantidad)

    # Determinar si la publicación ya tiene al menos una imagen registrada
    tiene_imagen = bool(producto_usuario.id_producto.imagen) or producto_usuario.id_producto.imagenes_secundarias.exists()

    if request.method == 'POST':
        form = ProductoForm(request.POST, request.FILES, requerir_imagen=(not tiene_imagen))  # Eliminar instance= que no es válido para forms.Form
        if form.is_valid():
            nuevo_stock = int(form.cleaned_data['cantidad'])

            # Validación de servidor: no se permite reducir el stock desde la edición.
            if nuevo_stock < stock_actual:
                messages.error(
                    request,
                    f'No puedes reducir las unidades de stock. '
                    f'Stock actual: {stock_actual} unidad(es), intentas registrar: {nuevo_stock}. '
                    f'Solo se permite reabastecer (valor igual o mayor al actual).'
                )
                form.add_error('cantidad', f'Debe ser igual o mayor al stock actual ({stock_actual}).')
            else:
                with transaction.atomic():
                    # Actualizar campos del producto maestro (tblproducto)
                    # NOTA: nombre y categoría NO son editables (se conservan del registro original).
                    producto = producto_usuario.id_producto
                    producto.descripcion = form.cleaned_data['descripcion']
                    
                    # Actualizar imágenes si se proporcionan nuevas (conservando existentes)
                    archivos_nuevos = request.FILES.getlist('imagen')
                    if archivos_nuevos:
                        if not producto.imagen:
                            producto.imagen = archivos_nuevos[0]
                            archivos_a_agregar = archivos_nuevos[1:]
                        else:
                            archivos_a_agregar = archivos_nuevos

                        ultimo_orden = producto.imagenes_secundarias.count()
                        for idx, img_file in enumerate(archivos_a_agregar, start=ultimo_orden + 1):
                            ProductoImagen.objects.create(
                                id_producto=producto,
                                imagen=img_file,
                                orden=idx
                            )
                    
                    # TODOS los usuarios pueden editar stock_minimo
                    stock_minimo_value = form.cleaned_data.get('stock_minimo')
                    if stock_minimo_value is not None:
                        producto.stock_minimo = stock_minimo_value
                    
                    producto.save()
                    logger.info(f"Producto maestro actualizado: {producto.nombre}, stock_minimo: {producto.stock_minimo}")
                    
                    # Actualizar campos específicos del usuario (tblproductos_has_tblusuarios)
                    # NOTA: No se actualiza 'cantidad' aquí: el trigger de BD la gestiona.
                    producto_usuario.precio = form.cleaned_data['precio']
                    producto_usuario.save()
                    
                    # Reabastecimiento: cantidad nueva mayor que la actual
                    diferencia = nuevo_stock - stock_actual
                    if diferencia > 0:
                        # El trigger trg_actualizar_stock_oferta suma 'diferencia' al stock.
                        tipo_reab, _ = TipoMovimiento.objects.get_or_create(tipo='reabastecimiento')
                        movimiento = Movimiento.objects.create(
                            id_tipo_movimiento=tipo_reab,
                            id_usuario=request.user
                        )
                        ProductoUsuarioMovimiento.objects.create(
                            id_movimiento=movimiento,
                            id_producto_usuario=producto_usuario,
                            cantidad=diferencia
                        )
                        logger.info(
                            f"Reabastecimiento registrado: +{diferencia} unidades para "
                            f"ProductoUsuario #{producto_usuario.id_producto_usuario} "
                            f"(movimiento #{movimiento.id_movimiento})"
                        )
                    
                    logger.info(f"ProductoUsuario actualizado: cantidad={producto_usuario.cantidad}, precio={producto_usuario.precio}")
                    
                    messages.success(request, '¡Producto actualizado exitosamente!')
                    return redirect('inventario:listar')
        else:
            # Log de errores de validación para debugging
            logger.error(f"Errores de validación del formulario: {form.errors}")
            mensaje_error = formatear_errores_form(form) or 'Revisa los campos del formulario.'
            messages.error(request, f'No se pudo guardar. {mensaje_error}')
    else:
        # Preparar datos para el formulario
        initial_data = {
            'nombre': producto_usuario.id_producto.nombre,
            'descripcion': producto_usuario.id_producto.descripcion,
            'id_categoria': producto_usuario.id_producto.id_categoria,
            'stock_minimo': producto_usuario.id_producto.stock_minimo,
            'imagen': producto_usuario.id_producto.imagen,
            'cantidad': stock_actual,  # Entero: evita mostrar decimales (.00)
            'precio': producto_usuario.precio,
        }
        form = ProductoForm(initial=initial_data, requerir_imagen=(not tiene_imagen))
        # TODOS los usuarios pueden editar stock_minimo (sin restricciones)

    # Configurar el campo 'cantidad' para impedir bajar el stock (form + input)
    form.fields['cantidad'].widget.attrs['min'] = str(stock_actual)
    form.fields['cantidad'].min_value = stock_actual

    categorias = get_categorias_cached()
    
    # Preparar detalle de imágenes con IDs para poder eliminarlas individualmente
    imagenes_detalle = []
    if producto_usuario.id_producto.imagen:
        try:
            imagenes_detalle.append({
                'id': 'portada',
                'url': producto_usuario.id_producto.imagen.url,
                'es_portada': True
            })
        except Exception:
            pass
    for sec in producto_usuario.id_producto.imagenes_secundarias.all():
        try:
            if sec.imagen:
                imagenes_detalle.append({
                    'id': str(sec.id),
                    'url': sec.imagen.url,
                    'es_portada': False
                })
        except Exception:
            pass

    # Usar producto_form.html que ya existe
    return render(request, 'inventario/producto_form.html', {
        'form': form,
        'producto_usuario': producto_usuario,
        'producto': producto_usuario.id_producto,  # El template usa producto.nombre
        'imagenes': producto_usuario.id_producto.get_imagenes(),
        'imagenes_detalle': imagenes_detalle,
        'categorias': categorias,
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
    if producto_usuario.id_usuario != request.user and not (request.user.is_staff or request.user.is_superuser):
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


@login_required
def eliminar_imagen_producto(request, pk, img_id):
    """
    Elimina una imagen de un producto (sea la principal/portada o una secundaria).
    Solo el propietario o un administrador pueden eliminar imágenes.
    """
    producto_usuario = get_object_or_404(
        ProductoUsuario.objects.select_related('id_producto', 'id_usuario'),
        id_producto_usuario=pk
    )

    # Verificar permisos
    if producto_usuario.id_usuario != request.user and not (request.user.is_staff or request.user.is_superuser):
        msg = 'No tienes permiso para modificar las imágenes de este producto.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': msg}, status=403)
        messages.error(request, msg)
        return redirect('inventario:editar', pk=pk)

    if request.method == 'POST':
        producto = producto_usuario.id_producto
        with transaction.atomic():
            if str(img_id).lower() in ['portada', 'principal']:
                # Eliminar imagen principal
                if producto.imagen:
                    try:
                        # Si hay secundarias, promocionar la primera a principal
                        primera_sec = producto.imagenes_secundarias.order_by('orden', 'id').first()
                        if primera_sec:
                            producto.imagen = primera_sec.imagen
                            producto.save()
                            primera_sec.delete()
                        else:
                            try:
                                producto.imagen.delete(save=False)
                            except Exception:
                                pass
                            producto.imagen = None
                            producto.save()
                    except Exception as e:
                        logger.error(f"Error al eliminar imagen principal: {e}")
                        producto.imagen = None
                        producto.save()
            else:
                # Eliminar imagen secundaria de tblproducto_imagenes
                try:
                    sec_id = int(img_id)
                    img_sec = ProductoImagen.objects.filter(id=sec_id, id_producto=producto).first()
                    if img_sec:
                        try:
                            if img_sec.imagen:
                                img_sec.imagen.delete(save=False)
                        except Exception:
                            pass
                        img_sec.delete()
                    else:
                        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                            return JsonResponse({'success': False, 'error': 'Imagen no encontrada.'}, status=404)
                except ValueError:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({'success': False, 'error': 'ID de imagen inválido.'}, status=400)

        msg = 'Imagen eliminada exitosamente.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True, 
                'message': msg,
                'imagenes_restantes': producto.get_imagenes()
            })
        messages.success(request, msg)
        return redirect('inventario:editar', pk=pk)

    return redirect('inventario:editar', pk=pk)