# CHANGELOG.md — AgroSFT

> Historial cronológico de cambios significativos en el proyecto.  
> Formato basado en [Keep a Changelog](https://keepachangelog.com/).

---

## [Unreleased]

### Removed (2026-09-02)
- **Eliminación del botón "Venta Directa" en el Carrito de Compras**:
  - `frontend/src/carrito/CarritoApp.vue`: Eliminado el botón "Venta Directa" del pie del carrito de compras.
  - `apps/ventas/templates/ventas/carrito/detalle.html`: Eliminado el botón "Venta Directa" de la plantilla Django del carrito.
  - Recompilación de assets frontend mediante Vite (`npm run build`).
- **Eliminación completa de los enlaces a "Mi historial / Historial de términos"**:
  - `frontend/src/layout/NavbarApp.vue`: Se eliminó el ítem de navegación "Mi historial" del menú desplegable de usuario.
  - `apps/usuarios/templates/usuarios/perfil.html`: Se removieron los enlaces hacia el historial de términos en la barra lateral y en la tarjeta de términos.
  - `apps/usuarios/templates/usuarios/terminos.html`: Se eliminó el botón "Ver mi Historial".
  - Recompilación de assets frontend mediante Vite (`npm run build`).

### Added (2026-08-20)
- **Soporte de imágenes en productos y perfil de usuario** (ver [[DECISIONS#ADR-013]]):
  - `apps/inventario/models/producto.py`: campo `imagen` como `ImageField(upload_to='productos/')` con validación de extensión (JPG/JPEG/PNG/WEBP) y tamaño máx. 5MB
  - `apps/usuarios/models/profile_model.py`: `imagen_perfil` convertido a `ImageField(upload_to='profile_pictures/')` con los mismos validators
  - `core/utils/helpers.py`: función `validate_image_size` (límite 5MB)
  - `apps/inventario/forms/producto_form.py` y `apps/usuarios/forms/auth_forms.py`: validators replicados en los campos de los formularios (validación server-side real en `is_valid()`)
  - `apps/inventario/controllers/producto_controller.py`: `request.FILES` en `crear_producto`/`editar_producto`; exposición de la URL de imagen en listas y marketplace
  - `apps/usuarios/controllers/auth_controller.py`: guardado/eliminación de foto de perfil en `UserProfile`
  - Templates y Vue: renderizado de imagen en marketplace, inventario, detalle, carrito y avatar del navbar
- **`scripts/agregar_imagen_producto.sql`** [NEW]: script idempotente de referencia para la columna `imagen` de `tblproducto` (ya existente en BD; documentación del cambio para reproducción)

### Fixed (2026-08-20)
- **Imagen rota en grids server-side** — Los controllers ahora exponen la URL de imagen como string (`producto.imagen`), pero `marketplace.html`, `producto_list.html` y `producto_detail.html` usaban `{{ producto.imagen.url }}` (válido solo para modelos), generando `<img src="">`:
  - Cambiado a `{{ producto.imagen }}` en los tres templates

### Fixed (2026-06-30)
- **Tablas `factura` e `item_factura` no existían en MariaDB** — La migración de `facturacion` no se había ejecutado tras el merge, causando error "Table doesn't exist" al hacer clic en "Generar Factura":
  - Ejecutado `python manage.py migrate facturacion` creando las tablas `factura` e `item_factura`
  - El flujo completo carrito → factura → solicitud → WhatsApp ahora funciona correctamente
- **Error `django_session` no existe al iniciar sesión** — `ProgrammingError (1146)` al POST en `/usuarios/login/`:
  - `config/settings.py`: `SESSION_ENGINE` cambiado de `django.contrib.sessions.backends.db` a `django.contrib.sessions.backends.signed_cookies`
  - Las sesiones ahora se almacenan en cookies firmadas, eliminando la dependencia de la tabla `django_session` en MariaDB
  - Ver [[DECISIONS#ADR-011]] para el análisis completo de la decisión
- **Clave incorrecta `total_productos` en detalle_solicitud** — El controller pasaba `total_productos` pero el template esperaba `total_productos_mios`, dejando el campo vacío:
  - `apps/ventas/controllers/solicitud_controller.py`: Cambiado `total_productos` a `total_productos_mios` en el dict del contexto

### Added (2026-06-30)
- **WhatsApp Click-to-Chat**: Nueva función `generar_whatsapp_link()` en `core/utils/helpers.py` que genera enlaces `wa.me` con formato internacional (+57 Colombia) y mensaje predefinido.
- **Contacto WhatsApp post-aceptación**: Al aceptar una solicitud de compra, el sistema genera automáticamente un enlace de WhatsApp y muestra un modal con botón para abrir el chat del comprador (`apps/ventas/controllers/solicitud_controller.py`).
- **Enlace cliqueable**: El número de teléfono del comprador en el detalle de solicitud ahora es un enlace a WhatsApp cuando la solicitud está aceptada (`apps/ventas/templates/ventas/solicitudes/solicitud_detail.html`).
- **Requisitos RF-V18 y RF-V19**: Documentados en REQUIREMENTS.md
- **Historia US-14**: Contactar comprador por WhatsApp documentada en USER_STORIES.md
- **API.md**: Documentado campo `whatsapp_link` en respuesta de aceptar solicitud

### Changed (2026-06-30)
- `REQUIREMENTS.md`: Agregados RF-V18 y RF-V19, actualizado RNF-U05
- `USER_STORIES.md`: Agregada US-14, actualizado conteo (14 completadas)
- `API.md`: Documentado campo `whatsapp_link` en respuesta AJAX de aceptar solicitud

### Removed (2026-06-25)
- **Módulo Vue de solicitudes eliminado** — Se revirtió a la tabla Django server-side original:
  - `frontend/src/solicitudes/SolicitudApp.vue`: Eliminado
  - `frontend/src/solicitudes/main.js`: Eliminado
  - `vite.config.js`: Eliminada entrada `solicitudes`
  - `apps/ventas/templates/ventas/solicitudes/solicitud_list.html`: Eliminado script Vue y div de montaje
  - Se mantiene el controlador Django (`solicitud_controller.py`) y templates server-side como única implementación

### Fixed (2026-06-25)
- **Logo del navbar ya no redirige al login** — El logo siempre enviaba a `/` que redirigía a `usuarios:login` sin importar el estado de autenticación:
  - `config/urls.py`: `home_redirect` ahora redirige a `inventario:marketplace` (usuarios autenticados no-staff), `usuarios:admin_usuarios_list` (staff) o `usuarios:login` (invitados)
- **Footer en posición inferior corregido** — El footer se mostraba en la parte superior en páginas con poco contenido:
  - Movido `margin-top: auto` de `.footer` (elemento anidado dentro de `#vue-footer`) a `#vue-footer` (hijo directo del body flex), asegurando que el footer se empuje al fondo correctamente

### Added (2026-06-25)
- **Nombre "AGROSFT" junto al logo en el navbar** — Agregado texto `<span>AGROSFT</span>` al lado del logo en `NavbarApp.vue`

### Added (2026-06-25)
- **Layout global migrado a Vue.js** — Navbar, footer y notificaciones ahora son un componente Vue (`LayoutApp.vue`) montado desde `base.html`:
  - Navbar con 3 estados: no autenticado, autenticado, staff (roles, carrito, dropdown de usuario)
  - Footer con logo SVG oficial
  - Notificaciones toast con auto-dismiss (animación escalonada)
- **Logo oficial del proyecto**: `static/img/agrosft_o.svg` — renderizado por Vue en navbar y footer
- **Context processor `core.context_processors.layout_data`**: inyecta datos de layout (usuario, URLs, carrito, mensajes) como JSON para Vue
- **Entry point Vite**: `frontend/src/layout/main.js` → bundle `layout.js` (11.64 kB)

### Added (2026-06-30)
- **Recuperación de contraseña con Brevo REST API** — Implementada la recuperación de contraseña usando la API REST de Brevo y el sistema nativo de Django:
  - `apps/usuarios/services/email_service.py` [NEW]: Consumo de la API de Brevo a través de la librería `requests`, con envío de correos que incluyen una plantilla HTML profesional (destacando a AGROSFT) y una versión en texto plano. Uso del remitente verificado a través de `settings.DEFAULT_FROM_EMAIL` y manejo seguro de errores con logs.
  - `apps/usuarios/forms/auth_forms.py`: Definido el formulario `PasswordResetRequestForm` para capturar el correo electrónico. Definido `NuevaPasswordForm`, formulario propio compatible con `Tblusuarios` (hereda de `models.Model`), que reemplaza a `SetPasswordForm` de Django (incompatible con modelos que no heredan de `AbstractBaseUser`).
  - `apps/usuarios/utils/password_reset_tokens.py` [NEW]: `TblusuariosPasswordResetTokenGenerator`, generador de tokens personalizado que sobreescribe `_make_hash_value()` para usar los campos reales `user.correo` y `user.contraseña` del modelo `Tblusuarios`, evitando la llamada a `get_email_field_name()` que solo existe en `AbstractBaseUser`.
  - `apps/usuarios/controllers/auth_controller.py`: Modificadas las vistas `UserPasswordResetView` y `UserPasswordResetConfirmView` para integrar la lógica de generación de tokens (`agrosft_token_generator`), codificación base64 (`uidb64`), y la actualización segura de contraseñas utilizando `user.set_password()` + `user.save()` (mecanismo nativo del proyecto).

### Changed (2026-06-24)
- **Paleta "Raíz y Confianza" implementada** — Rebranding visual completo:
  - `base.html`: Variables CSS en `:root` actualizadas (verde claro #3C8D3C, naranja #E8853B, azul cielo #3A8BC8, crema #F5F1E8, texto #3D5245); sombras, hover y colores inline reemplazados; corregido typo "AGROSTF" → "AGROSFT"
  - `admin-custom.css`: Panel admin rebrandeado con verde bosque + ámbar + azul cielo
  - `base_site.html`: Enlace a sitio principal actualizado
  - `admin_usuarios_list.html`: Avatares de roles con nuevos colores
  - `admin_estadisticas.html`: Card gradient a verde bosque
  - `SolicitudApp.vue`: Hover color actualizado
  - Nuevas variables: `--color-info: #7BAFD4`, `--color-rating: #E07C3A`
- **Documentación SDD alineada con BD real**:
  - `DATABASE.md`: Agregado tipo `cancelada` (id=5) a `tipo_movimiento`; documentados 5 triggers reales (separando calificación en INSERT/UPDATE/DELETE); agregada columna `imagen` a tblproducto; tablas `user_profiles`, `user_devices`, `user_addresses` confirmadas como existentes en MariaDB con FK CASCADE; actualizado flujo de stock (solo `vendida` descuenta)
  - `ARCHITECTURE.md`: Agregado `cancelada` a la tabla de estados de solicitud
  - `USER_STORIES.md`: Agregado estado `Cancelada` al diagrama de flujo de solicitudes
  - `03-BASE-DATOS.md`: Agregado tipo `cancelada`; triggers actualizados a 5; tablas extendidas marcadas como inexistentes; flujo de stock documentado

### Added (2026-06-17)
- **Boton "Cancelar Venta"** en ventas con estado "En proceso"
  - Endpoint `POST /ventas/<pk>/cancelar/` en `venta_controller.py`
  - Cambia `tipo_movimiento` a 'cancelada' (nuevo tipo en BD)
  - No afecta stock (stock solo se descuenta al marcar 'vendida')
  - Badge rojo "Cancelada" en listado y detalle
- **Modulo "Mis Compras"**: Vista del comprador con listado y detalle de pedidos
  - `compra_controller.py` con `listar_compras()` y `detalle_compra()`
  - URLs: `GET /ventas/compras/` y `GET /ventas/compras/<pk>/`
  - Estados traducidos: Pendiente (compra), En proceso (venta), Finalizada (vendida)
  - Enlace "Mis Compras" en navbar para usuarios no-staff
- **Botón "Marcar como Vendido"** en módulo de ventas (`venta_list.html` y `venta_detail.html`)
  - Endpoint `POST /ventas/<pk>/marcar-vendida/` en `venta_controller.py`
  - Cambia `tipo_movimiento` de 'venta' a 'vendida' en BD
  - Solo visible para ventas con estado "En proceso"
  - Confirmación antes de ejecutar
- **Estados traducidos** en módulo de ventas: 'venta' → "En proceso", 'vendida' → "Vendido"
- **RF-V16**: Marcar venta como vendida desde módulo de ventas
- **RF-V17**: Actualización automática de stock al marcar como "Vendido"
  - Modificado trigger `trg_actualizar_stock_oferta`: ya no descuenta stock en solicitudes de compra (tipo='compra')
  - Nuevo trigger `trg_descontar_stock_vendida`: descuenta stock cuando movimiento cambia a 'vendida'
  - Validación de stock suficiente antes de confirmar venta en `venta_controller.py`
  - Scripts SQL: `scripts/trigger_modificar_stock.sql`, `scripts/trigger_stock_vendida.sql`

### Fixed (2026-06-17)
- **Stock negativo**: Corrección del problema donde pedidos (checkout) descontaban stock incorrectamente
  - Script `scripts/corregir_stock_negativo.sql` revierte descuentos incorrectos de movimientos 'compra' previos
  - Nuevo trigger `scripts/trigger_proteccion_stock.sql` con validación `SIGNAL` que impide stock negativo
  - Checkout (`carrito_controller.py`) ahora refresca stock desde BD antes de validar disponibilidad

### Pendiente (ver [[ROADMAP#Fase 1]])
- Corregir SQL injection en `tabla_existe()` y `columna_existe()`
- Agregar `@login_required` a vistas de carrito sin protección
- Eliminar clase `TemporalUsuario` peligrosa
- Consolidar modelo duplicado `TipoMovimiento`
- Eliminar modelos obsoletos (`SolicitudCompra`, `Venta`)
- Completar backend de password reset

---

## [2026-06-17] — Documentación SDD y Refactor Solicitudes JS

### Added
- **Documentación SDD completa** (9 archivos):
  - `PROJECT_CONTEXT.md` — Contexto global del proyecto
  - `REQUIREMENTS.md` — 45 requisitos funcionales + 17 no funcionales + 8 brechas
  - `USER_STORIES.md` — 13 historias de usuario con criterios de aceptación
  - `ARCHITECTURE.md` — Arquitectura detallada con diagramas Mermaid
  - `DATABASE.md` — Modelo de datos completo (11 tablas documentadas)
  - `API.md` — 36 endpoints con contratos de request/response
  - `ROADMAP.md` — Plan de evolución en 4 fases
  - `DECISIONS.md` — 8 registros de decisiones técnicas (ADR)
  - `CHANGELOG.md` — Este archivo

### Changed
- **`frontend/src/solicitudes/SolicitudApp.vue`**: Refactorizado completamente a JavaScript puro
  - Eliminado `import { getCSRFToken }` (ya no usa CSRF)
  - Eliminado `defineProps` (ya no recibe props del servidor)
  - Agregados datos mock con 5 solicitudes de ejemplo
  - Agregadas stats cards con contadores por estado
  - Agregado filtro por estado, búsqueda y ordenamiento
  - Agregado modal de detalle con desglose de productos
  - Agregadas notificaciones toast
  - Agregadas transiciones CSS suaves
  - `onMounted` intenta cargar JSON de Django primero, fallback a mock data

- **`frontend/src/solicitudes/main.js`**: Simplificado
  - Eliminado `JSON.parse(document.getElementById('solicitudes-data').textContent)`
  - Eliminado paso de props al componente
  - Ahora: `createApp(SolicitudApp).mount(el)`

- **Documentación existente actualizada**:
  - `06-MODULO-VENTAS.md` — Sección de solicitudes actualizada a "COMPLETADO"
  - `08-FRONTEND.md` — SolicitudApp.vue documentada como autocontenida

### Removed
- Código duplicado en `SolicitudApp.vue` (versión vieja DB-conectada eliminada)
- Archivos placeholder de Obsidian (`Bienvenido.md`, `cree un enlace.md`)

---

## [Pre-2026-06-17] — Estado Base del Proyecto

### Estado al inicio de documentación

**Módulos funcionales**:
- ✅ Usuarios: Registro, Login, Logout, Perfil, Cambiar Password, Términos
- ✅ Inventario: CRUD productos, Marketplace, Aprobación/Rechazo
- ✅ Ventas: Carrito (sesión), Solicitudes (inbox vendedor), Ventas, Calificaciones
- ✅ Clientes: Listado, Detalle, Historial de compras
- ✅ Frontend: 5 componentes Vue 3 (MarketApp, CarritoApp, InventarioApp, SolicitudApp, CalificacionApp)

**Problemas técnicos identificados**:
- ❌ SQL injection en `tabla_existe()` y `columna_existe()` (auth_controller.py)
- ❌ `TemporalUsuario.check_password()` siempre retorna True
- ⚠️ Vistas de carrito sin `@login_required`
- ⚠️ Modelo `TipoMovimiento` duplicado en inventario y ventas
- ⚠️ Modelos obsoletos `SolicitudCompra`, `Venta` aún en código
- ⚠️ Modelo `Cliente` sin `managed = False`
- ⚠️ Password reset con UI pero sin backend real

---

## Convenciones de Formato

### Tipos de Cambio

| Tipo | Descripción |
|---|---|
| **Added** | Nueva funcionalidad |
| **Changed** | Modificación de funcionalidad existente |
| **Fixed** | Corrección de bug |
| **Removed** | Funcionalidad eliminada |
| **Security** | Cambio relacionado con seguridad |
| **Deprecated** | Funcionalidad marcada para eliminación futura |

### Criterios de Inclusión

Se registran cambios que:
- Afectan la API pública o comportamiento observable
- Modifican la estructura de datos
- Añaden/eliminan funcionalidades significativas
- Corrigen bugs de seguridad o datos
- Cambian dependencias externas

No se registran:
- Refactorizaciones internas sin impacto observable
- Cambios de formato o estilo de código
- Actualizaciones de documentación menor

---

## Enlaces Relacionados

- [[PROJECT_CONTEXT]] — Contexto global del proyecto
- [[ROADMAP]] — Plan de cambios futuros
- [[DECISIONS]] — Decisiones técnicas que motivaron estos cambios
- [[REQUIREMENTS]] — Requisitos que guían la evolución
