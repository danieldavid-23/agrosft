# NOTA: Estos modelos apuntan a tablas que NO existen en la BD actual
# from .solicitud import SolicitudCompra, DetalleSolicitudCompra
# from .venta import Venta, DetalleVenta
from .movimiento import Movimiento, ProductoUsuarioMovimiento

__all__ = [
    # 'SolicitudCompra', 
    # 'DetalleSolicitudCompra', 
    # 'Venta', 
    # 'DetalleVenta',
    'Movimiento',
    'ProductoUsuarioMovimiento'
]