"""
Servicio de Auditoría para el Panel de Administración de AgroSFT.
Registra todas las acciones administrativas con timestamp, admin, acción y detalles.
"""


def log_admin_action(request, accion, objetivo=None, detalles=None):
    """
    Registra una acción administrativa en la tabla admin_audit_log.

    Parámetros:
        request   : El objeto HttpRequest de Django (para obtener usuario e IP)
        accion    : Cadena corta describiendo la acción (ej. "Crear Usuario", "Aprobar Producto")
        objetivo  : Descripción del objeto afectado (ej. "usuario@email.com", "Tomates - ID 42")
        detalles  : Texto libre con información adicional (opcional)
    """
    try:
        from apps.usuarios.models.admin_audit_log_model import AdminAuditLog
        ip = _get_client_ip(request)
        AdminAuditLog.objects.create(
            admin=request.user,
            accion=accion,
            objetivo=objetivo or '',
            detalles=detalles or '',
            ip_address=ip,
        )
    except Exception:
        # Nunca dejar que el log rompa la funcionalidad principal
        pass


def _get_client_ip(request):
    """Extrae la IP real del cliente, considerando proxies."""
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')
