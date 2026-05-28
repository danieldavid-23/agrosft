from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
from django.core.exceptions import ValidationError

@dataclass
class ProductoDTO:
    """DTO para respuesta de productos"""
    id: int
    nombre: str
    descripcion: str
    categoria_id: int
    categoria_nombre: str
    precio: float
    cantidad: int  # Cambiado de stock a cantidad
    stock_minimo: int
    agricultor_id: int
    estado: str
    esta_agotado: bool
    created_at: str
    updated_at: str
    
    @classmethod
    def from_model(cls, producto):
        if not producto:
            return None
        
        # Obtener nombre de categoría si existe
        categoria_nombre = producto.categoria.nombre if hasattr(producto, 'categoria') and producto.categoria else ''
        
        return cls(
            id=producto.id,
            nombre=producto.nombre,
            descripcion=producto.descripcion,
            categoria_id=producto.categoria_id,
            categoria_nombre=categoria_nombre,
            precio=float(producto.precio),
            cantidad=int(producto.cantidad),  # Cambiado de stock a cantidad
            stock_minimo=producto.stock_minimo,
            agricultor_id=producto.agricultor_id,
            estado=producto.estado,
            esta_agotado=producto.cantidad == 0,  # Cambiado de stock a cantidad
            created_at=producto.created_at.strftime('%Y-%m-%d %H:%M'),
            updated_at=producto.updated_at.strftime('%Y-%m-%d %H:%M')
        )

@dataclass
class ProductoCreateDTO:
    """DTO para crear producto"""
    nombre: str
    descripcion: str
    categoria_id: int
    precio: float
    cantidad: int  # Cambiado de stock a cantidad
    stock_minimo: Optional[int] = 5
    
    def validate(self):
        errors = []
        
        if not self.nombre or len(self.nombre.strip()) < 3:
            errors.append("El nombre debe tener al menos 3 caracteres")
        
        if not self.precio or self.precio <= 0:
            errors.append("El precio debe ser mayor a 0")
        
        if self.cantidad is None or self.cantidad < 0:  # Cambiado de stock a cantidad
            errors.append("La cantidad debe ser un número positivo")
        
        if errors:
            raise ValidationError(errors)


@dataclass
class ProductoUsuarioDTO:
    """DTO para respuesta de productos de usuario (publicaciones)"""
    id_producto_usuario: int
    producto_id: int
    producto_nombre: str
    usuario_id: int
    usuario_nombre: str
    cantidad: int
    precio: float
    estado: str
    calificacion_promedio: Optional[float] = None
    fecha_creacion: str = ''
    
    @classmethod
    def from_model(cls, producto_usuario):
        if not producto_usuario:
            return None
        
        return cls(
            id_producto_usuario=producto_usuario.id_producto_usuario,
            producto_id=producto_usuario.id_producto.id_producto,
            producto_nombre=producto_usuario.id_producto.nombre,
            usuario_id=producto_usuario.id_usuario.id_users,
            usuario_nombre=f"{producto_usuario.id_usuario.nombres} {producto_usuario.id_usuario.apellidos}",
            cantidad=int(producto_usuario.cantidad) if producto_usuario.cantidad else 0,
            precio=float(producto_usuario.precio),
            estado=producto_usuario.id_estado.estado,
            calificacion_promedio=float(producto_usuario.calificacion_promedio) if producto_usuario.calificacion_promedio else None,
            fecha_creacion=producto_usuario.fecha_creacion.strftime('%Y-%m-%d %H:%M') if producto_usuario.fecha_creacion else ''
        )

@dataclass
class ProductoUpdateDTO:
    """DTO para actualizar producto"""
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    categoria_id: Optional[int] = None
    precio: Optional[float] = None
    cantidad: Optional[int] = None  # Cambiado de stock a cantidad
    stock_minimo: Optional[int] = None
    
    def validate(self):
        errors = []
        
        if self.nombre is not None and len(self.nombre.strip()) < 3:
            errors.append("El nombre debe tener al menos 3 caracteres")
        
        if self.precio is not None and self.precio <= 0:
            errors.append("El precio debe ser mayor a 0")
        
        if self.cantidad is not None and self.cantidad < 0:  # Cambiado de stock a cantidad
            errors.append("La cantidad debe ser un número positivo")
        
        if errors:
            raise ValidationError(errors)