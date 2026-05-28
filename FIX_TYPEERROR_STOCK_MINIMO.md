# ✅ FIX: TypeError + Permiso de Stock Mínimo

## 📅 Fecha: 27 de Mayo, 2026

---

## 🐛 PROBLEMAS

### **1. TypeError al guardar**
```
TypeError: BaseForm.__init__() got an unexpected keyword argument 'instance'
```

**Causa:** 
- `ProductoForm` hereda de `forms.Form` (NO es `ModelForm`)
- El controller pasaba `instance=producto_usuario` que no es válido para `forms.Form`

### **2. Restricción de administrador innecesaria**
- Solo admins podían editar `stock_minimo`
- **Requerimiento:** TODOS los usuarios deben poder editar su alerta de stock mínimo

---

## ✅ SOLUCIONES

### **1. Eliminar parámetro `instance=`**

**Archivo:** `apps/inventario/controllers/producto_controller.py`

**Antes:**
```python
form = ProductoForm(request.POST, instance=producto_usuario)
```

**Después:**
```python
form = ProductoForm(request.POST)  # forms.Form no acepta instance=
```

**Explicación:**
- `forms.Form` es un formulario manual (NO vinculado a un modelo)
- Solo `ModelForm` acepta el parámetro `instance`
- Los datos se actualizan manualmente en el controller

---

### **2. Qitar restricción de admin para stock_minimo**

**Archivo:** `apps/inventario/controllers/producto_controller.py`

#### **En POST (guardado):**

**Antes:**
```python
# Solo administradores pueden editar stock_minimo
if request.user.is_staff or request.user.is_superuser:
    stock_minimo_value = form.cleaned_data.get('stock_minimo')
    if stock_minimo_value is not None:
        producto.stock_minimo = stock_minimo_value
```

**Después:**
```python
# TODOS los usuarios pueden editar stock_minimo
stock_minimo_value = form.cleaned_data.get('stock_minimo')
if stock_minimo_value is not None:
    producto.stock_minimo = stock_minimo_value
```

#### **En GET (inicialización):**

**Antes:**
```python
# Solo administradores pueden editar stock_minimo
if not request.user.is_staff and not request.user.is_superuser:
    form.fields['stock_minimo'].widget.attrs['readonly'] = True
    form.fields['stock_minimo'].widget.attrs['disabled'] = True
    form.fields['stock_minimo'].help_text = 'Solo administradores pueden modificar este campo'
```

**Después:**
```python
# TODOS los usuarios pueden editar stock_minimo (sin restricciones)
# No se agrega código de restricción
```

---

## 📊 TABLA DE PERMISOS ACTUALIZADA

### **Todos los usuarios (incluyendo no-admins):**

| Campo | Puede Editar |
|-------|--------------|
| nombre | ✅ Sí |
| descripcion | ✅ Sí |
| id_categoria | ✅ Sí |
| **stock_minimo** | ✅ **Sí** (CAMBIO) |
| cantidad | ✅ Sí |
| precio | ✅ Sí |
| id_estado | ❌ No (solo admin) |

---

## 🧪 VERIFICACIÓN

### **Probar guardado:**

1. **Editar producto:**
   ```
   http://127.0.0.1:8000/inventario/producto/5/editar/
   ```

2. **Modificar campos:**
   - Cambiar unidades (ej: 10 → 25)
   - Cambiar alerta stock mínimo (ej: 5 → 15)
   - Click en "Guardar Cambios"

3. **Resultado esperado:**
   - ✅ Sin error TypeError
   - ✅ Guarda correctamente
   - ✅ Mensaje: "¡Producto actualizado exitosamente!"
   - ✅ Redirige a lista de inventario

### **Probar como usuario normal:**

- ✅ Campo "Alerta Stock" debe estar **habilitado** (no gris)
- ✅ Puedes cambiar el valor
- ✅ Se guarda correctamente

---

## 📝 NOTAS TÉCNICAS

### **Diferencia entre forms.Form y ModelForm:**

| Característica | `forms.Form` | `ModelForm` |
|----------------|--------------|-------------|
| Vinculado a modelo | ❌ No | ✅ Sí |
| Parámetro `instance` | ❌ No acepta | ✅ Sí acepta |
| Guarda automático | ❌ Manual | ✅ Con `.save()` |
| Campos automáticos | ❌ Definir todos | ✅ Del modelo |
| Validación automática | ❌ Manual | ✅ Del modelo |

### **Por qué usamos forms.Form:**

1. **Dos modelos diferentes:**
   - `Producto` (catálogo maestro)
   - `ProductoUsuario` (publicación del usuario)

2. **Control manual necesario:**
   - Actualizar ambos modelos en transacción
   - Permisos diferentes por campo
   - Lógica de negocio personalizada

3. **Campos combinados:**
   - Algunos de `Producto` (nombre, stock_minimo)
   - Algunos de `ProductoUsuario` (cantidad, precio)

---

## ✅ CHECKLIST

- [x] Eliminado parámetro `instance=` del formulario
- [x] Quitada restricción de admin para stock_minimo en POST
- [x] Quitada restricción de admin para stock_minimo en GET
- [x] Verificado que formulario no tiene otros problemas
- [ ] Probar guardado sin errores
- [ ] Probar edición de stock_minimo como usuario normal
- [ ] Verificar que ambos campos se guardan correctamente

---

## 🚀 BENEFICIOS

### **Para Usuarios:**
- ✅ Pueden configurar su propia alerta de stock mínimo
- ✅ Control total sobre sus publicaciones
- ✅ Sin errores al guardar cambios

### **Para el Sistema:**
- ✅ Código más simple (sin verificaciones de admin para stock_minimo)
- ✅ Mejor experiencia de usuario
- ✅ Sin errores TypeError

---

**✅ FIX COMPLETADO - Listo para probar!**

---

*Documento generado el 27 de Mayo, 2026 - Equipo AgroSFT*
