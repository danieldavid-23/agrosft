"""
Script de validación de esquema de base de datos
Verifica que los modelos Django coincidan con la estructura real de la BD MariaDB

Uso:
    python manage.py shell < scripts/validate_schema.py
"""

import sys
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from apps.inventario.models import Producto, ProductoUsuario, Categoria, Estado
from apps.ventas.models.movimiento import Movimiento, ProductoUsuarioMovimiento, TipoMovimiento
from apps.usuarios.models.profile_model import Tblusuarios


def get_table_columns(table_name):
    """Obtiene las columnas reales de una tabla en la BD"""
    with connection.cursor() as cursor:
        cursor.execute(f"DESCRIBE {table_name}")
        columns = {}
        for row in cursor.fetchall():
            columns[row[0]] = {
                'type': row[1],
                'null': row[2],
                'key': row[3],
                'default': row[4],
                'extra': row[5]
            }
        return columns


def get_model_fields(model):
    """Obtiene los campos definidos en un modelo Django"""
    fields = {}
    for field in model._meta.get_fields():
        if hasattr(field, 'db_column') and field.db_column:
            fields[field.db_column] = {
                'django_field': field.__class__.__name__,
                'max_length': getattr(field, 'max_length', None),
                'null': field.null,
                'blank': getattr(field, 'blank', None),
            }
        elif hasattr(field, 'name'):
            fields[field.name] = {
                'django_field': field.__class__.__name__,
                'max_length': getattr(field, 'max_length', None),
                'null': field.null,
                'blank': getattr(field, 'blank', None),
            }
    return fields


def validate_model(model, table_name):
    """Valida que un modelo coincida con la tabla de la BD"""
    print(f"\n{'='*80}")
    print(f"Validando modelo: {model.__name__} -> Tabla: {table_name}")
    print(f"{'='*80}")
    
    try:
        db_columns = get_table_columns(table_name)
        model_fields = get_model_fields(model)
        
        issues = []
        warnings = []
        
        # Verificar que todos los campos del modelo existan en la BD
        print(f"\n📋 Campos del modelo ({len(model_fields)}):")
        for field_name, field_info in model_fields.items():
            if field_name in db_columns:
                db_info = db_columns[field_name]
                status = "✅"
                
                # Verificar tipos
                db_type = db_info['type'].upper()
                django_type = field_info['django_field'].upper()
                
                # Validaciones de tipo
                if 'CHAR' in db_type and 'CHAR' not in django_type and 'TEXT' not in django_type:
                    warnings.append(f"⚠️  {field_name}: BD={db_type}, Django={django_type}")
                elif 'INT' in db_type and 'INTEGER' not in django_type and 'AUTO' not in django_type and 'FOREIGN' not in django_type:
                    warnings.append(f"⚠️  {field_name}: BD={db_type}, Django={django_type}")
                elif 'DECIMAL' in db_type and 'DECIMAL' not in django_type:
                    warnings.append(f"⚠️  {field_name}: BD={db_type}, Django={django_type}")
                
                print(f"  {status} {field_name:30s} BD: {db_info['type']:20s} Django: {field_info['django_field']}")
            else:
                # Campo del modelo no existe en BD
                issues.append(f"❌ {field_name} existe en el modelo pero NO en la BD")
                print(f"  ❌ {field_name:30s} [ERROR: No existe en BD]")
        
        # Verificar que todos los campos de la BD estén en el modelo
        print(f"\n📋 Campos de la BD ({len(db_columns)}):")
        for col_name, col_info in db_columns.items():
            if col_name not in model_fields:
                # Ignorar campos que Django maneja automáticamente
                if col_name not in ['id', 'password'] and not col_name.startswith('_'):
                    issues.append(f"❌ {col_name} existe en la BD pero NO en el modelo")
                    print(f"  ❌ {col_name:30s} [ERROR: No existe en modelo]")
            else:
                print(f"  ✅ {col_name:30s} OK")
        
        # Resumen
        print(f"\n{'='*80}")
        if issues:
            print(f"❌ ERRORES ENCONTRADOS: {len(issues)}")
            for issue in issues:
                print(f"  {issue}")
        elif warnings:
            print(f"⚠️  ADVERTENCIAS: {len(warnings)}")
            for warning in warnings:
                print(f"  {warning}")
            print("✅ Sin errores críticos")
        else:
            print("✅ PERFECTO: Modelo y BD están perfectamente alineados")
        
        print(f"{'='*80}")
        return len(issues) == 0
        
    except Exception as e:
        print(f"❌ ERROR al validar: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Validar todos los modelos principales"""
    print("\n" + "="*80)
    print("VALIDACIÓN DE ESQUEMA DE BASE DE DATOS AGROSFT")
    print("="*80)
    
    models_to_validate = [
        (Tblusuarios, 'tblusuarios'),
        (Categoria, 'tblcategoria'),
        (Producto, 'tblproducto'),
        (Estado, 'estado'),
        (TipoMovimiento, 'tipo_movimiento'),
        (ProductoUsuario, 'tblproductos_has_tblusuarios'),
        (Movimiento, 'movimiento'),
        (ProductoUsuarioMovimiento, 'tblproductos_has_tblusuarios_has_movimiento'),
    ]
    
    results = {}
    
    for model, table_name in models_to_validate:
        try:
            results[model.__name__] = validate_model(model, table_name)
        except Exception as e:
            print(f"\n❌ Error validando {model.__name__}: {str(e)}")
            results[model.__name__] = False
    
    # Resumen final
    print("\n" + "="*80)
    print("RESUMEN FINAL")
    print("="*80)
    
    for model_name, success in results.items():
        status = "✅ OK" if success else "❌ ERRORES"
        print(f"  {status:10s} {model_name}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\nTotal: {passed}/{total} modelos validados correctamente")
    
    if passed == total:
        print("\n🎉 ¡Todos los modelos están perfectamente alineados con la BD!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} modelo(s) tienen problemas que necesitan atención")
        return 1


if __name__ == '__main__':
    sys.exit(main())
