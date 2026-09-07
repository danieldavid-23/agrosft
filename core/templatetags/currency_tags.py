from django import template

register = template.Library()

@register.filter
def currency_cop(value):
    """
    Format a number as Colombian Peso (COP).
    Integer values will not show decimals.
    Decimal values will show 2 decimal places.
    Formats with dot for thousands and comma for decimals.
    """
    try:
        if value is None or value == '':
            return '$0'
        
        # Convert to float
        val = float(value)
        
        # Check if it's an integer
        if val.is_integer():
            formatted = f"{int(val):,}".replace(",", ".")
        else:
            # format with 2 decimals, then replace comma with dot for thousands, and dot with comma for decimals
            formatted = f"{val:,.2f}"
            formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
            
        return f"${formatted}"
    except (ValueError, TypeError):
        return value


@register.filter
def format_cantidad(value):
    """
    Formatea la cantidad para que números enteros no muestren decimales (ej. 1 en vez de 1,00).
    """
    try:
        if value is None or value == '':
            return '0'
        val = float(value)
        if val.is_integer():
            return f"{int(val):,}".replace(",", ".")
        return f"{val:g}".replace(".", ",")
    except (ValueError, TypeError):
        return value


@register.filter
def clean_producto_nombre(value):
    """
    Si la descripción incluye ' - nombre_vendedor', extrae únicamente el nombre del producto.
    """
    if not value:
        return ''
    val_str = str(value)
    if ' - ' in val_str:
        return val_str.split(' - ')[0].strip()
    return val_str

