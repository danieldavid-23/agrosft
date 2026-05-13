from ..models import Producto, HistorialProducto
from .base_repository import BaseRepository
from django.core.paginator import Paginator
from django.db.models import Q

class ProductoRepository(BaseRepository):
    
    def get_by_id(self, id):
        try:
            return Producto.objects.get(id=id, eliminado=False)
        except Producto.DoesNotExist:
            return None
    
    def get_all(self, filters=None):
        queryset = Producto.objects.filter(eliminado=False)
        
        if filters:
            if filters.get('estado'):
                queryset = queryset.filter(estado=filters['estado'])
            if filters.get('categoria_id'):
                queryset = queryset.filter(categoria_id=filters['categoria_id'])
            if filters.get('agricultor_id'):
                queryset = queryset.filter(agricultor_id=filters['agricultor_id'])
            if filters.get('agricultor'):
                queryset = queryset.filter(agricultor=filters['agricultor'])
            if filters.get('search'):
                queryset = queryset.filter(nombre__icontains=filters['search'])
        
        return queryset.select_related('categoria').order_by('-created_at')
    
    def get_paginated(self, page=1, per_page=20, filters=None):
        queryset = self.get_all(filters)
        paginator = Paginator(queryset, per_page)
        return paginator.get_page(page)
    
    def create(self, data, usuario_id=None):
        producto = Producto.objects.create(**data)
        
        # Registrar historial
        HistorialProducto.objects.create(
            producto_id=producto.id,
            usuario_id=usuario_id,
            accion='creacion',
            valor_nuevo=f"Producto creado: {producto.nombre}"
        )
        
        return producto
    
    def update(self, id, data, usuario_id=None):
        producto = self.get_by_id(id)
        if not producto:
            return None
        
        # Registrar cambios antes de actualizar
        cambios = []
        for key, value in data.items():
            old_value = getattr(producto, key)
            if old_value != value:
                cambios.append({
                    'campo': key,
                    'anterior': old_value,
                    'nuevo': value
                })
        
        # Actualizar producto
        for key, value in data.items():
            setattr(producto, key, value)
        producto.save()
        
        # Guardar historial de cambios
        for cambio in cambios:
            HistorialProducto.objects.create(
                producto_id=producto.id,
                usuario_id=usuario_id,
                accion='modificacion',
                campo_modificado=cambio['campo'],
                valor_anterior=str(cambio['anterior']),
                valor_nuevo=str(cambio['nuevo'])
            )
        
        return producto
    
    def delete(self, id, usuario_id=None):
        producto = self.get_by_id(id)
        if producto:
            producto.soft_delete(usuario_id)
            
            HistorialProducto.objects.create(
                producto_id=producto.id,
                usuario_id=usuario_id,
                accion='eliminacion'
            )
            return True
        return False
    
    def get_productos_pendientes(self):
        return Producto.objects.filter(
            estado='pendiente', 
            eliminado=False
        ).select_related('categoria')
    
    def get_productos_por_agricultor(self, agricultor_id):
        return Producto.objects.filter(
            agricultor_id=agricultor_id,
            eliminado=False
        ).select_related('categoria')