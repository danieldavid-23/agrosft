from django.db import models
from django.core.validators import FileExtensionValidator
from core.models.resizable_image import ResizableImageField
from core.utils.helpers import validate_image_size, image_cache_bust
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
    imagen = ResizableImageField(
        upload_to='productos/', 
        null=True, 
        blank=True, 
        db_column='imagen',
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp']),
            validate_image_size
        ]
    )
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

    def get_imagenes(self):
        """Retorna lista de URLs de todas las imágenes disponibles para el carrusel"""
        urls = []
        if self.imagen:
            try:
                urls.append(image_cache_bust(self.imagen.url))
            except Exception:
                pass
        for img in self.imagenes_secundarias.all():
            try:
                if img.imagen:
                    url_bust = image_cache_bust(img.imagen.url)
                    if url_bust not in urls:
                        urls.append(url_bust)
            except Exception:
                pass
        return urls


class ProductoImagen(models.Model):
    """
    Modelo para almacenar múltiples imágenes asociadas a un producto (carrusel)
    """
    id = models.AutoField(primary_key=True)
    id_producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='imagenes_secundarias',
        db_column='id_producto'
    )
    imagen = ResizableImageField(
        upload_to='productos/',
        db_column='imagen',
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp']),
            validate_image_size
        ]
    )
    orden = models.IntegerField(default=0, db_column='orden')
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')

    class Meta:
        db_table = 'tblproducto_imagenes'
        managed = False
        ordering = ['orden', 'id']
        verbose_name = 'Imagen de Producto'
        verbose_name_plural = 'Imágenes de Producto'

    def __str__(self):
        return f"Imagen {self.id} de {self.id_producto.nombre}"


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
        """Retorna el stock como entero no negativo para compatibilidad con templates"""
        from core.utils.helpers import safe_int
        val = safe_int(self.cantidad)
        return max(0, val)