"""
Core utility helpers for AgroSFT.
Provides safe type conversions, shared constants, and utility functions.
"""
import logging
import re
import urllib.parse

logger = logging.getLogger(__name__)


class EstadoProducto:
    """Constants for product states matching database values exactly."""
    PENDIENTE = 'Pendiente'
    APROBADO = 'Aprobado'
    RECHAZADO = 'Rechazado'

    @classmethod
    def choices(cls):
        return [cls.PENDIENTE, cls.APROBADO, cls.RECHAZADO]

    @classmethod
    def is_valid(cls, value):
        """Check if a value is a valid estado (case-insensitive)."""
        return value.capitalize() in cls.choices() if value else False


class EstadoSolicitud:
    """Constants for purchase request states."""
    PENDIENTE = 'pendiente'
    ACEPTADA = 'aceptada'
    RECHAZADA = 'rechazada'
    VENDIDO = 'vendido'
    CANCELADO = 'cancelado'


def safe_int(value, default=0):
    """
    Safely convert a value to integer.
    Handles VARCHAR cantidad fields that may contain non-numeric data.
    
    Args:
        value: The value to convert (can be str, None, or any type)
        default: Default value to return on conversion failure
    
    Returns:
        int: The converted value or default
    """
    if value is None:
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        logger.warning(f"Failed to convert '{value}' to int, using default={default}")
        return default


def safe_decimal(value, default=0.0):
    """
    Safely convert a value to float/decimal.
    
    Args:
        value: The value to convert
        default: Default value to return on conversion failure
    
    Returns:
        float: The converted value or default
    """
    if value is None:
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        logger.warning(f"Failed to convert '{value}' to decimal, using default={default}")
        return default


def generar_whatsapp_link(telefono, mensaje=""):
    """
    Genera un enlace de WhatsApp wa.me con formato internacional.
    Para Colombia (+57): elimina caracteres no dígitos, antepone 57 si es necesario.

    Args:
        telefono: Número de teléfono (con o sin formato)
        mensaje: Texto predefinido para el chat (opcional)

    Returns:
        str: URL https://wa.me/57XXXXXXXXXX?text=... o cadena vacía si no hay teléfono
    """
    if not telefono:
        return ""

    digitos = re.sub(r'\D', '', str(telefono))

    if not digitos:
        return ""

    # Formatear a estándar internacional (+57 para Colombia)
    if digitos.startswith('57') and len(digitos) >= 12:
        numero = digitos
    elif len(digitos) == 10:
        numero = f'57{digitos}'
    elif len(digitos) > 10 and not digitos.startswith('57'):
        numero = f'57{digitos}'
    else:
        numero = digitos

    url = f"https://wa.me/{numero}"
    if mensaje:
        mensaje_codificado = urllib.parse.quote(mensaje)
        url += f"?text={mensaje_codificado}"

    return url
