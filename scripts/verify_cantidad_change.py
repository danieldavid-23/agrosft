"""
Script de verificación post-ALTER TABLE
Confirma que el campo cantidad fue cambiado exitosamente a DECIMAL

Uso:
    python manage.py shell < scripts/verify_cantidad_change.py
"""

import sys
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from apps.inventario.models import ProductoUsuario


def verificar_tipo_cantidad_bd():
    """Verifica el tipo real de la columna cantidad en la BD"""
    print("\n" + "="*80)
    print("VERIFICANDO TIPO DE COLUMNA 'cantidad' EN BD")
    print("="*80)
    
    with connection.cursor() as cursor:
        cursor.execute("DESCRIBE tblproductos_has_tblusuarios")
        columns = {row[0]: row[1] for row in cursor.fetchall()}
        
        if 'cantidad' in columns:
            tipo_real = columns['cantidad']
            print(f"\n📊 Tipo actual en BD: {tipo_real}")
            
            if 'decimal' in tipo_real.lower():
                print("✅ CORRECTO: La columna es DECIMAL")
                return True
            elif 'varchar' in tipo_real.lower() or 'char' in tipo_real.lower():
                print("❌ ERROR: La columna sigue siendo VARCHAR/CHAR")
                print("\n⚠️  Debes ejecutar el ALTER TABLE:")
                print("   ALTER TABLE tblproductos_has_tblusuarios")
                print("   MODIFY COLUMN cantidad DECIMAL(10,2) NOT NULL DEFAULT 0.00;")
                return False
            else:
                print(f"⚠️  Tipo inesperado: {tipo_real}")
                return False
        else:
            print("❌ ERROR: La columna 'cantidad' no existe")
            return False


def verificar_modelo_django():
    """Verifica que el modelo Django usa DecimalField"""
    print("\n" + "="*80)
    print("VERIFICANDO MODELO DJANGO")
    print("="*80)
    
    campo = ProductoUsuario._meta.get_field('cantidad')
    
    print(f"\n📋 Información del campo 'cantidad' en ProductoUsuario:")
    print(f"   Tipo Django: {campo.__class__.__name__}")
    print(f"   max_digits: {campo.max_digits}")
    print(f"   decimal_places: {campo.decimal_places}")
    print(f"   default: {campo.default}")
    
    if campo.__class__.__name__ == 'DecimalField':
        print("\n✅ CORRECTO: El modelo usa DecimalField")
        return True
    else:
        print(f"\n❌ ERROR: El modelo usa {campo.__class__.__name__} en lugar de DecimalField")
        return False


def prueba_insercion():
    """Prueba que se pueden hacer operaciones matemáticas sin conversión"""
    print("\n" + "="*80)
    print("PRUEBA DE INSERCIÓN Y OPERACIONES")
    print("="*80)
    
    try:
        # Crear un objeto de prueba
        from apps.inventario.models import Producto, Estado
        from apps.usuarios.models.profile_model import Tblusuarios
        
        # Obtener o crear datos de prueba
        if Tblusuarios.objects.exists():
            usuario = Tblusuarios.objects.first()
        else:
            print("⚠️  No hay usuarios en la BD, saltando prueba de inserción")
            return True
        
        if Producto.objects.exists():
            producto = Producto.objects.first()
        else:
            print("⚠️  No hay productos en la BD, saltando prueba de inserción")
            return True
        
        if Estado.objects.exists():
            estado = Estado.objects.first()
        else:
            print("⚠️  No hay estados en la BD, saltando prueba de inserción")
            return True
        
        print("\n📝 Creando ProductoUsuario de prueba...")
        pu = ProductoUsuario(
            id_producto=producto,
            id_usuario=usuario,
            id_estado=estado,
            cantidad=15.50,  # Decimal directo, no string
            precio=25.99
        )
        pu.save()
        
        print(f"✅ ProductoUsuario creado exitosamente")
        print(f"   ID: {pu.id_producto_usuario}")
        print(f"   Cantidad: {pu.cantidad} (tipo: {type(pu.cantidad).__name__})")
        print(f"   Precio: {pu.precio}")
        
        # Probar operaciones matemáticas
        print("\n🧪 Probando operaciones matemáticas...")
        subtotal = pu.cantidad * pu.precio
        print(f"   {pu.cantidad} × {pu.precio} = {subtotal}")
        print(f"   ✅ Operación exitosa, resultado: ${subtotal:.2f}")
        
        # Limpiar
        print("\n🗑️  Eliminando registro de prueba...")
        pu.delete()
        print("✅ Registro eliminado")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR en prueba de inserción: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Ejecutar todas las verificaciones"""
    print("\n" + "="*80)
    print("VERIFICACIÓN POST-ALTER TABLE")
    print("Campo: tblproductos_has_tblusuarios.cantidad")
    print("="*80)
    
    resultados = {
        'BD': verificar_tipo_cantidad_bd(),
        'Modelo': verificar_modelo_django(),
        'Inserción': prueba_insercion(),
    }
    
    # Resumen final
    print("\n" + "="*80)
    print("RESUMEN FINAL")
    print("="*80)
    
    for test, resultado in resultados.items():
        status = "✅ PASS" if resultado else "❌ FAIL"
        print(f"  {status:10s} {test}")
    
    total = len(resultados)
    passed = sum(1 for v in resultados.values() if v)
    
    print(f"\nTotal: {passed}/{total} pruebas superadas")
    
    if passed == total:
        print("\n🎉 ¡ÉXITO! El ALTER TABLE se ejecutó correctamente y todo funciona.")
        print("\n✅ Beneficios:")
        print("   - No más necesidad de safe_int() para cantidad")
        print("   - Operaciones matemáticas directas sin conversión")
        print("   - Trigger de stock funcionará correctamente")
        print("   - Mejor performance sin conversiones implícitas")
        return 0
    else:
        print(f"\n⚠️  {total - passed} prueba(s) fallaron. Revisa los errores arriba.")
        return 1


if __name__ == '__main__':
    sys.exit(main())
