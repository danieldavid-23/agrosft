from django.db import models
from apps.usuarios.models.profile_model import Tblusuarios


class Estado(models.Model):
    """
    Modelo que representa la tabla estado en la base de datos
    Define los estados de publicación: Aprobado, Pendiente, Rechazado
    """
    id_estado = models.AutoField(primary_key=True, db_column='id_estado')
    estado = models.CharField(max_length=45, db_column='estado')

    class Meta:
        db_table = 'estado'
        managed = False
        verbose_name = 'Estado'
        verbose_name_plural = 'Estados'

    def __str__(self):
        return self.estado


class TipoMovimiento(models.Model):
    """
    Modelo que representa la tabla tipo_movimiento en la base de datos
    Define los tipos de movimiento: 'compra' (abastecimiento) y 'venta' (producto vendido)
    """
    id_tipo_movimiento = models.AutoField(primary_key=True, db_column='id_tipo_movimiento')
    tipo = models.CharField(max_length=45, db_column='tipo_movimiento')

    class Meta:
        db_table = 'tipo_movimiento'
        managed = False
        verbose_name = 'Tipo de Movimiento'
        verbose_name_plural = 'Tipos de Movimiento'

    def __str__(self):
        return self.tipo


class Categoria(models.Model):
    """
    Modelo que representa la tabla tblcategoria en la base de datos
    Categorías de productos: Frutas, Verduras, Tubérculos, Granos y Cereales, Insumos Agrícolas
    """
    id_categoria = models.AutoField(primary_key=True, db_column='idt_categoria')
    nombre = models.CharField(max_length=45, db_column='categoria')
    descripcion = models.TextField(blank=True, null=True, db_column='descripcion')
    activo = models.BooleanField(default=True, db_column='activo')
    created_at = models.DateTimeField(db_column='created_at', null=True, blank=True)
    updated_at = models.DateTimeField(db_column='updated_at', null=True, blank=True)

    class Meta:
        db_table = 'tblcategoria'
        managed = False
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """
    Modelo que representa la tabla tblproducto en la base de datos
    Catálogo unificado de productos genéricos (evita redundancia de información)
    """
    id_producto = models.AutoField(primary_key=True, db_column='id_productos')
    nombre = models.CharField(max_length=45, db_column='nombre')
    descripcion = models.TextField(blank=True, null=True, db_column='descripcion')
    cantidad = models.IntegerField(db_column='cantidad')
    fecha_creacion = models.DateTimeField(auto_now_add=True, db_column='fecha_creacion')
    id_categoria = models.ForeignKey(
        Categoria, 
        on_delete=models.CASCADE, 
        db_column='tblcategoria_idt_categoria'
    )
    stock_minimo = models.IntegerField(default=5, db_column='stock_minimo')
    estado = models.CharField(max_length=20, default='pendiente', db_column='estado')
    eliminado = models.BooleanField(default=False, db_column='eliminado')
    fecha_eliminacion = models.DateTimeField(null=True, blank=True, db_column='fecha_eliminacion')
    eliminado_por_id = models.IntegerField(null=True, blank=True, db_column='eliminado_por_id')
    updated_at = models.DateTimeField(null=True, blank=True, db_column='updated_at')

    class Meta:
        db_table = 'tblproducto'
        managed = False
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return self.nombre


class ProductoUsuario(models.Model):
    """
    Modelo que representa la tabla tblproductos_has_tblusuarios en la base de datos
    Relación muchos-a-muchos entre productos y usuarios con datos específicos de cada publicación:
    - Precio por vendedor
    - Stock disponible (cantidad)
    - Estado de la publicación
    - Calificación promedio (actualizada automáticamente por triggers)
    """
    id_producto_usuario = models.AutoField(primary_key=True, db_column='id_pd_us')
    id_producto = models.ForeignKey(
        Producto, 
        on_delete=models.CASCADE, 
        db_column='tblproductos_id_productos'
    )
    id_usuario = models.ForeignKey(
        Tblusuarios, 
        on_delete=models.CASCADE, 
        db_column='tblusuarios_id_users'
    )
    id_estado = models.ForeignKey(
        Estado, 
        on_delete=models.CASCADE, 
        db_column='Estado_id_estado'
    )
    cantidad = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        db_column='cantidad',
        help_text='Stock disponible para esta publicación'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True, db_column='fecha_creacion')
    precio = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        db_column='precio'
    )
    calificacion_promedio = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        null=True, 
        blank=True,
        db_column='calificacion_promedio',
        help_text='Promedio de calificaciones (actualizado por triggers de BD)'
    )

    class Meta:
        db_table = 'tblproductos_has_tblusuarios'
        managed = False
        verbose_name = 'Producto de Usuario'
        verbose_name_plural = 'Productos de Usuarios'

    def __str__(self):
        return f"{self.id_producto.nombre} - {self.id_usuario.nombres} {self.id_usuario.apellidos}"
    
    def obtener_stock(self):
        """Retorna el stock como entero para compatibilidad con templates"""
        from core.utils.helpers import safe_int
        return safe_int(self.cantidad)


class Calificacion(models.Model):
    """
    Modelo que representa la tabla calificacion en la base de datos
    NOTA: Esta tabla parece ser una escala de referencia pero solo tiene 1 registro (valor 5).
    Las calificaciones reales se almacenan en ProductoUsuarioMovimiento.calificacion
    """
    id_calificacion = models.AutoField(primary_key=True, db_column='id_calificacion')
    calificacion = models.IntegerField(db_column='calificacion')

    class Meta:
        db_table = 'calificacion'
        managed = False
        verbose_name = 'Calificación (Referencia)'
        verbose_name_plural = 'Calificaciones (Referencia)'

    def __str__(self):
        return f"Calificación: {self.calificacion}"