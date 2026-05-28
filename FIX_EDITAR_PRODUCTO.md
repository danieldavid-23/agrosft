# ✅ FIX: TemplateDoesNotExist + NoReverseMatch al editar producto

## 📅 Fecha: 27 de Mayo, 2026

---

## 🐛 PROBLEMAS IDENTIFICADOS

### **Error 1:** TemplateDoesNotExist
**Error:** `TemplateDoesNotExist at /inventario/producto/5/editar/`
**Template faltante:** `inventario/editar_producto.html`

### **Error 2:** NoReverseMatch
**Error:** `Reverse for 'detalle' with arguments '('',)' not found`
**Causa:** Template usaba `producto.id` (vacío) en lugar de `producto_usuario.id_producto_usuario`

**Causa raíz:**
1. El controller intentaba usar un template que no existe: `editar_producto.html`
2. Código obsoleto que aún convertía `cantidad` a string (ya es DecimalField)
3. Uso innecesario de `safe_int()` para campo que ahora es Decimal

---

## ✅ SOLUCIÓN APLICADA

### **1. Template Corregido**

**Archivo:** `apps/inventario/controllers/producto_controller.py`

**Antes:**
```python
return render(request, 'inventario/editar_producto.html', {
    'form': form,
    'producto_usuario': producto_usuario,
    'categorias': categorias,
    'estados': estados
})
```

**Después:**
```python
return render(request, 'inventario/producto_form.html', {
    'form': form,
    'producto_usuario': producto_usuario,
    'producto': producto_usuario.id_producto,  # El template usa producto.nombre
    'categorias': categorias,
    'estados': estados,
    'titulo': 'Editar Producto',
    'accion': 'editar'
})
```

**Beneficios:**
- ✅ Usa template existente `producto_form.html` que maneja crear y editar
- ✅ Pasa variable `producto` que el template necesita para mostrar el nombre
- ✅ Pasa variable `accion='editar'` para modo edición

---

### **2. URL Corregida en Template**

**Archivo:** `apps/inventario/templates/inventario/producto_form.html`

**Antes:**
```django
<a href="{% if producto %}{% url 'inventario:detalle' producto.id %}{% else %}...">
```

**Problema:**
- `producto.id` no existe (el modelo `Producto` usa `id_producto` como PK)
- Aún si existiera, la vista `producto_detail` espera `id_producto_usuario`, no `id_producto`

**Después:**
```django
<a href="{% if producto_usuario %}{% url 'inventario:detalle' producto_usuario.id_producto_usuario %}{% else %}...">
```

**Explicación:**
- `producto_usuario` siempre existe en el context (es el objeto que se está editando)
- `id_producto_usuario` es la primary key de `ProductoUsuario`
- La vista `producto_detail` espera exactamente este ID:
  ```python
  producto = get_object_or_404(ProductoUsuario, id_producto_usuario=pk)
  ```

---

### **2. Eliminada Conversión Obsoleta de cantidad**

#### **Función: `editar_producto()`**

**Antes:**
```python
producto_usuario.cantidad = str(form.cleaned_data['cantidad'])  # Convertir a string
# ...
'cantidad': safe_int(producto_usuario.cantidad),  # Convertir a int
```

**Después:**
```python
producto_usuario.cantidad = form.cleaned_data['cantidad']  # Decimal directo
# ...
'cantidad': producto_usuario.cantidad,  # Decimal, no necesita conversión
```

#### **Función: `crear_producto()`**

**Antes:**
```python
producto_usuario.cantidad = str(form.cleaned_data['cantidad'])  # Convertir a string
```

**Después:**
```python
producto_usuario.cantidad = form.cleaned_data['cantidad']  # Decimal directo
```

---

### **3. Reemplazado safe_int() por métodos del modelo**

#### **Función: `listar_productos()`**

**Antes:**
```python
'stock': safe_int(pu.cantidad),
'esta_agotado': safe_int(pu.cantidad) == 0,
```

**Después:**
```python
'stock': pu.obtener_stock(),  # Usa método helper del modelo
'esta_agotado': pu.cantidad == 0,  # Comparación directa con Decimal
```

#### **Función: `marketplace()`**

**Antes:**
```python
'stock': safe_int(pu.cantidad),
'esta_agotado': safe_int(pu.cantidad) == 0,
```

**Después:**
```python
'stock': pu.obtener_stock(),  # Usa método helper del modelo
'esta_agotado': pu.cantidad == 0,  # Comparación directa con Decimal
```

---

### **4. Importación Limpia**

**Antes:**
```python
from core.utils.helpers import safe_int, EstadoProducto
```

**Después:**
```python
from core.utils.helpers import EstadoProducto
```

---

## 📊 CAMBIOS REALIZADOS

| Archivo | Líneas Cambiadas | Tipo |
|---------|------------------|------|
| `producto_controller.py` | ~15 líneas | Corrección + Optimización |

### **Funciones Modificadas:**
1. ✅ `crear_producto()` - Eliminada conversión a string
2. ✅ `editar_producto()` - Template corregido + conversión eliminada
3. ✅ `listar_productos()` - safe_int reemplazado
4. ✅ `marketplace()` - safe_int reemplazado

---

## 🧪 VERIFICACIÓN

### **Probar funcionalidad:**

1. **Crear producto:**
   ```
   http://127.0.0.1:8000/inventario/producto/crear/
   ```
   - Debería funcionar sin errores
   - cantidad se guarda como Decimal

2. **Editar producto:**
   ```
   http://127.0.0.1:8000/inventario/producto/{id}/editar/
   ```
   - Debería mostrar formulario con datos actuales
   - Sin error TemplateDoesNotExist
   - Campos precargados correctamente

3. **Listar productos:**
   ```
   http://127.0.0.1:8000/inventario/
   ```
   - Stock se muestra correctamente
   - Sin errores de conversión

4. **Marketplace:**
   ```
   http://127.0.0.1:8000/inventario/marketplace/
   ```
   - Stock de otros usuarios visible
   - Sin errores de tipo

---

## 🎯 BENEFICIOS

### **Código más limpio:**
- ✅ Sin conversiones innecesarias de tipo
- ✅ Uso de métodos helper del modelo
- ✅ Template reutilizado (DRY principle)

### **Mejor performance:**
- ✅ Eliminadas conversiones VARCHAR ↔ DECIMAL
- ✅ Comparaciones directas con Decimal
- ✅ Menos overhead de funciones helper

### **Mantenibilidad:**
- ✅ Un template para crear y editar
- ✅ Lógica de formato en el modelo (OOP)
- ✅ Código alineado con esquema de BD

---

## 📝 NOTAS IMPORTANTES

### **Template producto_form.html:**

El template ya soporta ambos modos usando variable `accion`:

```django
{% if accion == 'crear' %}
    <h3>Registrar Nuevo Producto</h3>
{% else %}
    <h3>Editar: {{ producto.nombre }}</h3>
{% endif %}
```

### **Método obtener_stock():**

Definido en `ProductoUsuario` modelo:

```python
def obtener_stock(self):
    """Retorna el stock como entero para compatibilidad con templates"""
    return int(self.cantidad)
```

### **Comparación con Decimal:**

Ahora podemos comparar directamente:

```python
# ANTES (con VARCHAR):
esta_agotado = safe_int(pu.cantidad) == 0  # str → int → compare

# DESPUÉS (con DECIMAL):
esta_agotado = pu.cantidad == 0  # Decimal → compare (más rápido)
```

---

## ⚠️ POSIBLES PROBLEMAS Y SOLUCIONES

### **Problema 1: Error de tipo al guardar**

**Síntoma:**
```
TypeError: unsupported operand type(s) for ...
```

**Solución:**
Verificar que el formulario envía Decimal, no string:
```python
# En forms.py, el campo debe ser:
cantidad = forms.DecimalField(...)
```

### **Problema 2: Template muestra datos incorrectos**

**Síntoma:**
Datos no se muestran al editar

**Solución:**
Verificar que se pasa variable `producto`:
```python
'producto': producto_usuario.id_producto
```

### **Problema 3: Error de validación en formulario**

**Síntoma:**
```
ValidationError: ['Enter a number.']
```

**Solución:**
Verificar que `ProductoForm` usa DecimalField:
```python
cantidad = forms.DecimalField(
    max_digits=10,
    decimal_places=2,
    min_value=0
)
```

---

## ✅ CHECKLIST DE VERIFICACIÓN

- [x] Template corregido (usa producto_form.html)
- [x] Conversión a string eliminada en crear_producto
- [x] Conversión a string eliminada en editar_producto
- [x] safe_int reemplazado en listar_productos
- [x] safe_int reemplazado en marketplace
- [x] Importación de safe_int eliminada
- [x] Variable `producto` agregada al context
- [x] Variable `accion='editar'` agregada al context
- [x] Sin errores de sintaxis
- [ ] Probar crear producto (manual)
- [ ] Probar editar producto (manual)
- [ ] Probar listar productos (manual)
- [ ] Probar marketplace (manual)

---

## 🚀 PRÓXIMOS PASOS

1. **Probar en navegador:**
   - Crear producto nuevo
   - Editar producto existente
   - Verificar que stock se muestra correctamente

2. **Verificar formulario:**
   - Revisar `apps/inventario/forms/producto_form.py`
   - Confirmar que `cantidad` es `DecimalField`

3. **Actualizar otros controllers:**
   - Buscar más usos de `safe_int` para cantidad
   - Reemplazar con métodos del modelo

4. **Limpiar código obsoleto:**
   - Si `safe_int` no se usa en otro lado, considerar eliminarlo
   - Actualizar documentación

---

**✅ FIX COMPLETADO - Listo para probar!**

---

*Documento generado el 27 de Mayo, 2026 - Equipo AgroSFT*
