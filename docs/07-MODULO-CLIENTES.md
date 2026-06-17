# Módulo Clientes

> Historial de actividad de compradores y vendedores basado en movimientos.

**App**: `apps.clientes` | **Namespace**: `clientes` | **URL prefix**: `/clientes/`

---

## Estructura de Archivos

```
apps/clientes/
├── controllers/
│   └── cliente_controller.py   → Listar, detalle, historial de compras
├── models/
│   └── cliente.py              → Modelo Cliente (no usado directamente)
└── urls.py
```

---

## Descripción

Este módulo funciona como un **dashboard de historial** que muestra:
- Usuarios que han realizado movimientos (compras/ventas)
- Estadísticas de actividad por usuario
- Historial detallado de transacciones

> [!note] Fuente de datos
> NO usa la tabla `clientes` (modelo `Cliente`). Los datos provienen directamente de `Tblusuarios` + `Movimiento` + `ProductoUsuarioMovimiento`. Ver [[03-BASE-DATOS]].

---

## Vistas (Controllers)

### `listar_clientes`
Muestra usuarios con actividad en el sistema:

```python
# Query: usuarios que tienen al menos un movimiento
Tblusuarios.objects.filter(movimientos__isnull=False)
    .annotate(total_movimientos, total_compras, total_ventas)
```

Por cada usuario muestra:
- Nombre completo, correo, teléfono
- Total de movimientos, compras y ventas
- Flags: `es_vendedor`, `es_comprador`
- Ordenado por actividad (más activos primero)

### `detalle_cliente`
Historial detallado de un usuario específico:

- Últimos 20 movimientos con producto, cantidad, fecha
- Estadísticas: total compras vs. ventas
- Datos del perfil del usuario

### `historial_compras`
Historial exclusivo de **compras** de un usuario:

- Filtra por `tipo_movimiento.tipo = 'compra'`
- Ordena por fecha descendente
- Muestra producto, cantidad, precio y fecha

---

## Modelo Cliente (No Usado)

```python
class Cliente(models.Model):
    usuario = OneToOneField(Tblusuarios)
    nombre_completo = CharField(200)
    telefono = CharField(20)
    direccion = TextField()
    fecha_registro = DateTimeField()
```

> [!warning] Este modelo existe pero NO se usa
> Las vistas consultan directamente `Tblusuarios` con joins a `Movimiento`. La tabla `clientes` en BD podría no existir. El modelo tiene `managed` no definido (default True), lo que podría causar errores con `makemigrations`.

---

## Rutas

| URL | Name | Descripción |
|---|---|---|
| `/clientes/` | `clientes:cliente_list` | Listar usuarios activos |
| `/clientes/<pk>/` | `clientes:cliente_detail` | Detalle de usuario |
| `/clientes/<id>/historial-compras/` | `clientes:historial_compras` | Historial de compras |

---

## Enlaces Relacionados

- [[00-INDEX]] — Volver al índice
- [[03-BASE-DATOS#movimiento]] — Schema de movimientos
- [[06-MODULO-VENTAS]] — Módulo de ventas y transacciones
