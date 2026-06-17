# API Endpoints — Referencia Completa

> Todas las rutas URL del sistema organizadas por módulo.

---

## Root

| URL | Name | Descripción |
|---|---|---|
| `/` | `home` | Redirige a `usuarios:login` |
| `/admin/` | — | Django Admin (habilitado) |
| `/oauth/` | `social:begin` | Rutas de Google OAuth2 |

---

## `/usuarios/` — Módulo Usuarios

| URL | Name | Auth | Métodos | Descripción |
|---|---|---|---|---|
| `login/` | `usuarios:login` | No | GET, POST | Formulario de inicio de sesión |
| `registro/` | `usuarios:registro` | No | GET, POST | Formulario de registro |
| `logout/` | `usuarios:logout` | No | GET, POST | Cerrar sesión |
| `perfil/` | `usuarios:perfil` | Sí | GET, POST | Ver/editar perfil + imagen |
| `cambiar-password/` | `usuarios:cambiar_password` | Sí | GET, POST | Cambiar contraseña |
| `terminos/` | `usuarios:terminos` | No | GET | Ver términos y condiciones |
| `aceptar-terminos/` | `usuarios:aceptar-terminos` | Sí | POST | Aceptar términos |
| `historial/` | `usuarios:historial` | Sí | GET | Historial de aceptación |
| `password-reset/` | `usuarios:password_reset` | No | GET, POST | Solicitar reset de contraseña |
| `password-reset/done/` | `usuarios:password_reset_done` | No | GET | Confirmación de envío |
| `password-reset-confirm/<uidb64>/<token>/` | `usuarios:password_reset_confirm` | No | GET, POST | Reset con token |
| `password-reset-complete/` | `usuarios:password_reset_complete` | No | GET | Reset completado |

---

## `/inventario/` — Módulo Inventario

| URL | Name | Auth | Métodos | Descripción |
|---|---|---|---|---|
| `/` | `inventario:listar` | Sí | GET | Mi Inventario (mis productos) |
| `marketplace/` | `inventario:marketplace` | Sí | GET | Marketplace (productos de otros) |
| `producto/<pk>/` | `inventario:detalle` | Sí | GET | Detalle de producto |
| `producto/nuevo/` | `inventario:crear` | Sí | GET, POST | Crear producto |
| `producto/<pk>/editar/` | `inventario:editar` | Sí | GET, POST | Editar producto |
| `producto/<pk>/eliminar/` | `inventario:eliminar` | Sí | GET, POST | Eliminar producto |
| `producto/<id>/aprobar/` | `inventario:aprobar` | Sí (staff) | POST | Aprobar producto |
| `producto/<id>/rechazar/` | `inventario:rechazar` | Sí (staff) | POST | Rechazar producto |
| `api/producto/<id>/stock/` | `inventario:api_stock` | No | GET | API: verificar stock |

### Respuestas AJAX

Las vistas `listar` y `marketplace` retornan JSON cuando reciben header `X-Requested-With: XMLHttpRequest`:

```json
{
  "products": [
    {
      "id": 1,
      "nombre": "Tomate",
      "descripcion": "Tomate cherry",
      "precio": 5000.0,
      "stock": 20,
      "stock_minimo": 5,
      "estado": "Aprobado",
      "categoria_nombre": "Frutas",
      "agricultor_id": 3,
      "agricultor_nombre": "Juan Pérez",
      "esta_agotado": false,
      "imagen": null,
      "es_mi_producto": false,
      "detailUrl": "/inventario/producto/1/"
    }
  ],
  "has_next": true,
  "has_prev": false,
  "page": 1
}
```

---

## `/ventas/` — Módulo Ventas

### Carrito

| URL | Name | Auth | Métodos | Descripción |
|---|---|---|---|---|
| `carrito/` | `ventas:carrito_detalle` | No | GET | Ver carrito |
| `carrito/agregar/<id>/` | `ventas:carrito_agregar` | No | GET, POST | Añadir producto |
| `carrito/actualizar/<id>/` | `ventas:carrito_actualizar` | No | POST | Cambiar cantidad |
| `carrito/eliminar/<id>/` | `ventas:carrito_eliminar` | No | POST | Remover producto |
| `carrito/checkout/` | `ventas:carrito_checkout` | Sí | POST | Crear solicitud de compra |
| `carrito/checkout-venta/` | `ventas:carrito_checkout_venta` | Sí | POST | Venta directa (deshabilitado) |

### Solicitudes de Compra

| URL | Name | Auth | Métodos | Descripción |
|---|---|---|---|---|
| `solicitudes/` | `ventas:solicitud_list` | Sí | GET | Inbox: solicitudes recibidas |
| `solicitudes/crear/` | `ventas:solicitud_create` | Sí | GET | Crear solicitud (redirect carrito) |
| `solicitudes/<pk>/` | `ventas:solicitud_detail` | Sí | GET | Detalle de solicitud |
| `solicitudes/<pk>/aceptar/` | `ventas:solicitud_aceptar` | Sí | POST | Aceptar solicitud |
| `solicitudes/<pk>/rechazar/` | `ventas:solicitud_rechazar` | Sí | POST | Rechazar solicitud |
| `solicitudes/<pk>/vendido/` | `ventas:solicitud_marcar_vendido` | Sí | POST | Marcar como vendida |
| `solicitudes/<pk>/detalle/<detalle_id>/<estado>/` | `ventas:solicitud_estado_detalle` | Sí | POST | Cambiar estado de detalle |

### Ventas

| URL | Name | Auth | Métodos | Descripción |
|---|---|---|---|---|
| `/` | `ventas:venta_list` | Sí | GET | Listar ventas del vendedor |
| `<pk>/` | `ventas:venta_detail` | Sí | GET | Detalle de venta |
| `crear/` | `ventas:venta_create` | Sí | GET | Crear venta (redirect solicitudes) |

### Calificaciones

| URL | Name | Auth | Métodos | Descripción |
|---|---|---|---|---|
| `calificaciones/calificar/<id>/` | `ventas:calificar_transaccion` | Sí | GET, POST | Calificar transacción |
| `calificaciones/historial/` | `ventas:historial_movimientos` | Sí | GET | Historial de movimientos |

---

## `/clientes/` — Módulo Clientes

| URL | Name | Auth | Métodos | Descripción |
|---|---|---|---|---|
| `/` | `clientes:cliente_list` | Sí | GET | Listar usuarios con actividad |
| `<pk>/` | `clientes:cliente_detail` | Sí | GET | Detalle de usuario |
| `<id>/historial-compras/` | `clientes:historial_compras` | Sí | GET | Historial de compras |

---

## Respuestas JSON Estándar

### Éxito
```json
{
  "success": true,
  "producto_id": 42,
  "message": "Producto añadido al carrito."
}
```

### Error
```json
{
  "success": false,
  "error": "Solo hay 5 unidades disponibles."
}
```

---

## Enlaces Relacionados

- [[00-INDEX]] — Volver al índice
- [[04-MODULO-USUARIOS#Rutas]] — Rutas de usuarios
- [[05-MODULO-INVENTARIO#Rutas]] — Rutas de inventario
- [[06-MODULO-VENTAS#Rutas]] — Rutas de ventas
