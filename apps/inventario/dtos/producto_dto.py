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
    stock: int
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
            stock=producto.stock,
            stock_minimo=producto.stock_minimo,
            agricultor_id=producto.agricultor_id,
            estado=producto.estado,
            esta_agotado=producto.stock == 0,
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
    stock: int
    stock_minimo: Optional[int] = 5
    
    def validate(self):
        errors = []
        
        if not self.nombre or len(self.nombre.strip()) < 3:
            errors.append("El nombre debe tener al menos 3 caracteres")
        
        if not self.precio or self.precio <= 0:
            errors.append("El precio debe ser mayor a 0")
        
        if self.stock is None or self.stock < 0:
            errors.append("El stock debe ser un número positivo")
        
        if errors:
            raise ValidationError(errors)

@dataclass
class ProductoUpdateDTO:
    """DTO para actualizar producto"""
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    categoria_id: Optional[int] = None
    precio: Optional[float] = None
    stock: Optional[int] = None
    stock_minimo: Optional[int] = None
    
    def validate(self):
        errors = []
        
        if self.nombre is not None and len(self.nombre.strip()) < 3:
            errors.append("El nombre debe tener al menos 3 caracteres")
        
        if self.precio is not None and self.precio <= 0:
            errors.append("El precio debe ser mayor a 0")
        
        if self.stock is not None and self.stock < 0:
            errors.append("El stock debe ser un número positivo")
        
        if errors:
            raise ValidationError(errors)