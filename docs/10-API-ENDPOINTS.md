# API Endpoints — Referencia Completa

> Todas las rutas URL del sistema organizadas por módulo.

---

## Root

| URL | Name | Descripción |
|---|---|---|
| `/` | `home` | Redirige según estado: staff/superusuario → `admin_usuarios_list`, autenticado → `marketplace`, invitado → `login` |
| `/admin/` | — | Django Admin (habilitado) |
| `/oauth/` | `social:begin` | Rutas de Google OAuth2 |

---

## `/usuarios/` — Módulo Usuarios

### Autenticación y perfil

| URL | Name | Auth | Métodos | Descripción |
|---|---|---|---|---|
| `login/` | `usuarios:login` | No | GET, POST | Formulario de inicio de sesión (redirige staff/superusuario → `admin_usuarios_list`, no-staff → `marketplace`, o `next`) |
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

### Panel de administración (staff / superusuario)

| URL | Name | Auth | Métodos | Descripción |
|---|---|---|---|---|
| `admin-usuarios/` | `usuarios:admin_usuarios_list` | Sí (staff) | GET | Listar usuarios |
| `admin-usuarios/crear/` | `usuarios:admin_usuario_crear` | Sí (staff) | GET, POST | Crear usuario |
| `admin-usuarios/editar/<pk>/` | `usuarios:admin_usuario_editar` | Sí (staff) | GET, POST | Editar usuario |
| `admin-usuarios/toggle-activo/<pk>/` | `usuarios:admin_usuario_toggle_activo` | Sí (staff) | POST | Activar/desactivar |
| `admin-estadisticas/` | `usuarios:admin_estadisticas` | Sí (staff) | GET | Estadísticas del sistema |
| `admin-moderacion/` | `usuarios:admin_moderacion` | Sí (staff) | GET | Productos pendientes |
| `admin-moderacion/aprobar/<pk>/` | `usuarios:admin_aprobar_producto` | Sí (staff) | POST | Aprobar producto |
| `admin-moderacion/rechazar/<pk>/` | `usuarios:admin_rechazar_producto` | Sí (staff) | POST | Rechazar producto |
| `admin-categorias/` | `usuarios:admin_categorias_list` | Sí (staff) | GET | Listar categorías |
| `admin-categorias/crear/` | `usuarios:admin_categoria_crear` | Sí (staff) | GET, POST | Crear categoría |
| `admin-categorias/editar/<pk>/` | `usuarios:admin_categoria_editar` | Sí (staff) | GET, POST | Editar categoría |
| `admin-categorias/toggle/<pk>/` | `usuarios:admin_categoria_toggle` | Sí (staff) | POST | Activar/desactivar categoría |
| `admin-reporte/usuarios/` | `usuarios:admin_reporte_usuarios_csv` | Sí (staff) | GET | Exportar CSV usuarios |
| `admin-reporte/productos/` | `usuarios:admin_reporte_productos_csv` | Sí (staff) | GET | Exportar CSV productos |
| `admin-reporte/ventas/` | `usuarios:admin_reporte_ventas_csv` | Sí (staff) | GET | Exportar CSV ventas |

---

## `/inventario/` — Módulo Inventario

| URL | Name | Auth | Métodos | Descripción |
|---|---|---|---|---|
| `/` | `inventario:listar` | Sí | GET | Mi Inventario (mis productos) |
| `marketplace/` | `inventario:marketplace` | Sí | GET | Marketplace (productos de otros) |
| `producto/<pk>/` | `inventario:detalle` | Sí | GET | Detalle de producto |
| `producto/nuevo/` | `inventario:crear` | Sí | GET, POST | Crear producto |
| `venta-directa/` | `inventario:venta_directa` | Sí | GET | Venta directa (carrito rápido) |
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
      "imagenes": [],
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
| `carrito/` | `ventas:carrito_detalle` | Sí | GET | Ver carrito |
| `carrito/agregar/<id>/` | `ventas:carrito_agregar` | Sí | GET, POST | Añadir producto |
| `carrito/actualizar/<id>/` | `ventas:carrito_actualizar` | Sí | POST | Cambiar cantidad |
| `carrito/eliminar/<id>/` | `ventas:carrito_eliminar` | Sí | POST | Remover producto |
| `carrito/checkout/` | `ventas:carrito_checkout` | Sí | POST | Crear solicitud de compra |
| `carrito/checkout-venta/` | `ventas:carrito_checkout_venta` | Sí | POST | Venta directa (deshabilitado) |

> [!note] Auth en el carrito
> Todas las vistas del carrito requieren `@login_required` desde ADR-015 (2026-09-07).

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
| `<pk>/marcar-vendida/` | `ventas:venta_marcar_vendida` | Sí | POST | Marcar venta como vendida |
| `<pk>/cancelar/` | `ventas:venta_cancelar` | Sí | POST | Cancelar venta en proceso |

### Compras (vista del comprador)

| URL | Name | Auth | Métodos | Descripción |
|---|---|---|---|---|
| `compras/` | `ventas:compra_list` | Sí | GET | Listar mis compras |
| `compras/<pk>/` | `ventas:compra_detail` | Sí | GET | Detalle de compra |

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

## `/facturacion/` — Módulo Facturación

| URL | Name | Auth | Métodos | Descripción |
|---|---|---|---|---|
| `crear/` | `facturacion:crear_factura` | Sí | POST | Crear factura desde el carrito |
| `detalle/<id>/` | `facturacion:detalle_factura` | Sí | GET | Detalle de factura |
| `historial/` | `facturacion:historial_facturas` | Sí | GET | Historial de facturas |
| `pdf/<id>/` | `facturacion:generar_pdf` | Sí | GET | Generar PDF (`?descargar=1` → attachment) |
| `generar_pedido/<movimiento_id>/` | `facturacion:generar_factura_pedido` | Sí | GET | Factura desde movimiento → PDF |

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
- [[DATABASE#2.12]], [[DATABASE#2.13]] — Tablas `factura` e `item_factura`
