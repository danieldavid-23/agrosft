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
