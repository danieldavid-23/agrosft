# 📚 Documentación completa de AgroSFT (español)

## 1. Visión General
AgroSFT es una plataforma **Marketplace agrícola** desarrollada con **Django** (Python) y **Vue.js** (frontend parcial). Permite a agricultores ofrecer sus productos y a compradores adquirirlos, gestionando stock, transacciones y facturación.

## 2. Arquitectura y Organización
```
agrosft/
├─ config/               # settings, urls, wsgi, asgi
├─ core/                 # middleware, context processors, template tags, utils
├─ apps/
│   ├─ usuarios/        # usuarios, perfil, autenticación (email/password y Google OAuth)
│   ├─ inventario/      # catálogos, productos, categorías, publicación de productos
│   ├─ ventas/          # carrito, solicitudes, movimientos, calificaciones
│   ├─ facturacion/     # facturas y líneas de factura
│   └─ clientes/        # datos de clientes (direcciones, contactos)
├─ templates/            # plantillas Django (HTML)
├─ static/               # CSS, JS, imágenes
├─ media/                # archivos subidos (fotos de producto, avatar)
├─ frontend/             # SPA Vue.js (navbar, layout)
└─ docs/                 # documentación interna
```

### 2.1 Módulo **core**
- **middleware.py** – `NoCacheMiddleware` evita que páginas protegidas queden en caché después de logout.
- **context_processors.py** – `layout_data` inyecta datos globales (usuario, carrito, mensajes) a todas las plantillas.
- **templatetags/currency_tags.py** – filtros `currency_cop`, `format_cantidad`, `clean_producto_nombre` para formatear valores monetarios y nombres.
- **utils/helpers.py** – funciones auxiliares (`safe_int`, `validar_tamaño_imagen`, `generar_whatsapp_link`).

## 3. Modelos Clave
| Modelo | Tabla (MySQL) | Propósito |
|--------|----------------|----------|
| `Tblusuarios` | `tblusuarios` | Usuario principal (correo como username). |
| `UserProfile` | `user_profiles` | Extensión de perfil (foto, bio, zona horaria). |
| `Producto` | `tblproducto` | Catálogo maestro de productos.
| `Categoria` | `tblcategoria` | Categorías (Frutas, Verduras, Insumos…). |
| `ProductoUsuario` | `tblproductos_has_tblusuarios` | Publicación de un producto por un agricultor (precio y stock propio). |
| `Estado` | `estado` | Estado de publicación (Pendiente, Aprobado, Rechazado). |
| `Movimiento` | `movimiento` | Cabecera de transacción (compra/venta). |
| `ProductoUsuarioMovimiento` | `tblproductos_has_tblusuarios_has_movimiento` | Detalle de cada movimiento, actualiza stock vía triggers DB. |
| `TipoMovimiento` | `tipo_movimiento` | `compra` o `venta`. |
| `Factura` | `factura` | Factura emitida por una compra. |
| `ItemFactura` | `item_factura` | Línea de factura (producto, cantidad, precio). |
| `Cliente` | `clientes` | Información de cliente (dirección, teléfono). |

> **Nota:** La mayoría de los modelos tienen `managed = False` porque la base de datos ya existía y se mantiene fuera de migraciones Django.

## 4. Patrones de Diseño
- **Repository Pattern** – `ProductoRepository` centraliza consultas y operaciones CRUD.
- **Service Layer** – `ProductoService`, `CarritoService` encapsulan lógica de negocio y coordinan repositorios y DTOs.
- **DTO (Data Transfer Objects)** – `ProductoDTO`, `ProductoCreateDTO`, `ProductoUpdateDTO` definen la estructura de datos para entrada/salida.
- **Middleware** – `NoCacheMiddleware` para control de caché.
- **Context Processor** – `layout_data` para datos globales.
- **Template Tags** – filtros personalizados de moneda.
- **Custom Auth Backend** – `TblusuariosAuthBackend` permite login con correo y contraseña.
- **OAuth Pipeline** – `create_user_custom` crea usuarios automáticamente al iniciar sesión con Google.
- **Soft Delete** – productos se marcan como `eliminado=True` en vez de borrarse físicamente.
- **Transaction Atomic** – checkout del carrito usa `transaction.atomic()` para consistencia.

## 5. Seguridad
| Área | Medidas Implementadas |
|------|-----------------------|
| **Autenticación** | Backend propio (`TblusuariosAuthBackend`) + Google OAuth2 mediante `social-auth-app-django`. |
| **Contraseñas** | `AUTH_PASSWORD_VALIDATORS` (mínimo 8 caracteres, no numérico, no común). Hash con PBKDF2‑SHA256. |
| **CSRF** | `CsrfViewMiddleware` activo en todo el proyecto. Todos los formularios usan `{% csrf_token %}`. |
| **Headers HTTP** | `SECURE_BROWSER_XSS_FILTER`, `SECURE_CONTENT_TYPE_NOSNIFF`, `X_FRAME_OPTIONS='DENY'`. En producción `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, HSTS (1 año). |
| **Sesiones** | Cookies firmadas (`signed_cookies`), expiración a los 30 min o al cerrar el navegador. |
| **Validación de Archivos** | `FileExtensionValidator` (jpg, jpeg, png, webp) + `validate_image_size` (≤ 5 MB). |
| **Anti‑enumeración** | En reset de contraseña, si el email no existe se silencia la respuesta. |
| **Cache Control** | `NoCacheMiddleware` añade `Cache-Control: no-store, no-cache, must-revalidate`. |
| **Transacciones** | Checkout envuelto en `transaction.atomic()`; triggers MySQL actualizan stock y calificación automáticamente. |

## 6. Flujos Principales
### 6.1 Registro y Login
1. **Registro** – `RegistroView` valida datos, usa `TblusuariosManager.create_user`. 
2. **Login** – `LoginView` llama a `authenticate` → `TblusuariosAuthBackend`. 
3. **Google OAuth** – pipeline llama a `create_user_custom` (crea usuario si no existe). 
### 6.2 Publicación de Producto
1. Agricultor envía formulario → `ProductoCreateDTO`.
2. `ProductoService.crear_producto` → `ProductoRepository.create` crea registro en `tblproducto` y `tblproductos_has_tblusuarios` con estado `Pendiente`.
3. Admin aprueba → Cambia a `Aprobado`. 
### 6.3 Carrito y Checkout
1. Usuario agrega producto → `Carrito.agregar` (sesión).
2. En checkout (`checkout_carrito`):
   - `transaction.atomic()`
   - Crea `Movimiento` tipo `compra`.
   - Por cada ítem crea `ProductoUsuarioMovimiento` (cantidad negativa).
   - Triggers MySQL actualizan stock y promedio de calificación.
   - Vacía el carrito.
### 6.4 Solicitudes de Compra (para agricultores)
1. Agricultor accede a `/ventas/solicitudes/` → `listar_solicitudes`.
2. Se filtran `Movimiento` de tipo `compra` que contienen productos del agricultor.
3. Se muestra comprador, productos, total y botón WhatsApp (`generar_whatsapp_link`). 
### 6.5 Facturación
1. Tras checkout se crea `Factura` vinculada al `Movimiento`.
2. `ItemFactura` almacena detalle de cada producto.
3. Plantilla PDF genera la factura (no incluida en código). 

## 7. URLs Principales
```python
# config/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('usuarios/', include('apps.usuarios.urls')),
    path('inventario/', include('apps.inventario.urls')),
    path('ventas/', include('apps.ventas.urls')),
    path('facturacion/', include('apps.facturacion.urls')),
    path('oauth/', include('social_django.urls', namespace='social')),
]
```
Cada app tiene su propio `urls.py` con rutas CRUD y vistas protegidas por `@login_required`.

## 8. Herramientas y Dependencias
- **Python 3.14**, **Django 5.0**
- **MySQL** (con `django.db.backends.mysql`)
- **django‑social‑auth** (Google OAuth)
- **Vue 3** + **Vite** (navbar y layout)
- **Bootstrap 5** (estilos de plantillas)
- **Pillow** (procesamiento de imágenes)
- **django‑extensions** (comandos útiles)

## 9. Buenas Prácticas y Puntos a Mejorar
- **Validar stock antes de crear `Movimiento`** → ya existe, pero se podría optimizar con consulta `SELECT ... FOR UPDATE` para evitar condiciones de carrera.
- **Centralizar constantes** (p.ej. tipos de movimiento) en un `enum.Enum` en `core/constants.py`.
- **Documentar triggers de MySQL** en `docs/DB_TRIGGERS.md` para que el equipo de DB los mantenga.
- **Añadir pruebas unitarias** para los servicios (`ProductoService`, `Carrito`) y los repositorios.
- **Migrar a gestión de modelos** (`managed = True`) cuando la base de datos ya esté bajo control de Django.

---
> **Resumen rápido**: AgroSFT combina una arquitectura multicapa (Controllers → Services → Repositories → Models) con patrones de diseño robustos, seguridad a nivel de middleware, autenticación dual y un flujo de compra que garantiza consistencia de stock mediante transacciones atómicas y triggers de base de datos.

---
**Fin de la documentación**.
