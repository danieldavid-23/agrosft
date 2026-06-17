from django.db import models
from apps.usuarios.models.profile_model import Tblusuarios


class AdminAuditLog(models.Model):
    """
    Modelo que representa la tabla admin_audit_log en la base de datos.
    Registra todas las acciones administrativas realizadas en el panel web.
    """
    id_log = models.AutoField(primary_key=True, db_column='id_log')
    admin = models.ForeignKey(
        Tblusuarios,
        on_delete=models.SET_NULL,
        null=True,
        db_column='id_admin'
    )
    accion = models.CharField(max_length=100, db_column='accion')
    objetivo = models.CharField(max_length=255, blank=True, null=True, db_column='objetivo')
    detalles = models.TextField(blank=True, null=True, db_column='detalles')
    ip_address = models.GenericIPAddressField(blank=True, null=True, db_column='ip_address')
    fecha = models.DateTimeField(auto_now_add=True, db_column='fecha')

    class Meta:
        db_table = 'admin_audit_log'
        managed = False  # La tabla se crea manualmente en phpMyAdmin
        verbose_name = 'Log de Auditoría'
        verbose_name_plural = 'Logs de Auditoría'
        ordering = ['-fecha']

    def __str__(self):
        admin_name = self.admin.get_full_name() if self.admin else 'Sistema'
        return f"[{self.fecha}] {admin_name} - {self.accion}: {self.objetivo}"
