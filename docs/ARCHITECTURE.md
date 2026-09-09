# ARCHITECTURE.md — AgroSFT

> Arquitectura del sistema, módulos, patrones de diseño y decisiones técnicas.  
> **Metodología**: Specification-Driven Development (SDD)

---

## 1. Vista General de la Arquitectura

```mermaid
graph TB
    subgraph Browser
        LayoutVue[LayoutApp.vue<br/>Navbar + Footer + Toast]
        PageVue[Vue 3 Components<br/>Marketplace, Carrito, etc.]
        Templates[Django Templates<br/>(páginas individuales)]
    end

    subgraph Django App Layer
        CP[context_processors<br/>layout_data]
        URL[URL Router]
        Ctrl[Controllers / Views]
        Forms[Django Forms]
        Svc[Services]
        Repo[Repositories]
    end

    subgraph Infrastructure
        ORM[Django ORM]
        Auth[Auth Backend]
        MW[Middleware]
        Cache[LocMem Cache]
    end

    subgraph External
        MariaDB[(MariaDB 10.4)]
        FS[File System /media]
    end

    CP -->|JSON| LayoutVue
    Templates --> URL
    PageVue -->|AJAX| Ctrl
    URL --> Ctrl
    Ctrl --> Forms
    Ctrl --> Svc
    Svc --> Repo
    Ctrl --> ORM
    Repo --> ORM
    ORM --> MariaDB
    Auth --> MariaDB
    MW --> Ctrl
    Svc --> Cache
    Ctrl --> FS
```

### Capas del Sistema

| Capa | Responsabilidad | Ubicación |
|---|---|---|
| **Layout Vue** | Navbar, footer, notificaciones (2 estados: guest/user) | `frontend/src/layout/LayoutApp.vue` |
| **Presentación** | Templates Django + Componentes Vue por página | `templates/`, `frontend/src/*/` |
| **Context Processor** | Inyecta JSON con datos de layout a Vue | `core/context_processors.py` |
| **Routing** | Mapeo URL → Controller | `config/urls.py`, `apps/*/urls.py` |
| **Controllers** | Orquestación de requests, validación de permisos, renderizado | `apps/*/controllers/` |
| **Forms** | Validación de entrada del usuario | `apps/*/forms/` |
| **Services** | Lógica de negocio reutilizable | `apps/*/services/` |
| **Repositories** | Acceso a datos, queries complejos | `apps/*/repositories/` |
| **Models** | Mapeo ORM a tablas existentes | `apps/*/models/` |
| **Core** | Clases base, middleware, utilidades compartidas | `core/` |

---

## 2. Apps Django

### 2.1 `core` — Framework Base

```
core/
├── controllers/base_controller.py  → BaseController con json_response(), get_request_data()
├── models/base_model.py           → AbstractBaseModel (created_at, updated_at, is_active)
├── models/terminos_model.py       → Fake Manager para términos (sin tabla real)
├── repositories/base_repository.py → GenericRepository (CRUD, paginación, log_action)
├── services/base_service.py       → BaseFieldValidator (validación genérica de campos)
├── utils/helpers.py               → EstadoProducto, EstadoSolicitud, safe_int, safe_decimal
└── middleware.py                  → NoCacheMiddleware (previene caché post-logout)
```

### 2.2 `apps.usuarios` — Gestión de Usuarios

```
apps/usuarios/
├── controllers/
│   ├── auth_controller.py        → RegistroView, LoginView, LogoutView, PerfilView, CambiarPasswordView
│   └── terminos_controller.py    → TerminosView, AceptarTerminosView
├── forms/auth_forms.py           → RegistroForm, LoginForm, PerfilForm, CambiarPasswordForm
├── models/
│   ├── profile_model.py          → Tblusuarios (AUTH_USER_MODEL), UserProfile, UserDevice, UserAddress
│   └── terminos_model.py         → Termino, AceptacionTermino (POJOs sin DB)
├── services/terminos_service.py  → TerminosService (aceptación vía caché)
├── backends.py                   → TblusuariosAuthBackend (autenticación personalizada)
└── pipeline.py                   → create_user_custom (Google OAuth pipeline)
```

**Modelo de Usuario**: `Tblusuarios`
- `USERNAME_FIELD = 'correo'` (correo como identificador único)
- `AUTH_USER_MODEL = 'usuarios.Tblusuarios'`
- Manager: `TblusuariosManager` (create_user, create_superuser)
- Contraseña: campo `contraseña` con `make_password`/`check_password`

### 2.3 `apps.inventario` — Catálogo y Marketplace

```
apps/inventario/
├── controllers/producto_controller.py  → CRUD productos, marketplace, aprobar/rechazar, API stock
├── forms/producto_form.py             → ProductoForm (nombre, descripción, categoría, precio, cantidad, imagen múltiple)
├── models/producto.py                 → Estado, Categoria, Producto, ProductoImagen, ProductoUsuario, Calificacion
├── repositories/producto_repository.py → ProductoRepository (queries complejos, soft delete)
└── services/producto_service.py       → Validación de datos de producto
```

> [!note] `TipoMovimiento` consolidado (2026-09-07)
> El duplicado de `TipoMovimiento` en `apps.inventario` fue eliminado ([[DECISIONS#ADR-015]]). `apps.inventario.models` re-exporta ahora el canónico desde `apps.ventas.models.movimiento`.

**Arquitectura Dual de Productos**:

```mermaid
graph LR
    P[tblproducto<br>Catálogo Maestro] -->|1:N| PU[tblproductos_has_tblusuarios<br>Publicaciones por Vendedor]
    PU -->|N:1| U[tblusuarios<br>Vendedor]
    PU -->|N:1| E[estado<br>Aprobado/Pendiente/Rechazado]
    P -->|N:1| C[tblcategoria<br>Frutas/Verduras/etc]
```

- **tblproducto**: Catálogo unificado (nombre, descripción, categoría, stock_minimo)
- **tblproducto_imagenes**: Galería de imágenes por producto (carrusel). La primera imagen se conserva en `tblproducto.imagen` como portada (compatibilidad legacy)
- **tblproductos_has_tblusuarios**: Publicación individual (precio, cantidad, estado, calificación promedio)
- Un mismo producto genérico puede tener múltiples publicaciones de distintos vendedores

### 2.4 `apps.ventas` — Transacciones

```
apps/ventas/
├── controllers/
│   ├── carrito_controller.py       → CRUD carrito + checkout (todo @login_required)
│   ├── solicitud_controller.py     → Inbox vendedor (aceptar/rechazar/vender)
│   ├── venta_controller.py         → Listado y detalle de ventas
│   ├── compra_controller.py        → Mis Compras: listado y detalle del comprador
│   └── calificacion_controller.py  → Calificar transacción + historial
├── forms/calificacion_form.py      → Rating 1.0-5.0 pasos de 0.5
├── models/movimiento.py            → TipoMovimiento (canónico), Movimiento, ProductoUsuarioMovimiento
├── services/carrito_service.py     → Carrito basado en sesión
└── templatetags/ventas_extras.py   → Filtros de template `multiply`, `abs_value`
```

> [!note] Limpieza de modelos obsoletos (2026-09-07)
> `SolicitudCompra`, `DetalleSolicitudCompra`, `Venta`, `DetalleVenta` y sus forms fueron eliminados ([[DECISIONS#ADR-015]]). `TipoMovimiento` canónico reside aquí.

**Arquitectura de Movimientos**:

```mermaid
graph LR
    TM[tipo_movimiento<br>compra/venta/rechazada/vendida] -->|1:N| M[movimiento<br>Header de transacción]
    M -->|1:N| PUM[tblproductos_has_tblusuarios_has_movimiento<br>Detalles]
    PUM -->|N:1| PU[ProductoUsuario<br>Publicación]
    M -->|N:1| U[tblusuarios<br>Comprador]
```

**Convención de cantidades**:
- **Positiva**: Abastecimiento/entrada de stock
- **Negativa**: Venta/salida de stock

**Estados de solicitud por tipo_movimiento**:

| tipo_movimiento | Estado Lógico | Significado |
|---|---|---|
| `compra` | Recibida | Comprador envió solicitud |
| `venta` | Aceptada | Vendedor aceptó |
| `rechazada` | Rechazada | Vendedor rechazó |
| `vendida` | Completada | Transacción finalizada |
| `cancelada` | Cancelada | Venta cancelada (desde estado `venta`) |

### 2.5 `apps.clientes` — Historial

```
apps/clientes/
├── controllers/cliente_controller.py  → Listar clientes, detalle, historial de compras
├── forms/cliente_form.py             → (No utilizado activamente)
└── models/cliente.py                 → Cliente (managed=False, no usado en lógica de negocio)
```

### 2.6 `apps.facturacion` — Facturación

> [!warning] Excepción a la regla `managed = False`
> Es la **única app** que gestiona su schema con migraciones Django (`python manage.py migrate facturacion`), creando las tablas `factura` e `item_factura`. Ver [[DECISIONS#ADR-016]].

```
apps/facturacion/
├── controllers/factura_controller.py  → Crear/detalle/historial/PDF/generar desde pedido
├── models.py                          → Factura, ItemFactura (db_table='factura'/'item_factura')
├── services/factura_service.py        → FacturaService (creación desde carrito/movimiento, cancelación, historial)
├── migrations/                        → 0001_initial, 0002_... (gestionadas por Django)
└── templates/facturacion/             → detalle_factura, factura_pdf, historial_facturas
```

**Modelo de facturación**:

```mermaid
graph LR
    M[movimiento<br>Transacción] -->|opcional| F[factura<br>Cabecera]
    F -->|1:N| I[item_factura<br>Detalle]
    I -->|N:1| P[tblproducto]
    U[tblusuarios] -->|1:N| F
```

**Flujo**: El `FacturaService` crea un `Movimiento` (tipo `compra`) más los `ProductoUsuarioMovimiento` desde el carrito, y genera una `Factura` con sus `ItemFactura`. La generación de PDF usa `xhtml2pdf` (plantilla `factura_pdf.html`).

---

## 3. Frontend Architecture

### 3.1 Layout Global en Vue

> Layout estructural migrado a Vue.js. Ver [[DECISIONS#ADR-011]].

El navbar y el footer se renderizan desde **dos componentes Vue** (`NavbarApp.vue` y `FooterApp.vue`), ambos montados desde el mismo entry point `layout/main.js`. Reciben datos mediante el context processor `core.context_processors.layout_data`, que inyecta un JSON (`#layout-data`) con datos del usuario, URLs de navegación, contador del carrito y mensajes flash.

```mermaid
graph TB
    subgraph Django
        CP[context_processors.layout_data]
        Template[base.html]
    end
    subgraph Vite
        LayoutJS[layout/main.js]
        NavbarVue[NavbarApp.vue]
        FooterVue[FooterApp.vue]
    end
    subgraph Browser
        NavbarDOM[div#vue-navbar]
        FooterDOM[div#vue-footer]
    end

    CP -->|layout_data_json| Template
    Template -->|json_script layout-data| LayoutJS
    LayoutJS -->|createApp| NavbarVue
    LayoutJS -->|createApp| FooterVue
    NavbarVue -->|mount| NavbarDOM
    FooterVue -->|mount| FooterDOM
```

`NavbarApp.vue` recibe como props el objeto completo de datos (`user`, `urls`, `cart_count`, `messages`) y maneja 2 estados (guest/user), notificaciones toast y dropdown de usuario con navegación estándar unificada. `FooterApp.vue` recibe solo `urls` y renderiza el logo SVG oficial. Ambos componentes son **no-scoped** y reutilizan las clases CSS de Bootstrap 5 y las variables CSS del proyecto (`frontend/src/style.css`).

### 3.2 Integración Django + Vue (Componentes de Página)

```mermaid
sequenceDiagram
    participant Django as Django Controller
    participant Template as Django Template
    participant JS as main.js (Vite)
    participant Vue as Vue Component
    participant API as Django API

    Django->>Template: json.dumps(data)
    Template->>JS: <script id="data">{json}</script>
    JS->>Vue: createApp(Component, props)
    Vue->>API: fetch(url, options)
    API-->>Vue: JsonResponse
    Vue->>Vue: Update reactive state
```

### 3.3 Entry Points (Vite)

| Entry | Archivo | Componente | Props |
|---|---|---|---|
| `layout` | `frontend/src/layout/main.js` | `NavbarApp.vue` + `FooterApp.vue` | `user`, `urls`, `cart_count`, `messages` |
| `marketplace` | `frontend/src/marketplace/main.js` | `MarketApp.vue` | `initialProducts`, `categories`, `urls` |
| `carrito` | `frontend/src/carrito/main.js` | `CarritoApp.vue` | `items`, `urls` |
| `inventario` | `frontend/src/inventario/main.js` | `InventarioApp.vue` | `initialProducts`, `categories`, `estados`, `urls` |
| `calificaciones` | `frontend/src/calificaciones/main.js` | `CalificacionApp.vue` | `movimientoDetalle`, `urls` |

---

## 4. Middleware

| Middleware | Ubicación | Función |
|---|---|---|
| `SecurityMiddleware` | Django built-in | Headers de seguridad |
| `SessionMiddleware` | Django built-in | Gestión de sesiones |
| `CommonMiddleware` | Django built-in | Normalización de URLs |
| `CsrfViewMiddleware` | Django built-in | Protección CSRF |
| `AuthenticationMiddleware` | Django built-in | Inyección de `request.user` |
| `MessageMiddleware` | Django built-in | Framework de mensajes |
| `XFrameOptionsMiddleware` | Django built-in | Prevención de clickjacking |
| `NoCacheMiddleware` | `core/middleware.py` | Previene caché para usuarios autenticados |

---

## 5. Autenticación

### Backend Personalizado

`TblusuariosAuthBackend` (`apps/usuarios/backends.py`):
- Autentica contra tabla `tblusuarios` usando campo `correo`
- Usa `check_password` de Django para verificar hash
- Retorna instancia de `Tblusuarios`

### Google OAuth2

Configurado vía `social-auth-app-django`:
- Pipeline personalizado: `apps/usuarios/pipeline.py` → `create_user_custom`
- Crea usuarios `Tblusuarios` con campos personalizados
- **Estado**: Configurado pero no activo (credenciales comentadas)

---

## 6. Sesiones y Caché

| Configuración | Valor | Razón |
|---|---|---|
| `SESSION_ENGINE` | `django.contrib.sessions.backends.signed_cookies` | Evita dependencia de tabla `django_session` (cookie firmada, ver [[DECISIONS#ADR-011]]) |
| `CACHES.default` | `LocMemCache` | Caché en memoria (categorías, estados) |
| `SESSION_EXPIRE_AT_BROWSER_CLOSE` | `True` | Seguridad |
| `SESSION_COOKIE_AGE` | `1800` (30 min) | Timeout de inactividad |

---

## 7. Gestión de Base de Datos

### Principio Fundamental

> [!danger] Regla Absoluta (con excepción)
> **Django NO gestiona el schema de base de datos** para las apps `usuarios`, `inventario`, `ventas` y `clientes`.
> - Todos los modelos de esas apps: `managed = False`
> - `MIGRATION_MODULES = {app: None}` para todas esas apps
> - El schema se mantiene directamente en MariaDB
> - Los triggers de BD gestionan stock y calificaciones automáticamente
>
> **Excepción**: la app `apps.facturacion` **sí gestiona su schema con migraciones Django** (tablas `factura` e `item_factura`). Ver [[DECISIONS#ADR-016]].

### Trigger Crítico

`trg_actualizar_stock_oferta`: Se ejecuta al insertar en `tblproductos_has_tblusuarios_has_movimiento`.
- Actualiza `cantidad` en `tblproductos_has_tblusuarios`
- Actualiza `calificacion_promedio` si se califica

> **NUNCA** replicar esta lógica en Python.

---

## 7.1 Media Storage (Imágenes)

| Configuración | Valor | Notas |
|---|---|---|
| `MEDIA_URL` | `/media/` | Base pública de archivos subidos |
| `MEDIA_ROOT` | `BASE_DIR / 'media'` | Directorio físico de almacenamiento |
| `Producto.imagen` | `ImageField(upload_to='productos/')` | Fotografía del producto en `tblproducto` |
| `UserProfile.imagen_perfil` | `ImageField(upload_to='profile_pictures/')` | Foto de perfil en `user_profiles` |

- En desarrollo (`DEBUG=True`), `config/urls.py` sirve los media con `static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)`.
- Los controllers de producto y perfil pasan `request.FILES` a los formularios para recibir archivos (`multipart/form-data`).
- Validación: extensiones `jpg/jpeg/png/webp` (`FileExtensionValidator`) y tamaño máximo 5MB (`core.utils.helpers.validate_image_size`), aplicada en **modelos** y **formularios**.
- Los valores en BD son rutas `VARCHAR(255)`; los templates Vue y Django usan `.url` sobre los campos `ImageField` o la URL ya resuelta en los dicts del controller.

---

## 8. Patrones de Diseño

| Patrón | Uso | Ejemplo |
|---|---|---|
| **Controller-Service-Repository** | Separación de responsabilidades | Controller → Service → Repository → Model |
| **Template Method** | BaseController con métodos comunes | `json_response()`, `get_request_data()` |
| **Strategy** | Auth backends intercambiables | `TblusuariosAuthBackend`, `GoogleOAuth2` |
| **Proxy** | Models como proxy de tablas externas | Todos los modelos con `managed = False` |
| **Session Facade** | Carrito encapsulado en sesión | `Carrito(request)` |
| **Observer** | Vue reactive state | `ref()`, `computed()`, `watch()` |

---

## Enlaces Relacionados

- [[PROJECT_CONTEXT]] — Contexto global
- [[DATABASE]] — Modelo de datos detallado
- [[API]] — Endpoints del sistema
- [[DECISIONS]] — Registro de decisiones arquitectónicas
