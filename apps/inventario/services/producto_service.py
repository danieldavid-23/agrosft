from ..repositories.producto_repository import ProductoRepository
from ..dtos.producto_dto import ProductoDTO, ProductoCreateDTO, ProductoUpdateDTO
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

class ProductoService:
    
    def __init__(self):
        self.repository = ProductoRepository()
    
    def listar_productos(self, page=1, filters=None):
        """Lista productos con paginación"""
        productos = self.repository.get_paginated(page, 20, filters)
        
        # Convertir a DTOs
        items = [ProductoDTO.from_model(p) for p in productos]
        
        return {
            'items': items,
            'total': productos.paginator.count if productos.paginator else len(items),
            'page': page,
            'has_next': productos.has_next(),
            'has_prev': productos.has_previous(),
        }
    
    def obtener_producto(self, producto_id):
        """Obtiene un producto por ID"""
        producto = self.repository.get_by_id(producto_id)
        return ProductoDTO.from_model(producto) if producto else None
    
    def crear_producto(self, data, usuario):
        """Crea un nuevo producto (RF-11)"""
        # Validar datos
        try:
            dto = ProductoCreateDTO(**data)
            dto.validate()
        except (ValidationError, TypeError) as e:
            logger.warning(f"Validation failed when creating product for user {getattr(usuario, 'id', usuario)}: {str(e)}")
            raise
        
        # Preparar datos para el repositorio
        producto_data = {
            'nombre': dto.nombre,
            'descripcion': dto.descripcion,
            'categoria_id': dto.categoria_id,
            'precio': dto.precio,
            'cantidad': dto.cantidad,  # Cambiado de stock a cantidad
            'stock_minimo': dto.stock_minimo,
            'agricultor': usuario,
            'estado': 'pendiente'  # RF-11b
        }
        
        # Crear producto
        try:
            producto = self.repository.create(producto_data, usuario.id)
        except Exception as e:
            logger.error(f"Error creating product for user {getattr(usuario, 'id', usuario)}: {str(e)}", exc_info=True)
            raise
        logger.info(f"Product '{dto.nombre}' created via service by user {getattr(usuario, 'id', usuario)}")
        return ProductoDTO.from_model(producto)
    
    def actualizar_producto(self, producto_id, data, usuario):
        """Actualiza un producto (RF-12)"""
        # Verificar que el producto existe
        producto = self.repository.get_by_id(producto_id)
        if not producto:
            logger.warning(f"Update failed: product {producto_id} not found (requested by user {getattr(usuario, 'id', usuario)})")
            raise ValidationError("Producto no encontrado")
        
        # Verificar permisos (RF-12)
        if producto.agricultor != usuario:
            # Verificar si es admin
            # Aquí deberías verificar permisos del usuario
            pass
        
        # Validar datos
        try:
            dto = ProductoUpdateDTO(**data)
            dto.validate()
        except (ValidationError, TypeError) as e:
            logger.warning(f"Validation failed when updating product {producto_id}: {str(e)}")
            raise
        
        # Preparar datos para actualizar (solo campos proporcionados)
        producto_data = {}
        for field in ['nombre', 'descripcion', 'categoria_id', 'precio', 'cantidad', 'stock_minimo']:  # Cambiado de stock a cantidad
            if hasattr(dto, field) and getattr(dto, field) is not None:
                producto_data[field] = getattr(dto, field)
        
        # Actualizar producto
        try:
            producto_actualizado = self.repository.update(producto_id, producto_data, usuario.id)
        except Exception as e:
            logger.error(f"Error updating product {producto_id}: {str(e)}", exc_info=True)
            raise
        return ProductoDTO.from_model(producto_actualizado)
    
    def eliminar_producto(self, producto_id, usuario):
        """Elimina un producto (RF-13)"""
        producto = self.repository.get_by_id(producto_id)
        if not producto:
            logger.warning(f"Delete failed: product {producto_id} not found (requested by user {getattr(usuario, 'id', usuario)})")
            raise ValidationError("Producto no encontrado")
        
        # Verificar si tiene pedidos activos (RF-13b)
        # Aquí deberías consultar al servicio de pedidos
        # if self.tiene_pedidos_activos(producto_id):
        #     raise ValidationError("No se puede eliminar: tiene pedidos activos")
        
        try:
            result = self.repository.delete(producto_id, user=usuario)
        except Exception as e:
            logger.error(f"Error deleting product {producto_id}: {str(e)}", exc_info=True)
            raise
        logger.info(f"Product {producto_id} deleted via service by user {getattr(usuario, 'id', usuario)}")
        return result
    
    def aprobar_producto(self, producto_id, usuario, aprobado=True):
        """Aprueba o rechaza un producto"""
        estado = 'aprobado' if aprobado else 'rechazado'
        
        producto = self.repository.update(
            producto_id, 
            {'estado': estado},
            usuario.id
        )
        
        return ProductoDTO.from_model(producto)