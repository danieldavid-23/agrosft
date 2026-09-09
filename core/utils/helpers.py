"""
Core utility helpers for AgroSFT.
Provides safe type conversions, shared constants, and utility functions.
"""
import logging
import re
import urllib.parse
from io import BytesIO

from PIL import Image
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile

logger = logging.getLogger(__name__)

MAX_IMAGE_DIMENSION = 400

IMAGE_VERSION = '20260907'


def image_cache_bust(url):
    """
    Añade un parámetro de versión a la URL de una imagen para invalidar la
    caché del navegador cuando el archivo se re-codifica en el mismo path.
    """
    if not url:
        return url
    separador = '&' if '?' in url else '?'
    return f'{url}{separador}v={IMAGE_VERSION}'


def validate_image_size(value):
    """
    Validates that the uploaded image size is less than 5MB.
    """
    limit_mb = 5
    if value.size > limit_mb * 1024 * 1024:
        raise ValidationError(f'El tamaño máximo permitido es {limit_mb}MB.')


def resize_uploaded_image(file_obj, field_name='imagen', max_dimension=MAX_IMAGE_DIMENSION):
    """
    Redimensiona una imagen subida a un máximo de `max_dimension` píxeles en su
    lado mayor, manteniendo la relación de aspecto (Pillow thumbnail).

    Devuelve un `InMemoryUploadedFile` listo para asignar al campo `ImageField`,
    u `None` cuando la imagen ya cumple el límite o no puede procesarse (el
    guardado original se conserva y no se rompe la operación).

    Args:
        file_obj: Archivo de imagen subido (UploadedFile / File).
        field_name: Nombre del campo ImageField al que se asignará el resultado.
        max_dimension: Límite máximo del lado mayor en píxeles.

    Returns:
        InMemoryUploadedFile | None
    """
    try:
        file_obj.seek(0)
        img = Image.open(file_obj)
        img.load()
    except Exception:
        return None

    if img.width <= max_dimension and img.height <= max_dimension:
        return None

    img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)

    fmt = (img.format or 'JPEG').upper()
    if fmt not in ('JPEG', 'PNG', 'WEBP'):
        fmt = 'JPEG'

    buffer = BytesIO()
    save_kwargs = {'format': fmt}
    if fmt == 'JPEG':
        if img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')
        save_kwargs.update({'quality': 72, 'optimize': True, 'progressive': True})
    elif fmt == 'PNG':
        method = getattr(Image, 'MEDIANCUT', None)
        img = img.quantize(colors=256, method=method) if method else img.quantize(colors=256)
        save_kwargs.update({'optimize': True})
    else:  # WEBP
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGBA')
        save_kwargs.update({'quality': 72, 'method': 6})
    img.save(buffer, **save_kwargs)

    content_types = {'JPEG': 'image/jpeg', 'PNG': 'image/png', 'WEBP': 'image/webp'}
    name = getattr(file_obj, 'name', None) or f'upload.{fmt.lower()}'

    size = buffer.tell()
    buffer.seek(0)

    return InMemoryUploadedFile(
        buffer,
        field_name,
        name,
        content_types[fmt],
        size,
        charset=None,
    )



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


def formatear_errores_form(form):
    """
    Retorna una cadena legible con los errores de un formulario Django,
    sin HTML crudo, para mostrar en mensajes de usuario.
    """
    if not hasattr(form, 'errors'):
        return ''
    errores = form.errors.as_data()
    partes = []
    for campo, lista_errores in errores.items():
        etiqueta = campo.replace('_', ' ').capitalize()
        mensajes = '; '.join(str(e.message) for e in lista_errores)
        mensajes = mensajes.replace('Este campo es obligatorio.', 'Campo obligatorio.')
        partes.append(f'{etiqueta}: {mensajes}')
    return ' - '.join(partes)
