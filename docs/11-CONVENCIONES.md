# Convenciones de Desarrollo

> Estándares de código, nomenclatura y prácticas que todo desarrollador debe seguir.

---

## Idioma

| Contexto | Idioma |
|---|---|
| **Comentarios en código** | Inglés |
| **Documentación (docs/)** | Español |
| **Mensajes de commit** | Español |
| **Nombres de variables/funciones** | Español (por convención del equipo) |
| **Labels de UI** | Español |

---

## Nomenclatura

### Python / Django

| Elemento | Convención | Ejemplo |
|---|---|---|
| Clases | PascalCase | `Tblusuarios`, `ProductoUsuario` |
| Funciones | snake_case | `listar_productos`, `get_categorias_cached` |
| Variables | snake_case | `productos_transformados`, `cache_key` |
| Constantes | UPPER_SNAKE | `PENDIENTE`, `APROBADO` |
| Módulos | snake_case | `producto_controller.py`, `carrito_service.py` |
| Templates | snake_case.html | `listar_productos.html`, `marketplace.html` |

### Base de Datos

| Elemento | Convención | Ejemplo |
|---|---|---|
| Tablas | minúsculas / tbl prefix | `tblproducto`, `tblusuarios`, `estado` |
| Columnas | minúsculas con underscores | `id_productos`, `fecha_creacion` |
| Primary Keys | `id_` + nombre tabla | `id_users`, `id_producto`, `id_pd_us` |
| Foreign Keys | tabla + `_id_` + columna | `tblcategoria_idt_categoria` |

### JavaScript / Vue

| Elemento | Convención | Ejemplo |
|---|---|---|
| Componentes | PascalCase.vue | `MarketApp.vue`, `CarritoApp.vue` |
| Variables | camelCase | `cartItems`, `selectedCategory` |
| Funciones | camelCase | `fetchProducts`, `agregarCarrito` |
| Props | camelCase | `initialProducts`, `urls` |

---

## Estructura de Apps Django

Cada app sigue esta organización:

```
apps/<nombre_app>/
├── controllers/     → Vistas Django (funciones o clases)
├── forms/           → Formularios de validación
├── models/          → Modelos ORM (managed = False)
├── repositories/    → Queries complejas encapsuladas
├── services/        → Lógica de negocio reutilizable
├── templates/       → Templates específicos de la app
├── tests/           → Tests unitarios
├── views/           → Vistas genéricas Django (opcional)
├── urls.py          → Rutas del módulo
├── admin.py         → Configuración Django Admin
└── apps.py          → AppConfig
```

---

## Modelos Django

### Reglas obligatorias

1. **`managed = False`** en TODOS los modelos → Django no gestiona el schema
2. **`db_column`** explícito en cada campo → Debe coincidir con BD real
3. **`db_table`** explícito → Nombre exacto de la tabla en BD
4. **PK personalizada** → Usar `AutoField(primary_key=True)` con el nombre real de la columna

### Ejemplo correcto

```python
class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True, db_column='id_productos')
    nombre = models.CharField(max_length=45, db_column='nombre')
    id_categoria = models.ForeignKey(Categoria, db_column='tblcategoria_idt_categoria')
    
    class Meta:
        db_table = 'tblproducto'
        managed = False
```

### Restricciones

- **NUNCA** ejecutar `makemigrations` ni `migrate` para apps propias
- **NUNCA** cambiar nombres de columnas en BD sin actualizar el modelo
- **Sincronizar** modelo ↔ BD manualmente después de cambios en BD

---

## Controllers (Vistas)

### Convenciones

- Usar `@login_required` para vistas que requieren autenticación
- Verificar propiedad de recursos: `if obj.id_usuario != request.user`
- Soportar respuesta dual: HTML (normal) y JSON (AJAX con `X-Requested-With`)
- Usar `messages` de Django para notificaciones al usuario
- Loggear acciones importantes con `logger.info()` / `logger.warning()`

### Patrón de respuesta dual

```python
@login_required
def mi_vista(request, pk):
    # ... lógica ...
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'data': ...})
    messages.success(request, 'Operación exitosa.')
    return redirect('modulo:listar')
```

---

## Frontend (Vue 3)

### Convenciones

- Un componente `.vue` por funcionalidad principal
- Props reciben datos iniciales desde Django (JSON serializado)
- `fetch()` para acciones interactivas (siempre con CSRF token)
- Formato de moneda: `Intl.NumberFormat('es-CO', { style: 'currency', currency: 'COP' })`
- Iconos: Font Awesome 6 (`<i class="fas fa-...">`)

### Estructura de componente

```vue
<script setup>
import { ref } from 'vue'
import { getCSRFToken } from '../shared/csrf.js'

const props = defineProps({ /* ... */ })
const data = ref(props.initialData)

async function action(item) {
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCSRFToken(),
      'X-Requested-With': 'XMLHttpRequest',
    },
  })
  const result = await res.json()
  if (result.success) { /* update local state */ }
}
</script>
```

---

## Seguridad

| Práctica | Implementación |
|---|---|
| CSRF | Siempre incluir `getCSRFToken()` en fetch POST |
| Contraseñas | Usar `make_password()` / `check_password()` de Django |
| SQL Injection | **Nunca** usar f-strings en `cursor.execute()` |
| Permisos | Verificar `request.user.is_staff` para acciones admin |
| Propiedad | Verificar `obj.id_usuario == request.user` antes de editar/eliminar |
| Inputs | Validar con Forms de Django antes de procesar |

> [!danger] Anti-patrón: SQL con f-strings
> ```python
> # ❌ MAL — Vulnerable a SQL injection
> cursor.execute(f"SELECT 1 FROM {table_name}")
> 
> # ✅ BIEN — Usar parámetros
> cursor.execute("SELECT 1 FROM %s", [table_name])
> ```

---

## Git

### Commits
- Formato: `tipo: descripción breve`
- Tipos: `feat`, `fix`, `refactor`, `docs`, `style`, `test`
- Idioma: Español
- Ejemplo: `feat: agregar módulo de solicitudes en JS puro`

### Ramas
- `main` — Producción
- `dev` — Desarrollo
- `feature/<nombre>` — Nuevas funcionalidades
- `fix/<nombre>` — Correcciones

---

## Enlaces Relacionados

- [[00-INDEX]] — Volver al índice
- [[02-ARQUITECTURA]] — Arquitectura del sistema
- [[09-CONFIGURACION]] — Configuración del entorno
