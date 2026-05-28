from django.db.models import Q
from django.utils import timezone
from apps.inventario.models import Producto, ProductoUsuario, Estado, Categoria
from core.utils.helpers import safe_int, EstadoProducto

class ProductoRepository:

    @staticmethod
    def get_by_filters(estado='', categoria_id='', nombre=''):
        """
        Obtiene productos con posibles filtros
        """
        queryset = ProductoUsuario.objects.select_related(
            'id_producto',
            'id_producto__id_categoria',
            'id_estado',
            'id_usuario'
        ).filter(
            id_producto_usuario__gt=0,
            id_producto__eliminado=False,
            id_producto__isnull=False,
            id_estado__isnull=False,
            id_usuario__isnull=False,
        )
        
        if estado:
            estado_obj = Estado.objects.filter(estado=estado).first()
            if estado_obj:
                queryset = queryset.filter(id_estado=estado_obj)
        
        if categoria_id:
            queryset = queryset.filter(id_producto__id_categoria=categoria_id)
        
        if nombre:
            queryset = queryset.filter(
                Q(id_producto__nombre__icontains=nombre) | 
                Q(id_producto__descripcion__icontains=nombre)
            )
        
        return queryset
    
    @staticmethod
    def get_all_with_filters(estado='', categoria_id='', nombre=''):
        """
        Obtiene todos los productos con posibles filtros
        """
        queryset = ProductoUsuario.objects.select_related(
            'id_producto',
            'id_producto__id_categoria',
            'id_estado',
            'id_usuario'
        ).filter(
            id_producto_usuario__gt=0,
            id_producto__eliminado=False,
            id_producto__isnull=False,
            id_estado__isnull=False,
            id_usuario__isnull=False,
        )
        
        if estado:
            estado_obj = Estado.objects.filter(estado=estado).first()
            if estado_obj:
                queryset = queryset.filter(id_estado=estado_obj)
        
        if categoria_id:
            queryset = queryset.filter(id_producto__id_categoria=categoria_id)
        
        if nombre:
            queryset = queryset.filter(
                Q(id_producto__nombre__icontains=nombre) | 
                Q(id_producto__descripcion__icontains=nombre)
            )
        
        return queryset
    
    @staticmethod
    def log_action(producto_id, user_id, action, field_changed=None, old_value=None, new_value=None):
        """
        Registra una acción en el historial de productos
        """
        # Este método podría necesitar actualizaciones según la estructura real de la base de datos
        pass
    
    @staticmethod
    def get_productos_by_estado(estado):
        """
        Obtiene productos por estado
        """
        estado_obj = Estado.objects.filter(estado=estado).first()
        if estado_obj:
            return ProductoUsuario.objects.filter(id_estado=estado_obj, id_producto__eliminado=False).select_related('id_producto', 'id_estado', 'id_usuario')
        return ProductoUsuario.objects.none()
    
    @staticmethod
    def get_productos_by_agricultor(usuario):
        """
        Obtiene productos por agricultor
        """
        return ProductoUsuario.objects.filter(id_usuario=usuario, id_producto__eliminado=False).select_related('id_producto', 'id_estado')
    
    @staticmethod
    def get_producto_detalle(producto_id):
        """
        Obtiene el detalle de un producto específico
        """
        return ProductoUsuario.objects.select_related('id_producto', 'id_estado', 'id_usuario').get(id_producto_usuario=producto_id)

    @staticmethod
    def get_paginated(page, per_page, filters=None):
        """
        Método auxiliar para obtener productos paginados
        """
        if filters is None:
            filters = {}
        estado = filters.get('estado', '')
        categoria_id = filters.get('categoria_id', '')
        nombre = filters.get('nombre', '')
        
        queryset = ProductoRepository.get_all_with_filters(estado, categoria_id, nombre)
        
        from django.core.paginator import Paginator
        paginator = Paginator(queryset, per_page)
        return paginator.get_page(page)

    @staticmethod
    def get_by_id(producto_id):
        """
        Obtiene un producto por ID
        """
        try:
            return ProductoUsuario.objects.select_related(
                'id_producto', 'id_estado', 'id_usuario'
            ).get(id_producto_usuario=producto_id)
        except ProductoUsuario.DoesNotExist:
            return None

    @staticmethod
    def create(producto_data, user_id):
        """
        Crea un nuevo producto
        """
        from apps.inventario.models import ProductoUsuario
        producto_usuario = ProductoUsuario()
        producto_usuario.id_producto_id = producto_data['producto_id']  # Ajustar según sea necesario
        producto_usuario.id_usuario_id = user_id
        producto_usuario.id_estado_id = producto_data.get('estado_id', 1)  # Asignar estado predeterminado
        producto_usuario.cantidad = str(producto_data.get('cantidad', 0))
        producto_usuario.precio = producto_data.get('precio', 0)
        producto_usuario.save()
        return producto_usuario

    @staticmethod
    def update(producto_id, producto_data, user_id):
        """
        Actualiza un producto existente
        """
        producto_usuario = ProductoRepository.get_by_id(producto_id)
        if producto_usuario:
            for attr, value in producto_data.items():
                if hasattr(producto_usuario, attr):
                    setattr(producto_usuario, attr, value)
            producto_usuario.save()
        return producto_usuario

    @staticmethod
    def delete(producto_usuario_id, user=None):
        """Soft delete: marks the product as eliminated instead of removing it."""
        try:
            producto_usuario = ProductoUsuario.objects.get(id_producto_usuario=producto_usuario_id)
            producto = producto_usuario.id_producto
            producto.eliminado = True
            producto.fecha_eliminacion = timezone.now()
            if user:
                producto.eliminado_por_id = user.pk
            producto.save()
            return True
        except ProductoUsuario.DoesNotExist:
            return False

    @staticmethod
    def restore(producto_id):
        """Restore a soft-deleted product."""
        try:
            producto = Producto.objects.get(id_producto=producto_id)
            producto.eliminado = False
            producto.fecha_eliminacion = None
            producto.eliminado_por_id = None
            producto.save()
            return True
        except Producto.DoesNotExist:
            return False