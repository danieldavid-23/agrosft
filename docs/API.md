# API.md — AgroSFT

> Contratos de endpoints: rutas, métodos, payloads y respuestas.  
> **Framework**: Django 6.0.2 | **Formato**: HTML + JSON (AJAX)

---

## Convenciones

- Las respuestas AJAX usan `JsonResponse` con header `X-Requested-With: XMLHttpRequest`
- Formularios estándar envían `application/x-www-form-urlencoded` con CSRF token
- Los endpoints de subida de archivos (`imagen`, `imagen_perfil`) requieren `Content-Type: multipart/form-data`
- Todas las rutas protegidas requieren `@login_required` (excepto auth y los endpoints de verificación de stock/recuperación). Desde ADR-015, **todas las vistas del carrito requieren autenticación**.
- Formato de fechas: `YYYY-MM-DD HH:MM` | Zona horaria: `America/Bogota`

---

## 1. Usuarios (`/usuarios/`)

### 1.1 Registro

```
GET  /usuarios/registro/
POST /usuarios/registro/
```

**Request Body (POST)**:

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `nombres` | string | Sí | Nombres del usuario |
| `apellidos` | string | Sí | Apellidos del usuario |
| `correo` | string | Sí | Email único |
| `telefono` | string | Sí | Teléfono de contacto |
| `password1` | string | Sí | Contraseña (min 8 chars) |
| `password2` | string | Sí | Confirmación de contraseña |

**Response (POST success)**: `Redirect → /usuarios/login/`

---

### 1.2 Login

```
GET  /usuarios/login/
POST /usuarios/login/
```

**Request Body (POST)**:

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `username` | string | Sí | Correo electrónico |
| `password` | string | Sí | Contraseña |

**Response (POST success)**: `Redirect → /usuarios/admin-usuarios/` (staff), `→ /inventario/marketplace/` (no-staff) o `?next=` param

---

### 1.3 Logout

```
GET  /usuarios/logout/
POST /usuarios/logout/
```

**Response**: `Redirect → /usuarios/login/`

---

### 1.4 Perfil

```
GET  /usuarios/perfil/
POST /usuarios/perfil/
```

**Request Body (POST)**:

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `nombres` | string | Sí | Nombres |
| `apellidos` | string | Sí | Apellidos |
| `telefono` | string | No | Teléfono |
| `imagen_perfil` | file | No | Imagen JPG/JPEG/PNG/WEBP (máx. 5MB) |
| `remove_photo` | string | No | `'true'` para eliminar foto |

**Response (AJAX)**:
```json
{"success": true}
```

---

### 1.5 Cambiar Contraseña

```
GET  /usuarios/cambiar-password/
POST /usuarios/cambiar-password/
```

**Request Body (POST)**:

| Campo | Tipo | Requerido |
|---|---|---|
| `current_password` | string | Sí |
| `new_password` | string | Sí |
| `confirm_password` | string | Sí |

### 1.6 Recuperación de Contraseña

```
GET  /usuarios/password-reset/
POST /usuarios/password-reset/                 → Solicitar enlace (Brevo email)
GET  /usuarios/password-reset/done/            → Confirmación de envío
GET  /usuarios/password-reset-confirm/<uidb64>/<token>/
POST /usuarios/password-reset-confirm/<uidb64>/<token>/
GET  /usuarios/password-reset-complete/
```

**Request Body (POST `password-reset/`)**:

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `correo` | string | Sí | Correo del usuario a recuperar |

**Request Body (POST `password-reset-confirm/.../`)**:

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `password1` | string | Sí | Nueva contraseña (min 8 caracteres) |
| `password2` | string | Sí | Confirmación de la contraseña |

**Implementación**: `apps/usuarios/controllers/auth_controller.py` → `UserPasswordResetView`, `UserPasswordResetConfirmView`; envío vía `apps/usuarios/services/email_service.py` (Brevo REST API). Tokens personalizados en `apps/usuarios/utils/password_reset_tokens.py`.

---

## 2. Inventario (`/inventario/`)

### 2.1 Mi Inventario

```
GET /inventario/
```

**Query Params**:

| Param | Tipo | Descripción |
|---|---|---|
| `q` | string | Búsqueda por nombre |
| `categoria` | int | Filtrar por ID de categoría |
| `orden` | string | `reciente` \| `precio_asc` \| `precio_desc` \| `nombre` |
| `page` | int | Número de página |

**Response (AJAX)**:
```json
{
  "products": [
    {
      "id": 1,
      "nombre": "Tomate Cherry",
      "precio": 8000.0,
      "stock": 50,
      "estado": "Aprobado",
      "imagen": "/media/productos/tomate_cherry.jpg",
      "imagenes": [
        "/media/productos/tomate_cherry.jpg",
        "/media/productos/tomate_cherry_2.jpg"
      ],
      "editUrl": "/inventario/producto/1/editar/",
      "deleteUrl": "/inventario/producto/1/eliminar/"
    }
  ],
  "has_next": true,
  "has_prev": false,
  "page": 1
}
```

---

### 2.2 Marketplace

```
GET /inventario/marketplace/
```

**Query Params**: Igual que Mi Inventario.

**Response (AJAX)**:
```json
{
  "products": [
    {
      "id": 5,
      "nombre": "Papa Pastusa",
      "precio": 3000.0,
      "stock": 100,
      "imagen": "/media/productos/papa_pastusa.jpg",
      "imagenes": [
        "/media/productos/papa_pastusa.jpg"
      ],
      "agricultor_nombre": "Juan Pérez",
      "detailUrl": "/inventario/producto/5/"
    }
  ],
  "has_next": true,
  "has_prev": false,
  "page": 1
}
```

---

### 2.3 Venta Directa

```
GET /inventario/venta-directa/
```

**Descripción**: Ruta de venta directa (carrito de compra rápida). Requiere autenticación.

---

### 2.4 Crear Producto

```
GET  /inventario/producto/nuevo/
POST /inventario/producto/nuevo/
```

**Request Body (POST, `multipart/form-data`)**:

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `nombre` | string | Sí | Nombre del producto |
| `descripcion` | string | No | Descripción |
| `imagen` | file (múltiple) | No | Fotografías JPG/JPEG/PNG/WEBP (máx. 5MB c/u). La primera se guarda como portada en `tblproducto.imagen`; las siguientes como registros de `tblproducto_imagenes` |
| `id_categoria` | int | Sí | ID de categoría |
| `precio` | decimal | Sí | Precio unitario |
| `cantidad` | int | Sí | Stock inicial |
| `stock_minimo` | int | No | Umbral mínimo (default: 5) |

**Response**: `Redirect → /inventario/`

---

### 2.5 Editar Producto

```
GET  /inventario/producto/<pk>/editar/
POST /inventario/producto/<pk>/editar/
```

**Request Body**: Igual que Crear Producto (`multipart/form-data`). El campo `imagen` acepta múltiples archivos: si se envía una nueva primera imagen, reemplaza la portada; los archivos adicionales se agregan a la galería de `tblproducto_imagenes`; si no se envía, se conserva la galería existente.

---

### 2.6 Eliminar Producto

```
POST /inventario/producto/<pk>/eliminar/
```

**Response (AJAX)**:
```json
{"success": true, "producto_id": 1}
```

---

### 2.7 Aprobar/Rechazar Producto (Admin)

```
POST /inventario/producto/<id>/aprobar/
POST /inventario/producto/<id>/rechazar/
```

**Requiere**: `request.user.is_staff == True` o `request.user.is_superuser == True`

---

### 2.8 API Verificar Stock

```
GET /inventario/api/producto/<producto_id>/stock/
```

**Response**:
```json
{
  "producto_id": 1,
  "nombre": "Tomate Cherry",
  "stock": 50,
  "disponible": true,
  "stock_minimo": 5,
  "agotado": false
}
```

---

## 3. Ventas (`/ventas/`)

### 3.1 Carrito

```
GET  /ventas/carrito/                              → Ver carrito
POST /ventas/carrito/agregar/<producto_id>/        → Agregar al carrito
POST /ventas/carrito/actualizar/<producto_id>/     → Cambiar cantidad
POST /ventas/carrito/eliminar/<producto_id>/       → Eliminar item
POST /ventas/carrito/checkout/                     → Crear solicitud
POST /ventas/carrito/checkout-venta/               → (Deshabilitado)
```

**Agregar al carrito — Request**:

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `cantidad` | int | No | Cantidad (default: 1) |

**Response (AJAX success)**:
```json
{"success": true, "producto_id": 5, "nombre": "Tomate Cherry"}
```

**Response (AJAX error)**:
```json
{"success": false, "error": "Solo hay 3 unidades disponibles de Tomate Cherry."}
```

---

### 3.2 Solicitudes

```
GET  /ventas/solicitudes/                          → Inbox del vendedor
GET  /ventas/solicitudes/<pk>/                     → Detalle de solicitud
POST /ventas/solicitudes/<pk>/aceptar/             → Aceptar solicitud
POST /ventas/solicitudes/<pk>/rechazar/            → Rechazar solicitud
POST /ventas/solicitudes/<pk>/vendido/             → Marcar como vendida
```

**Aceptar — Response (AJAX)**:
```json
{
  "success": true,
  "message": "¡Solicitud #5 aceptada y transferida al módulo de ventas con estado 'en proceso'!",
  "estado": "aceptada",
  "whatsapp_link": "https://wa.me/573154840318?text=%C2%A1Hola%20Samuel!%20He%20aceptado%20tu%20solicitud..."
}
```

**Rechazar — Response (AJAX)**:
```json
{"success": true, "message": "¡Solicitud #5 rechazada!", "estado": "rechazada"}
```

> **Nota**: Al aceptar, se genera un enlace `wa.me` con mensaje predefinido para contactar al comprador. Para requests no-AJAX, se almacena en sesión y se muestra un modal en la página de detalle.

---

### 3.3 Ventas

```
GET  /ventas/                                       → Listar ventas
GET  /ventas/<pk>/                                  → Detalle de venta
POST /ventas/<pk>/marcar-vendida/                   → Marcar venta como vendida
POST /ventas/<pk>/cancelar/                         → Cancelar venta en proceso
GET  /ventas/crear/                                 → Redirect a solicitudes
```

**Marcar como vendida — Response**:
- Success: `Redirect → /ventas/<pk>/` + mensaje de confirmación
- Error: `Redirect → /ventas/` + mensaje de error

> **Nota**: Solo disponible para ventas con estado "En proceso" (tipo_movimiento = 'venta'). Requiere POST con CSRF token.

**Cancelar venta — Response**:
- Success: `Redirect → /ventas/<pk>/` + mensaje de confirmación
- Error: `Redirect → /ventas/` + mensaje de error

> **Nota**: Cambia tipo_movimiento a 'cancelada'. No afecta stock. Solo disponible para ventas "En proceso".

---

### 3.4 Mis Compras (vista del comprador)

```
GET  /ventas/compras/                               → Listar mis compras
GET  /ventas/compras/<pk>/                          → Detalle de compra
```

**Listar compras — Context**:

| Variable | Tipo | Descripcion |
|---|---|---|
| `compras[].id` | int | ID del movimiento |
| `compras[].fecha` | datetime | Fecha del pedido |
| `compras[].total_productos` | int | Cantidad de productos |
| `compras[].total` | float | Total estimado |
| `compras[].estado` | string | Pendiente / En proceso / Finalizada |

**Detalle de compra — Context**:

| Variable | Tipo | Descripcion |
|---|---|---|
| `compra.id` | int | ID del movimiento |
| `compra.fecha` | datetime | Fecha del pedido |
| `compra.estado` | string | Pendiente / En proceso / Finalizada |
| `compra.total` | float | Total del pedido |
| `productos[]` | QuerySet | Detalles con producto, vendedor, cantidad, precio |

> **Nota**: Solo muestra movimientos donde `id_usuario = request.user` (el comprador). Acceso restringido con `@login_required`.

---

### 3.5 Calificaciones

```
GET  /ventas/calificaciones/calificar/<movimiento_id>/
POST /ventas/calificaciones/calificar/<movimiento_id>/
GET  /ventas/calificaciones/historial/
```

**Calificar — Request (POST)**:

| Campo | Tipo | Requerido | Rango |
|---|---|---|---|
| `calificacion` | decimal | Sí | 1.0 – 5.0 (pasos de 0.5) |

**Response (AJAX success)**:
```json
{"success": true, "calificacion": 4.5}
```

---

## 4. Clientes (`/clientes/`)

```
GET /clientes/                                     → Listar clientes activos
GET /clientes/<pk>/                                → Detalle de cliente
GET /clientes/<cliente_id>/historial-compras/      → Historial de compras
```

---

## 5. Facturación (`/facturacion/`)

> Todos requieren `@login_required`. Generación de PDF con `xhtml2pdf`. Ver [[ARCHITECTURE#2.6]] y [[DECISIONS#ADR-016]].

```
POST /facturacion/crear/                                   → Crear factura desde el carrito actual
GET  /facturacion/detalle/<factura_id>/                    → Detalle de factura
GET  /facturacion/historial/                               → Historial de facturas del usuario
GET  /facturacion/pdf/<factura_id>/                        → Generar PDF (inline; ?descargar=1 → attachment)
GET  /facturacion/generar_pedido/<movimiento_id>/          → Crear/obtener factura desde un movimiento y redirigir a PDF
```

**Response (crear_factura)**:
- Success: `Redirect → /facturacion/detalle/<id>/` + mensaje de confirmación
- Error (carrito vacío): `Redirect → /ventas/carrito/` + mensaje de error

> **Nota**: `crear_factura` crea un `Movimiento` tipo `compra` + `ProductoUsuarioMovimiento` desde el carrito, luego genera la `Factura` con sus items y limpia el carrito.

---

## 6. OAuth (`/oauth/`)

```
GET /oauth/login/google-oauth2/                    → Inicio Google OAuth
GET /oauth/complete/google-oauth2/                 → Callback OAuth
```

**Estado**: Configurado, no activo.

---

## 7. Sistema

```
GET /                                              → Redirect según estado (ver home_redirect en config/urls.py)
GET /admin/                                        → Django Admin (si habilitado)
```

---

## Resumen de Endpoints

| Módulo | Endpoints documentados | Protegidos | AJAX |
|---|---|---|---|
| Usuarios (auth + admin) | 28 | 14 | 1 |
| Inventario | 10 | 9 | 4 |
| Ventas | 22 | 18 | 8 |
| Compras (sub-módulo ventas) | 2 | 2 | 0 |
| Clientes | 3 | 3 | 0 |
| Facturación | 5 | 5 | 0 |
| **Total apps** | **68** | — | — |

> **Rutas registradas en `urlpatterns`**: **68** en las 5 apps (`usuarios` 28, `inventario` 10, `ventas` 22, `clientes` 3, `facturacion` 5) + rutas raíz (`home`), OAuth (`social_django`) y `/admin/`. Los totales de "AJAX" se refieren a endpoints que responden `JsonResponse` ante `X-Requested-With: XMLHttpRequest`.

---

## Enlaces Relacionados

- [[PROJECT_CONTEXT]] — Contexto global
- [[ARCHITECTURE]] — Arquitectura que soporta estos endpoints
- [[DATABASE]] — Tablas que cada endpoint consulta/modifica
- [[REQUIREMENTS]] — Requisitos que cada endpoint satisface
