"""
Script para asegurar que los tipos de movimiento básicos existan en la base de datos
Ejecutar: python manage.py shell < scripts/asegurar_tipos_movimiento.py
"""

from apps.inventario.models import TipoMovimiento

def asegurar_tipos_movimiento():
    """Crea los tipos de movimiento 'compra' y 'venta' si no existen"""
    
    tipos_requeridos = ['compra', 'venta']
    
    for tipo in tipos_requeridos:
        obj, created = TipoMovimiento.objects.get_or_create(
            tipo=tipo,
            defaults={'tipo': tipo}
        )
        if created:
            print(f'✓ Creado tipo de movimiento: {tipo}')
        else:
            print(f'✓ Tipo de movimiento ya existe: {tipo}')
    
    print('\nTipos de movimiento verificados correctamente.')
    
    # Mostrar todos los tipos existentes
    print('\nTipos de movimiento existentes:')
    for tm in TipoMovimiento.objects.all():
        print(f'  - ID: {tm.id_tipo_movimiento}, Tipo: {tm.tipo}')

if __name__ == '__main__':
    asegurar_tipos_movimiento()
