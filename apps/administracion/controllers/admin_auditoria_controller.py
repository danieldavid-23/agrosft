"""
Controlador para la auditoría administrativa del Panel de Administración.
"""
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from apps.usuarios.models.admin_audit_log_model import AdminAuditLog
from .admin_controller import admin_required, registrar_auditoria


@admin_required
def lista_auditoria(request):
    """Listado de acciones administrativas registradas."""
    logs = AdminAuditLog.objects.select_related('admin').order_by('-fecha')

    q = request.GET.get('q', '').strip()
    if q:
        logs = logs.filter(
            accion__icontains=q
        ) | logs.filter(objetivo__icontains=q) | logs.filter(detalles__icontains=q)

    contexto = {
        'titulo': 'Auditoría',
        'logs': logs,
        'q': q,
        'seccion_activa': 'auditoria',
    }
    return render(request, 'administracion/auditoria/lista.html', contexto)


@admin_required
def limpiar_auditoria(request):
    """Elimina todos los registros de auditoría."""
    if request.method == 'POST':
        registrar_auditoria(
            request.user, 'Limpiar auditoría',
            objetivo='Todos los registros', request=request,
        )
        AdminAuditLog.objects.all().delete()
        messages.success(request, 'Los registros de auditoría fueron eliminados.')
    return redirect('administracion:auditoria')