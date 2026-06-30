# API.md — AgroSFT

> Contratos de endpoints: rutas, métodos, payloads y respuestas.  
> **Framework**: Django 6.0.2 | **Formato**: HTML + JSON (AJAX)

---

## Convenciones

- Las respuestas AJAX usan `JsonResponse` con header `X-Requested-With: XMLHttpRequest`
- Formularios estándar envían `application/x-www-form-urlencoded` con CSRF token
- Todas las rutas protegidas requieren `@login_required` (excepto auth y carrito)
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

**Response (POST success)**: `Redirect → /inventario/marketplace/` o `?next=` param

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
| `imagen_perfil` | file | No | Imagen JPG/PNG |
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

### 2.3 Crear Producto

```
GET  /inventario/producto/nuevo/
POST /inventario/producto/nuevo/
```

**Request Body (POST)**:

| Campo | Tipo | Requerido | Descripción |
|---|---|---|---|
| `nombre` | string | Sí | Nombre del producto |
| `descripcion` | string | No | Descripción |
| `id_categoria` | int | Sí | ID de categoría |
| `precio` | decimal | Sí | Precio unitario |
| `cantidad` | int | Sí | Stock inicial |
| `stock_minimo` | int | No | Umbral mínimo (default: 5) |

**Response**: `Redirect → /inventario/`

---

### 2.4 Editar Producto

```
GET  /inventario/producto/<pk>/editar/
POST /inventario/producto/<pk>/editar/
```

**Request Body**: Igual que Crear Producto.

---

### 2.5 Eliminar Producto

```
POST /inventario/producto/<pk>/eliminar/
```

**Response (AJAX)**:
```json
{"success": true, "producto_id": 1}
```

---

### 2.6 Aprobar/Rechazar Producto (Admin)

```
POST /inventario/producto/<id>/aprobar/
POST /inventario/producto/<id>/rechazar/
```

**Requiere**: `request.user.is_staff == True`

---

### 2.7 API Verificar Stock

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

## 5. OAuth (`/oauth/`)

```
GET /oauth/login/google-oauth2/                    → Inicio Google OAuth
GET /oauth/complete/google-oauth2/                 → Callback OAuth
```

**Estado**: Configurado, no activo.

---

## 6. Sistema

```
GET /                                              → Redirect a /usuarios/login/
GET /admin/                                        → Django Admin (si habilitado)
```

---

## Resumen de Endpoints

| Módulo | Endpoints | Protegidos | AJAX |
|---|---|---|---|
| Usuarios | 12 | 5 | 1 |
| Inventario | 8 | 7 | 4 |
| Ventas | 17 | 13 | 8 |
| Clientes | 3 | 3 | 0 |
| **Total** | **40** | **28** | **13** |

---

## Enlaces Relacionados

- [[PROJECT_CONTEXT]] — Contexto global
- [[ARCHITECTURE]] — Arquitectura que soporta estos endpoints
- [[DATABASE]] — Tablas que cada endpoint consulta/modifica
- [[REQUIREMENTS]] — Requisitos que cada endpoint satisface
