"""
Controlador principal del Panel de Administración de AgroSFT.

Brinda acceso solo a usuarios staff/superusuario y expone el dashboard
con estadísticas agregadas de la plataforma.
"""
from functools import wraps
from django.contrib import messages
from django.shortcuts import render, redirect
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta

from apps.usuarios.models.profile_model import Tblusuarios
from apps.inventario.models import Producto, ProductoUsuario, Categoria
from apps.ventas.models.movimiento import Movimiento, ProductoUsuarioMovimiento
from apps.facturacion.models import Factura
from apps.clientes.models import Cliente
from apps.usuarios.models.admin_audit_log_model import AdminAuditLog


def admin_required(view_func):
    """
    Decorador que restringe el acceso al panel solo a usuarios
    staff o superusuario autenticados.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('usuarios:login')
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'No tienes permisos para acceder al panel de administración.')
            return redirect('inventario:marketplace')
        return view_func(request, *args, **kwargs)
    return _wrapped


def registrar_auditoria(admin, accion, objetivo=None, detalles=None, request=None):
    """
    Registra una acción administrativa en el log de auditoría.
    """
    try:
        AdminAuditLog.objects.create(
            admin=admin,
            accion=accion,
            objetivo=objetivo,
            detalles=detalles,
            ip_address=request.META.get('REMOTE_ADDR') if request else None,
        )
    except Exception:
        pass


@admin_required
def dashboard(request):
    """Vista principal del panel con estadísticas en tiempo real."""
    # Totales generales
    total_usuarios = Tblusuarios.objects.count()
    usuarios_activos = Tblusuarios.objects.filter(is_active=True).count()
    total_productos = Producto.objects.filter(eliminado=False).count()
    total_publicaciones = ProductoUsuario.objects.count()
    total_categorias = Categoria.objects.count()

    # Movimientos y facturación
    total_movimientos = Movimiento.objects.count()
    total_facturas = Factura.objects.count()
    monto_facturado = Factura.objects.filter(estado='emitida').aggregate(t=Sum('total'))['t'] or 0

    # Stock total y productos con stock bajo
    stock_total = Producto.objects.filter(eliminado=False).aggregate(s=Sum('cantidad'))['s'] or 0
    stock_bajo = Producto.objects.filter(eliminado=False, cantidad__lte=5).count()

    # Últimos registros
    ultimos_usuarios = Tblusuarios.objects.order_by('-fecha_creacion')[:5]
    ultimas_facturas = Factura.objects.order_by('-creada_en')[:5]
    ultimas_auditorias = AdminAuditLog.objects.order_by('-fecha')[:6]

    # Actividad de los últimos 7 días
    hace_7_dias = timezone.now() - timedelta(days=7)
    nuevos_usuarios_semana = Tblusuarios.objects.filter(fecha_creacion__gte=hace_7_dias).count()
    facturas_semana = Factura.objects.filter(creada_en__gte=hace_7_dias).count()

    contexto = {
        'titulo': 'Dashboard',
        'stats': {
            'usuarios': total_usuarios,
            'usuarios_activos': usuarios_activos,
            'productos': total_productos,
            'publicaciones': total_publicaciones,
            'categorias': total_categorias,
            'movimientos': total_movimientos,
            'facturas': total_facturas,
            'monto_facturado': monto_facturado,
            'stock_total': stock_total,
            'stock_bajo': stock_bajo,
            'nuevos_usuarios_semana': nuevos_usuarios_semana,
            'facturas_semana': facturas_semana,
        },
        'ultimos_usuarios': ultimos_usuarios,
        'ultimas_facturas': ultimas_facturas,
        'ultimas_auditorias': ultimas_auditorias,
        'seccion_activa': 'dashboard',
    }
    return render(request, 'administracion/dashboard.html', contexto)