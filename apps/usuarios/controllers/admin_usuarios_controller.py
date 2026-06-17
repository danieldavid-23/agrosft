import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from apps.usuarios.models.profile_model import Tblusuarios
from apps.usuarios.forms.auth_forms import AdminUsuarioForm
from apps.usuarios.services.audit_log import log_admin_action


# ───────────────────────────────────────────────────────────────────────────
#  DECORADOR HELPER: Verifica que el usuario sea staff
# ───────────────────────────────────────────────────────────────────────────
def _require_staff(func):
    """Decorator que redirige si el usuario no es administrador."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, "Acceso denegado. No tienes permisos de administrador.")
            return redirect('inventario:marketplace')
        return func(request, *args, **kwargs)
    wrapper.__name__ = func.__name__
    return login_required(wrapper)


# ───────────────────────────────────────────────────────────────────────────
#  FUNCIONALIDAD 4: GESTIÓN DE USUARIOS CON BÚSQUEDA Y FILTROS
# ───────────────────────────────────────────────────────────────────────────
@_require_staff
def admin_usuarios_list(request):
    """Lista de usuarios con búsqueda por nombre/correo y filtros por rol/estado."""
    query = request.GET.get('q', '').strip()
    filtro_rol = request.GET.get('rol', 'todos')
    filtro_estado = request.GET.get('estado', 'todos')

    usuarios = Tblusuarios.objects.all().order_by('-id_users')

    # Búsqueda por texto
    if query:
        from django.db.models import Q
        usuarios = usuarios.filter(
            Q(nombres__icontains=query) |
            Q(apellidos__icontains=query) |
            Q(correo__icontains=query)
        )

    # Filtro por rol
    if filtro_rol == 'staff':
        usuarios = usuarios.filter(is_staff=True)
    elif filtro_rol == 'superadmin':
        usuarios = usuarios.filter(is_superuser=True)
    elif filtro_rol == 'usuarios':
        usuarios = usuarios.filter(is_staff=False, is_superuser=False)

    # Filtro por estado
    if filtro_estado == 'activos':
        usuarios = usuarios.filter(is_active=True)
    elif filtro_estado == 'inactivos':
        usuarios = usuarios.filter(is_active=False)

    total = usuarios.count()

    return render(request, 'usuarios/admin_usuarios_list.html', {
        'usuarios': usuarios,
        'titulo': 'Gestión de Usuarios',
        'query': query,
        'filtro_rol': filtro_rol,
        'filtro_estado': filtro_estado,
        'total': total,
    })


@_require_staff
def admin_usuario_crear(request):
    """Permite a un administrador crear un nuevo usuario."""
    if request.method == 'POST':
        form = AdminUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            log_admin_action(request, 'Crear Usuario', user.correo,
                             f"Nombres: {user.nombres} {user.apellidos} | Staff: {user.is_staff}")
            messages.success(request, f"Usuario {user.correo} creado exitosamente.")
            return redirect('usuarios:admin_usuarios_list')
    else:
        form = AdminUsuarioForm()

    return render(request, 'usuarios/admin_usuario_form.html', {
        'form': form,
        'titulo': 'Crear Nuevo Usuario',
        'is_edit': False
    })


@_require_staff
def admin_usuario_editar(request, pk):
    """Permite a un administrador editar un usuario existente."""
    usuario = get_object_or_404(Tblusuarios, id_users=pk)

    if request.method == 'POST':
        form = AdminUsuarioForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            log_admin_action(request, 'Editar Usuario', usuario.correo,
                             f"Staff: {usuario.is_staff} | Activo: {usuario.is_active}")
            messages.success(request, f"Usuario {usuario.correo} actualizado exitosamente.")
            return redirect('usuarios:admin_usuarios_list')
    else:
        form = AdminUsuarioForm(instance=usuario)

    return render(request, 'usuarios/admin_usuario_form.html', {
        'form': form,
        'titulo': f'Editar Usuario: {usuario.correo}',
        'usuario': usuario,
        'is_edit': True
    })


@_require_staff
def admin_usuario_toggle_activo(request, pk):
    """Activa o desactiva un usuario con un solo clic."""
    usuario = get_object_or_404(Tblusuarios, id_users=pk)

    if usuario.id_users == request.user.id_users:
        messages.error(request, "No puedes desactivar tu propia cuenta de administrador.")
    else:
        usuario.is_active = not usuario.is_active
        usuario.save()
        estado = "activado" if usuario.is_active else "desactivado"
        log_admin_action(request, f'Usuario {estado.capitalize()}', usuario.correo)
        messages.success(request, f"Usuario {usuario.correo} ha sido {estado} correctamente.")

    return redirect('usuarios:admin_usuarios_list')


# ───────────────────────────────────────────────────────────────────────────
#  ESTADÍSTICAS
# ───────────────────────────────────────────────────────────────────────────
@_require_staff
def admin_estadisticas(request):
    """Muestra estadísticas detalladas del rendimiento de la plataforma."""
    from apps.inventario.models.producto import Producto, ProductoUsuario, Categoria
    from apps.ventas.models.movimiento import ProductoUsuarioMovimiento
    from django.db.models import Count

    total_usuarios = Tblusuarios.objects.count()
    total_productos = Producto.objects.count()
    total_ofertas = ProductoUsuario.objects.count()

    detalles_ventas = ProductoUsuarioMovimiento.objects.filter(cantidad__lt=0).select_related(
        'id_producto_usuario',
        'id_producto_usuario__id_producto'
    )
    total_ventas_count = detalles_ventas.count()
    facturacion_total = sum(abs(v.cantidad) * v.id_producto_usuario.precio for v in detalles_ventas)

    categorias = Categoria.objects.annotate(num_productos=Count('producto')).filter(activo=True).order_by('-num_productos')

    transacciones_recientes = ProductoUsuarioMovimiento.objects.select_related(
        'id_producto_usuario',
        'id_producto_usuario__id_producto',
        'id_producto_usuario__id_usuario',
        'id_movimiento',
        'id_movimiento__id_usuario'
    ).order_by('-fecha_movimiento')[:6]

    recent_txs = []
    for tx in transacciones_recientes:
        es_venta = tx.cantidad < 0
        tipo = "Venta" if es_venta else "Abastecimiento"
        cantidad_abs = abs(tx.cantidad)
        subtotal = cantidad_abs * tx.id_producto_usuario.precio
        comprador = tx.id_movimiento.id_usuario
        vendedor = tx.id_producto_usuario.id_usuario
        recent_txs.append({
            'id': tx.id_movimiento_usuario,
            'fecha': tx.fecha_movimiento,
            'tipo': tipo,
            'es_venta': es_venta,
            'producto': tx.id_producto_usuario.id_producto.nombre,
            'vendedor': vendedor.get_full_name(),
            'comprador': comprador.get_full_name(),
            'cantidad': cantidad_abs,
            'precio_unitario': tx.id_producto_usuario.precio,
            'total': subtotal
        })

    return render(request, 'usuarios/admin_estadisticas.html', {
        'titulo': 'Estadísticas de la Plataforma',
        'total_usuarios': total_usuarios,
        'total_productos': total_productos,
        'total_ofertas': total_ofertas,
        'total_ventas_count': total_ventas_count,
        'facturacion_total': facturacion_total,
        'categorias': categorias,
        'recent_txs': recent_txs,
    })


# ───────────────────────────────────────────────────────────────────────────
#  FUNCIONALIDAD 1: MODERACIÓN DE PRODUCTOS PENDIENTES
# ───────────────────────────────────────────────────────────────────────────
@_require_staff
def admin_moderacion(request):
    """Muestra los productos con estado 'pendiente' para su aprobación o rechazo."""
    from apps.inventario.models.producto import Producto
    pendientes = Producto.objects.filter(
        estado='pendiente',
        eliminado=False
    ).select_related('id_categoria').order_by('-fecha_creacion')

    return render(request, 'usuarios/admin_moderacion.html', {
        'titulo': 'Moderación de Productos',
        'pendientes': pendientes,
    })


@_require_staff
def admin_aprobar_producto(request, pk):
    """Aprueba un producto pendiente (estado -> 'aprobado')."""
    from apps.inventario.models.producto import Producto
    producto = get_object_or_404(Producto, id_producto=pk, eliminado=False)
    if producto.estado == 'pendiente':
        producto.estado = 'aprobado'
        producto.save()
        log_admin_action(request, 'Aprobar Producto', f"{producto.nombre} (ID {pk})")
        messages.success(request, f"✅ Producto '{producto.nombre}' aprobado correctamente.")
    else:
        messages.warning(request, f"El producto '{producto.nombre}' no está en estado pendiente.")
    return redirect('usuarios:admin_moderacion')


@_require_staff
def admin_rechazar_producto(request, pk):
    """Rechaza un producto pendiente (estado -> 'rechazado')."""
    from apps.inventario.models.producto import Producto
    producto = get_object_or_404(Producto, id_producto=pk, eliminado=False)
    if producto.estado == 'pendiente':
        producto.estado = 'rechazado'
        producto.save()
        log_admin_action(request, 'Rechazar Producto', f"{producto.nombre} (ID {pk})")
        messages.warning(request, f"❌ Producto '{producto.nombre}' rechazado.")
    else:
        messages.warning(request, f"El producto '{producto.nombre}' no está en estado pendiente.")
    return redirect('usuarios:admin_moderacion')


# ───────────────────────────────────────────────────────────────────────────
#  FUNCIONALIDAD 2: GESTIÓN DE CATEGORÍAS
# ───────────────────────────────────────────────────────────────────────────
@_require_staff
def admin_categorias_list(request):
    """Lista todas las categorías de productos."""
    from apps.inventario.models.producto import Categoria
    from django.db.models import Count
    categorias = Categoria.objects.annotate(
        num_productos=Count('producto')
    ).order_by('nombre')
    return render(request, 'usuarios/admin_categorias.html', {
        'titulo': 'Gestión de Categorías',
        'categorias': categorias,
    })


@_require_staff
def admin_categoria_crear(request):
    """Crea una nueva categoría de producto."""
    from apps.inventario.models.producto import Categoria
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        if not nombre:
            messages.error(request, "El nombre de la categoría es obligatorio.")
        elif Categoria.objects.filter(nombre__iexact=nombre).exists():
            messages.error(request, f"Ya existe una categoría con el nombre '{nombre}'.")
        else:
            cat = Categoria.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                activo=True,
                created_at=timezone.now(),
                updated_at=timezone.now(),
            )
            log_admin_action(request, 'Crear Categoría', cat.nombre)
            messages.success(request, f"Categoría '{cat.nombre}' creada exitosamente.")
            return redirect('usuarios:admin_categorias_list')
    return render(request, 'usuarios/admin_categoria_form.html', {
        'titulo': 'Nueva Categoría',
        'is_edit': False,
    })


@_require_staff
def admin_categoria_editar(request, pk):
    """Edita una categoría existente."""
    from apps.inventario.models.producto import Categoria
    categoria = get_object_or_404(Categoria, id_categoria=pk)
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        descripcion = request.POST.get('descripcion', '').strip()
        if not nombre:
            messages.error(request, "El nombre es obligatorio.")
        else:
            categoria.nombre = nombre
            categoria.descripcion = descripcion
            categoria.updated_at = timezone.now()
            categoria.save()
            log_admin_action(request, 'Editar Categoría', categoria.nombre)
            messages.success(request, f"Categoría '{categoria.nombre}' actualizada.")
            return redirect('usuarios:admin_categorias_list')
    return render(request, 'usuarios/admin_categoria_form.html', {
        'titulo': f'Editar Categoría: {categoria.nombre}',
        'categoria': categoria,
        'is_edit': True,
    })


@_require_staff
def admin_categoria_toggle(request, pk):
    """Activa o desactiva una categoría."""
    from apps.inventario.models.producto import Categoria
    categoria = get_object_or_404(Categoria, id_categoria=pk)
    categoria.activo = not categoria.activo
    categoria.updated_at = timezone.now()
    categoria.save()
    estado = "activada" if categoria.activo else "desactivada"
    log_admin_action(request, f'Categoría {estado.capitalize()}', categoria.nombre)
    messages.success(request, f"Categoría '{categoria.nombre}' {estado}.")
    return redirect('usuarios:admin_categorias_list')


# ───────────────────────────────────────────────────────────────────────────
#  FUNCIONALIDAD 3: REPORTES CSV (compatibles con Excel)
# ───────────────────────────────────────────────────────────────────────────
@_require_staff
def admin_reporte_usuarios_csv(request):
    """Descarga la lista de usuarios como CSV."""
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="reporte_usuarios_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Nombres', 'Apellidos', 'Correo', 'Teléfono', 'Staff', 'Superadmin', 'Activo', 'Fecha Registro'])

    for u in Tblusuarios.objects.all().order_by('id_users'):
        writer.writerow([
            u.id_users,
            u.nombres,
            u.apellidos,
            u.correo,
            u.telefono or '',
            'Sí' if u.is_staff else 'No',
            'Sí' if u.is_superuser else 'No',
            'Sí' if u.is_active else 'No',
            u.fecha_creacion.strftime('%Y-%m-%d %H:%M') if u.fecha_creacion else '',
        ])

    log_admin_action(request, 'Descargar Reporte', 'Reporte de Usuarios CSV')
    return response


@_require_staff
def admin_reporte_productos_csv(request):
    """Descarga el catálogo de productos como CSV."""
    from apps.inventario.models.producto import Producto
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="reporte_productos_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Nombre', 'Categoría', 'Cantidad', 'Stock Mínimo', 'Estado', 'Eliminado', 'Fecha Creación'])

    for p in Producto.objects.select_related('id_categoria').filter(eliminado=False).order_by('id_producto'):
        writer.writerow([
            p.id_producto,
            p.nombre,
            p.id_categoria.nombre if p.id_categoria else '',
            p.cantidad,
            p.stock_minimo,
            p.estado,
            'No',
            p.fecha_creacion.strftime('%Y-%m-%d %H:%M') if p.fecha_creacion else '',
        ])

    log_admin_action(request, 'Descargar Reporte', 'Reporte de Productos CSV')
    return response


@_require_staff
def admin_reporte_ventas_csv(request):
    """Descarga el historial de ventas como CSV."""
    from apps.ventas.models.movimiento import ProductoUsuarioMovimiento
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="reporte_ventas_{timezone.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Fecha', 'Tipo', 'Producto', 'Vendedor', 'Comprador', 'Cantidad', 'Precio Unit.', 'Total'])

    transacciones = ProductoUsuarioMovimiento.objects.select_related(
        'id_producto_usuario',
        'id_producto_usuario__id_producto',
        'id_producto_usuario__id_usuario',
        'id_movimiento',
        'id_movimiento__id_usuario'
    ).order_by('-fecha_movimiento')

    for tx in transacciones:
        es_venta = tx.cantidad < 0
        tipo = "Venta" if es_venta else "Abastecimiento"
        cant = abs(tx.cantidad)
        precio = tx.id_producto_usuario.precio
        total = cant * precio
        writer.writerow([
            tx.id_movimiento_usuario,
            tx.fecha_movimiento.strftime('%Y-%m-%d %H:%M') if tx.fecha_movimiento else '',
            tipo,
            tx.id_producto_usuario.id_producto.nombre,
            tx.id_producto_usuario.id_usuario.get_full_name(),
            tx.id_movimiento.id_usuario.get_full_name(),
            cant,
            precio,
            total,
        ])

    log_admin_action(request, 'Descargar Reporte', 'Reporte de Ventas CSV')
    return response


# ───────────────────────────────────────────────────────────────────────────
#  FUNCIONALIDAD 5: REGISTRO DE AUDITORÍA
# ───────────────────────────────────────────────────────────────────────────
@_require_staff
def admin_audit_logs(request):
    """Muestra el historial de acciones administrativas."""
    from apps.usuarios.models.admin_audit_log_model import AdminAuditLog
    try:
        logs = AdminAuditLog.objects.select_related('admin').order_by('-fecha')[:200]
        error_tabla = False
    except Exception:
        logs = []
        error_tabla = True

    return render(request, 'usuarios/admin_audit_logs.html', {
        'titulo': 'Registro de Auditoría',
        'logs': logs,
        'error_tabla': error_tabla,
    })
