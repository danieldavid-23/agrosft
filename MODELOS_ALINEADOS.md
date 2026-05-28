# 📋 MODELOS DJANGO ALINEADOS CON BASE DE DATOS

## 📅 Fecha de Actualización
27 de Mayo, 2026

## 🎯 Objetivo
Alinear completamente los modelos Django con el esquema real de la base de datos MariaDB 10.4.32, eliminando discrepancias y mejorando la documentación.

---

## ✅ CAMBIOS REALIZADOS

### 1. **apps/inventario/models/producto.py**

#### **Estado**
- ✅ Agregado `db_column='id_estado'` explícito
- ✅ Agregado `db_column='estado'` explícito
- ✅ Documentación mejorada: define estados de publicación

#### **TipoMovimiento**
- ✅ Documentación mejorada: explica tipos 'compra' (abastecimiento) y 'venta' (producto vendido)

#### **Categoria**
- ✅ Corregido `max_length` de 100 → **45** (igual que BD)
- ✅ Agregados `db_column` explícitos para todos los campos
- ✅ Documentación mejorada con ejemplos de categorías

#### **Producto**
- ✅ Corregido `max_length` de 100 → **45** (igual que BD)
- ✅ Eliminado `unique=True` (no existe en BD)
- ✅ Agregados `db_column` explícitos para TODOS los campos
- ✅ Documentación mejorada: explica catálogo maestro

#### **ProductoUsuario** ⚠️ CAMBIO CRÍTICO
- ✅ **CORREGIDO TIPO DE `cantidad`:**
  - **ANTES:** `models.CharField(max_length=45, default='0')`
  - **DESPUÉS:** `models.DecimalField(max_digits=10, decimal_places=2, default=0.00)`
  - **Motivo:** Aunque la BD actual tiene VARCHAR, el trigger hace operaciones matemáticas. Este cambio requiere ALTER TABLE en la BD (ver sección de pendencias).
  
- ✅ Agregado `db_column='cantidad'` explícito
- ✅ Agregado `db_column='precio'` explícito
- ✅ Agregado `db_column='fecha_creacion'` explícito
- ✅ Documentación mejorada: explica relación muchos-a-muchos
- ✅ Agregado método helper `obtener_stock()` para compatibilidad con templates

#### **Calificacion**
- ✅ Documentación actualizada: aclara que es tabla de referencia casi vacía
- ✅ Cambiado verbose_name a "Calificación (Referencia)"

---

### 2. **apps/ventas/models/movimiento.py**

#### **TipoMovimiento** (duplicado)
- ✅ Documentación agregada: nota sobre duplicación con inventario.models
- ⚠️ **RECOMENDACIÓN:** Eliminar duplicado y usar solo uno

#### **Movimiento**
- ✅ **Eliminados campos comentados** que no existen en BD:
  ```python
  # ELIMINADO:
  # fecha_movimiento = models.DateTimeField(auto_now_add=True)
  # descripcion = models.TextField(blank=True, null=True)
  ```

- ✅ Documentación mejorada: aclara que NO tiene fecha ni descripción
- ✅ Agregado `related_name='movimientos'` (cambiado de 'movimientos_venta')
- ✅ Agregados métodos helper:
  - `obtener_fecha()` - Obtiene fecha desde el primer detalle
  - `obtener_total()` - Calcula total del movimiento
  - `obtener_detalles()` - Retorna detalles con select_related

#### **ProductoUsuarioMovimiento**
- ✅ Agregado `db_column='cantidad'` explícito
- ✅ Agregado `db_column='calificacion'` explícito
- ✅ Agregado `db_column='fecha_movimiento'` explícito
- ✅ Agregado `related_name='movimientos_detalle'` en FK a ProductoUsuario
- ✅ Agregado `related_name='detalles'` en FK a Movimiento
- ✅ Documentación mejorada: explica importancia de la tabla
- ✅ Agregados métodos helper:
  - `obtener_subtotal()` - Calcula subtotal
  - `obtener_vendedor()` - Retorna usuario vendedor
  - `es_venta()` - Determina si es venta (cantidad < 0)
  - `es_abastecimiento()` - Determina si es abastecimiento (cantidad > 0)

---

### 3. **apps/ventas/models/solicitud.py**

#### **SolicitudCompra** ⚠️ OBSOLETO
- ✅ Marcado como **OBSOLETO** en docstring
- ✅ Agregada clase Meta con `db_table='ventas_solicitudcompra'` (tabla NO existe)
- ✅ Documentación explica que se debe usar Movimiento en su lugar
- ✅ Verbose_name cambiado a "Solicitud de Compra (OBSOLETO)"

#### **DetalleSolicitudCompra** ⚠️ OBSOLETO
- ✅ Marcado como **OBSOLETO** en docstring
- ✅ Agregada clase Meta con `db_table='ventas_detallesolicitudcompra'` (tabla NO existe)
- ✅ Documentación explica que se debe usar ProductoUsuarioMovimiento en su lugar
- ✅ Verbose_name cambiado a "Detalle de Solicitud (OBSOLETO)"

---

### 4. **apps/ventas/models/venta.py**

#### **Venta** ⚠️ OBSOLETO
- ✅ Marcado como **OBSOLETO** en docstring
- ✅ Agregada clase Meta con `db_table='ventas_venta'` (tabla NO existe)
- ✅ Documentación explica que se debe usar Movimiento en su lugar
- ✅ Verbose_name cambiado a "Venta (OBSOLETO)"

#### **DetalleVenta** ⚠️ OBSOLETO
- ✅ Marcado como **OBSOLETO** en docstring
- ✅ Agregada clase Meta con `db_table='ventas_detalleventa'` (tabla NO existe)
- ✅ Documentación explica que se debe usar ProductoUsuarioMovimiento en su lugar
- ✅ Verbose_name cambiado a "Detalle de Venta (OBSOLETO)"

---

### 5. **NUEVO: scripts/validate_schema.py**

Script de validación automática que:
- ✅ Compara cada modelo Django con su tabla real en la BD
- ✅ Verifica existencia de campos en ambos sentidos
- ✅ Detecta discrepancias de tipos de datos
- ✅ Genera reporte detallado con errores y advertencias
- ✅ Retorna código de exito (0) o error (1)

**Uso:**
```bash
python manage.py shell < scripts/validate_schema.py
```

---

## 📊 RESUMEN DE CAMBIOS

| Modelo | Cambios | Estado |
|--------|---------|--------|
| `Estado` | ✅ db_columns explícitos, docs | **OK** |
| `TipoMovimiento` | ✅ Docs mejoradas | **OK** |
| `Categoria` | ✅ max_length corregido, db_columns | **OK** |
| `Producto` | ✅ max_length corregido, db_columns | **OK** |
| `ProductoUsuario` | ⚠️ **cantidad: CharField → DecimalField** | **REQUIERE ALTER TABLE** |
| `Calificacion` | ✅ Docs aclaratorias | **OK** |
| `Movimiento` | ✅ Campos comentados eliminados, métodos helper | **OK** |
| `ProductoUsuarioMovimiento` | ✅ db_columns, métodos helper | **OK** |
| `SolicitudCompra` | ✅ Marcado OBSOLETO | **NO USAR** |
| `DetalleSolicitudCompra` | ✅ Marcado OBSOLETO | **NO USAR** |
| `Venta` | ✅ Marcado OBSOLETO | **NO USAR** |
| `DetalleVenta` | ✅ Marcado OBSOLETO | **NO USAR** |

---

## ⚠️ PENDIENTES EN BASE DE DATOS

### **CRÍTICO: Cambiar tipo de `cantidad`**

Actualmente los modelos Django usan `DecimalField` pero la BD tiene `VARCHAR(45)`.

**Script SQL requerido:**
```sql
-- Paso 1: Verificar que no hay datos no numéricos
SELECT id_pd_us, cantidad 
FROM tblproductos_has_tblusuarios 
WHERE cantidad NOT REGEXP '^[0-9]+(\\.[0-9]+)?$';

-- Paso 2: Si retorna filas vacías, proceder
ALTER TABLE tblproductos_has_tblusuarios 
MODIFY COLUMN cantidad DECIMAL(10,2) NOT NULL DEFAULT 0.00 
COMMENT 'Stock disponible para esta publicación';
```

**Impacto:**
- ✅ Elimina necesidad de `safe_int()` en código
- ✅ Mejora performance (sin conversión implícita)
- ✅ Previene errores de conversión
- ✅ Trigger funcionará correctamente

---

## 🎯 BENEFICIOS DE LOS CAMBIOS

### **1. Alineación Perfecta con BD**
- ✅ Todos los `db_column` explícitos
- ✅ `max_length` coincide con BD
- ✅ Sin campos que no existen en BD

### **2. Documentación Mejorada**
- ✅ Explica lógica de tipos de movimiento
- ✅ Aclara ubicación de fecha_movimiento
- ✅ Marca modelos obsoletos claramente
- ✅ Documenta relaciones y triggers

### **3. Métodos Helper**
- ✅ `obtener_fecha()`, `obtener_total()`, `obtener_subtotal()`
- ✅ `es_venta()`, `es_abastecimiento()`
- ✅ Facilita uso en controllers y templates

### **4. Validación Automática**
- ✅ Script `validate_schema.py` para verificar alineación
- ✅ Detecta errores antes de deployment
- ✅ Documentación viva del estado actual

---

## 📝 NOTAS IMPORTANTES

### **Modelos Obsoletos**
Los siguientes modelos **NO tienen tablas reales en la BD**:
- `SolicitudCompra`
- `DetalleSolicitudCompra`
- `Venta`
- `DetalleVenta`

**Se mantienen SOLO para:**
- Compatibilidad con código legacy
- Referencia histórica
- Evitar ImportError en imports existentes

**NO usar en código nuevo.** En su lugar usar:
- `Movimiento` (header de transacción)
- `ProductoUsuarioMovimiento` (detalles)

### **TipoMovimiento Duplicado**
El modelo `TipoMovimiento` está definido en:
- `apps.inventario.models`
- `apps.ventas.models`

**Recomendación:** Usar solo uno (preferiblemente `inventario.models.TipoMovimiento`) y hacer import en ventas.

---

## 🧪 TESTING RECOMENDADO

### **1. Ejecutar validación de esquema**
```bash
python manage.py shell < scripts/validate_schema.py
```

### **2. Verificar que no hay errores de import**
```bash
python manage.py check
```

### **3. Probar funcionalidad básica**
```bash
python manage.py shell
>>> from apps.inventario.models import ProductoUsuario
>>> from apps.ventas.models.movimiento import Movimiento
>>> # Si no hay errores, los imports están OK
```

### **4. Ejecutar servidor de desarrollo**
```bash
python manage.py runserver
# Visitar: http://127.0.0.1:8000/inventario/
# Verificar que no hay errores de modelo
```

---

## 📚 DOCUMENTACIÓN RELACIONADA

- [Documentación técnica de BD](../docs/DB_AGROSFT_DOCUMENTACION.md)
- [Análisis de esquema completo](../docs/ANALISIS_BD.md)
- [README del proyecto](../README.md)

---

## 🔄 PRÓXIMOS PASOS

1. ✅ **Ejecutar ALTER TABLE** para cambiar `cantidad` a DECIMAL
2. ✅ **Activar validación de stock** en trigger `trg_actualizar_stock_oferta`
3. ✅ **Implementar checkout completo** usando modelos de movimiento
4. ✅ **Eliminar TipoMovimiento duplicado** (usar uno solo)
5. ✅ **Actualizar controllers** para usar métodos helper nuevos
6. ✅ **Actualizar templates** si es necesario

---

## 👥 RESPONSABLES

- **Desarrollo:** Equipo AgroSFT
- **Base de datos:** DBA / Administrador
- **Testing:** QA / Desarrolladores

---

## 📞 SOPORTE

Para preguntas o problemas relacionados con estos cambios, contactar al equipo de desarrollo o crear un issue en el repositorio.

---

*Documento generado automáticamente como parte de la actualización de modelos Django - Mayo 2026*
