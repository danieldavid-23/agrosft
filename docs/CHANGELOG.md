# CHANGELOG.md — AgroSFT

> Historial cronológico de cambios significativos en el proyecto.  
> Formato basado en [Keep a Changelog](https://keepachangelog.com/).

---

## [Unreleased]

### Removed (2026-09-08)
- **Eliminación de la vista y módulo de Auditoría del panel de administración**:
  - `apps/usuarios/controllers/admin_usuarios_controller.py`: Eliminada la vista `admin_audit_logs`.
  - `apps/usuarios/urls.py`: Eliminada la ruta `/usuarios/admin-auditoria/` y su import.
  - `templates/usuarios/admin_audit_logs.html`: Eliminada la plantilla asociada.
  - `core/context_processors.py`: Eliminada la clave `urls.admin_auditoria` del layout global.
  - `frontend/src/layout/NavbarApp.vue`: Eliminado el enlace de "Auditoría" del menú superior del administrador (quedan 4 módulos: Usuarios, Categorías, Moderación, Estadísticas).
  - `templates/base.html`: Versión de assets actualizada a `?_v=20260908_2` tras recompilar el bundle Vue con `npm run build`.
  - Documentación actualizada en `API.md`, `10-API-ENDPOINTS.md`, `ARCHITECTURE.md` y `08-FRONTEND.md`.

### Fixed (2026-09-08)
- **Acceso y privilegios del panel de administración para superusuarios (`is_superuser`)** (ADR-020):
  - Solucionado el problema donde un superusuario (`is_superuser=True`) con `is_staff=False` era tratado como usuario normal y redirigido al marketplace en lugar del panel de administración.
  - `apps/usuarios/controllers/auth_controller.py`: `LoginView.post` ahora evalúa `user.is_staff or user.is_superuser` para redirigir a `usuarios:admin_usuarios_list`.
  - `config/urls.py`: `home_redirect` ahora redirige a `usuarios:admin_usuarios_list` para `request.user.is_staff or request.user.is_superuser`.
  - `apps/usuarios/controllers/admin_usuarios_controller.py`: Decorador `_require_staff` permite acceso a usuarios con `is_staff` o `is_superuser`.
  - `apps/usuarios/models/profile_model.py`: Métodos `has_perm` y `has_module_perms` reconocen `self.is_superuser`.
  - `apps/inventario/controllers/producto_controller.py`: Permisos de moderación y gestión de productos extienden soporte a `is_superuser`.
  - `frontend/src/layout/NavbarApp.vue`: Muestra opciones administrativas cuando `user.is_staff || user.is_superuser` y bundle recompilado con `npm run build`.
  - `templates/base.html`: Parámetros de versión actualizados a `?_v=20260908_1` para invalidar la caché persistente del navegador sobre `layout.js` y `style.css`.
  - BD: Actualizadas banderas `is_staff=True` e `is_superuser=True` en la cuenta de desarrollo `samupe2903@gmail.com` y verificado `agrosft84@gmail.com`.
  - Plantillas actualizadas (`listar_productos.html`, `Productosdetalles.html`, `producto_detail.html`) para permitir acciones de moderación y edición a superusuarios.

### Changed (2026-09-08)
- **Navbar específico para administradores (`is_staff`)** (ADR-019):
  - El navbar único (`frontend/src/layout/NavbarApp.vue`) ahora muestra una rama propia para staff con **solo los 5 módulos del panel de administración**: Usuarios, Categorías, Moderación, Estadísticas y Auditoría (además del dropdown de usuario). Los usuarios no-staff conservan su navegación normal (Inicio, Mi Inventario, Clientes, Ventas, Solicitudes, Mis Compras, carrito).
  - `core/context_processors.py`: `layout_data` ahora expone las URLs admin en el JSON (`urls.admin_usuarios`, `urls.admin_categorias`, `urls.admin_moderacion`, `urls.admin_estadisticas`, `urls.admin_auditoria`) a través del helper `_url()`.
  - Frontend recompilado (`npm run build` → `static/dist/layout.js`).
  - Verificación: test client con el admin (`agrosft84@gmail.com`) → `is_staff=true` + las 5 URLs admin presentes en `#layout-data`; usuario no-staff simulado → `is_staff=false`, mantiene las URLs de usuario.

### Changed (2026-09-08)
- **Redirección post-login por rol** (ADR-018):
  - `apps/usuarios/controllers/auth_controller.py`: `LoginView.post` ahora redirige a los usuarios `is_staff` a `usuarios:admin_usuarios_list`, mantiene la precedencia de `?next=` y deja el fallback en `inventario:marketplace` para el resto de usuarios.
  - Documentación actualizada: `API.md`, `10-API-ENDPOINTS.md`, `04-MODULO-USUARIOS.md` y `DECISIONS.md` (ADR-018).

### Fixed (2026-09-08)
- **Corregidas etiquetas de plantilla Django rotas por saltos de línea** (TemplateSyntaxError en varias vistas):
  - Un auto-formateador partió etiquetas `{% if %}`, `{% endif %}`, `{% endfor %}` y variables `{{ }}` en varias líneas; Django no admite etiquetas multi-línea, lo que producía `TemplateSyntaxError` (`Invalid block tag`) o fuga de sintaxis cruda a la interfaz.
  - Archivos corregidos (etiqueta unida a una sola línea): `apps/usuarios/templates/usuarios/login.html`, `registro.html`, `perfil.html`, `password_reset_form.html`, `password_reset_confirm.html`, `aceptar_terminos.html`, `historial_terminos.html`, `terminos.html` e `apps/inventario/templates/inventario/producto_list.html` y `marketplace.html`.
  - Verificación: las 46 plantillas del proyecto compilan correctamente vía `loader.get_template(...)` (0 errores) y el escaneo de etiquetas multi-línea reporta 0 coincidencias.
  - Prevención: creado `.vscode/settings.json` que desactiva `formatOnSave`/formateo para HTML y `django-html`, de modo que el formateador del IDE no vuelva a partir etiquetas de plantillas Django.

### Added (2026-09-08)
- **Botón y acceso bidireccional para generación de facturas en el módulo "Ventas"** (ver [[DECISIONS#ADR-015]], [[REQUIREMENTS#RF-V20]], [[USER_STORIES#US-16]]):
  - `apps/ventas/templates/ventas/venta_list.html`: Incorporado botón "Factura" con diseño uniforme a "Mis Compras" (`btn-sm btn-success rounded-pill` con ícono `fas fa-file-invoice-dollar` y enlace a `facturacion:generar_factura_pedido`).
  - `apps/ventas/templates/ventas/venta_detail.html`: Incorporado botón "Generar Factura" en el encabezado de detalle de la venta.
  - `apps/ventas/templates/ventas/solicitudes/solicitud_list.html` y `solicitud_detail.html`: Removido botón preliminar de facturación en solicitudes para concentrar la emisión en transacciones concretadas en Ventas.
  - `apps/facturacion/controllers/factura_controller.py`: Modificada la lógica de autorización en `generar_factura_pedido`, `generar_pdf_factura` y `detalle_factura` para habilitar el acceso tanto al comprador como al vendedor del movimiento (o staff), evitando error 404 al vendedor.
  - `apps/facturacion/services/factura_service.py`: `obtener_o_crear_factura_desde_movimiento` optimizado para buscar la factura por `movimiento` (garantizando una única factura por transacción) y fijar al comprador como titular del comprobante.

### Fixed (2026-09-08)
- **Corrección de renderizado de iconos FontAwesome en la vista de inicio de sesión (`login.html`)**:
  - Eliminada la regla universal `.auth-page * { font-family: 'Inter' }` que sobreescribía la familia tipográfica de Font Awesome convirtiendo los iconos (checks del hero, sobre de email, candado de contraseña, ojo del toggle y flecha de inicio de sesión) en cuadros vacíos (`□`).
  - Añadida regla de aislamiento y especificidad reforzada para selectores `.fa, .fas, .far, .fab` asegurando el mapeo correcto de glifos sin alterar la lógica de formularios, botones ni eventos de contraseña.

### Changed (2026-09-08)
- **Ajuste de diseño del banner principal en Marketplace (`marketplace.html`)**:
  - Eliminado el margen/padding superior y lateral (`main.container-fluid`) para que el recuadro verde del hero (`.mp-hero`) quede perfectamente continuo y al ras del borde inferior del navbar (`border-radius: 0; padding-top: 0;`), cubriendo de borde a borde sin separación.

### Changed (2026-09-07)
- **Imágenes aún más ligeras y pequeñas (máx. 400×400 px)**:
  - `core/utils/helpers.py`: `MAX_IMAGE_DIMENSION` 600 → **400** (mantiene nitidez en cards de 220 px y detalle ≤460 px). Compresión reforzada en `resize_uploaded_image()`: PNG → paleta de 256 colores con `quantize()` + `optimize=True`; JPEG → `quality=72, progressive, optimize`; WEBP → `quality=72, method=6`. Resultado: pesos ≈ 5–87 KB (antes 0,3–2 MB).
  - Cache-busting: nuevo `image_cache_bust()` y `IMAGE_VERSION = '20260907'`; se aplica a las URLs de imagen en `Producto.get_imagenes()` (cubre marketplace, inventario, detalle Vue y server) y `listar_productos_api`; tarjeta de relacionados usa `?v=20260907` en línea. Obliga al navegador a descartar las versiones viejas (los archivos re-codificados conservan el mismo nombre/ruta).
  - Vista de detalle (`Productosdetalles.html`): galería `.pdg-wrapper` compacta — `max-width: 460px`, `height: 340px`, centrada — para que el producto no ocupe todo el ancho de la columna.
  - Backfill ejecutado: las 10 imágenes referenciadas en BD re-codificadas a ≤400 px (idempotente, 0 errores).

### Changed (2026-09-07)
- **Optimización del redimensionado de imágenes → `ResizableImageField`** (supersede el `save()` de modelos):
  - `core/models/resizable_image.py`: nuevo `ResizableImageField` con `attr_class = ResizableImageFieldFile` que intercepta `FieldFile.save()` (invocado desde `FileField.pre_save`) y aplica `resize_uploaded_image()` **antes** de persistir, por lo que el original grande nunca se escribe en `MEDIA_ROOT`. Se eliminan los `save()` sobrescritos de `Producto`, `ProductoImagen` y `UserProfile`; sus campos pasan a `ResizableImageField`.
  - `apps/inventario/management/commands/redimensionar_imagenes.py`: management command `redimensionar_imagenes` que reprocesa **en su lugar** (sin cambiar rutas en BD, `storage.delete` + `storage.save`) las imágenes ya almacenadas mayores de 600 px en productos y perfiles. Ejecutado el 2026-09-07: 9 imágenes referenciadas procesadas (idempotente, 0 daños).
  - Fix de bug en `core/utils/helpers.py`: `resize_uploaded_image()` ahora hace `buffer.seek(0)` antes de construir el `InMemoryUploadedFile` (sin esto, `.read()` del resultado devolvía `b''`). Durante el primer backfill se detectó el archivo vacío resultante y se recuperó el contenido original desde git antes de re-ejecutar.

### Changed (2026-09-07)
- **Redimensionado automático de imágenes con Pillow (máx. 600×600)**:
  - `core/utils/helpers.py`: nuevo helper `resize_uploaded_image()` + constante `MAX_IMAGE_DIMENSION = 600`. Usa `Image.thumbnail()` con `LANCZOS` (preserva relación de aspecto, nunca agranda), normaliza a JPEG/PNG/WEBP, convierte RGBA→RGB solo cuando el destino es JPEG y guarda con `quality=85, optimize=True`. Devuelve `None` si la imagen ya cumple el límite (sin re-codificar) o si el archivo no es procesable (el guardado original se conserva).
  - `apps/inventario/models/producto.py`: sobrescrito `save()` en `Producto` y `ProductoImagen` para redimensionar la imagen recién asignada antes de guardarla (detectada vía `_committed`; no reprocesa archivos ya almacenados en saves sin cambio de imagen).
  - `apps/usuarios/models/profile_model.py`: sobrescrito `save()` en `UserProfile` con el mismo patrón para `imagen_perfil`.
  - Frontend: fallbacks server-side alineados con el patrón de las cards Vue — `<img>` envuelto en `.image-wrapper` y con `loading="lazy"` en `apps/inventario/templates/inventario/marketplace.html` y `producto_list.html`. Assets recompilados (`npm run build` → `static/dist/`).
  - Impacto: imágenes de alta resolución ya no se sirven crudas; peso y tiempos de carga reducidos sin deformar las tarjetas (CSS de cards ya usaba alto fijo + `object-fit: cover` — ver ADR-013/ADR-014).

### Changed (2026-09-07)
- **Sincronización de documentación SDD con el código real** (ADR-016, ADR-017):
  - Documentado el módulo **Facturación** (`apps.facturacion`, tablas `factura`/`item_factura` gestionadas por migraciones Django — excepción a la regla `managed = False`):
    - `ARCHITECTURE.md` (+ sección 2.6 con diagrama y flujo), `02-ARQUITECTURA.md`, `DATABASE.md` (+ secciones 2.12/2.13), `03-BASE-DATOS.md`, `API.md` (+ sección 5), `10-API-ENDPOINTS.md` (+ sección `/facturacion/`), `00-INDEX.md`, `PROJECT_CONTEXT.md`, `01-VISION-GENERAL.md`, `ROADMAP.md` (2.4), `12-BRECHAS-Y-ROADMAP.md` (doc. comerciales ✅) y `DECISIONS.md` (ADR-016).
  - **Versión real de Django corregida a 5.0.14** (docs decían 6.0.2): `PROJECT_CONTEXT.md`, `00-INDEX.md`.
  - **`SESSION_ENGINE` documentado como `signed_cookies`** (era `cache`): `ARCHITECTURE.md`, `02-ARQUITECTURA.md`.
  - **Layout corregido**: se documenta el montaje real de `NavbarApp.vue` (+`#vue-navbar`) y `FooterApp.vue` (+`#vue-footer`) desde `frontend/src/layout/main.js`; se elimina la referencia inexistente a `LayoutApp.vue`.
  - **Rutas faltantes documentadas**: sección "Panel de Administración de Usuarios" (16 rutas staff) en `API.md` (1.7) y `10-API-ENDPOINTS.md`; rutas `inventario/venta-directa/`, `ventas/compras/`, `venta_marcar_vendida/`, `venta_cancelar/`.
  - **Carrito corregido a `Auth: Sí`** en ambos docs de API (ADR-015: todas las vistas del carrito requieren `@login_required`); descripción de `home` corregida (redirige según estado).
  - **Totales actualizados**: 68 endpoints en 5 apps; 15 tablas; 17 ADR.
  - **Eliminado `apps/inventario/app.py`** (residuo Flask + SQLite ajeno a Django, código muerto — ADR-017).
  - Ver [[DECISIONS#ADR-016]], [[DECISIONS#ADR-017]].

### Security (2026-09-07)
- **Corregida vulnerabilidad de SQL injection en `tabla_existe()` y `columna_existe()`** (RNF-S09):
  - `apps/usuarios/controllers/auth_controller.py`: funciones `tabla_existe()` y `columna_existe()` reescritas para usar `information_schema` con **queries completamente parametrizadas** (`%s`), eliminando los f-strings inseguros (`SELECT 1 FROM {table}`, `DESCRIBE {table}`).
  - `apps/usuarios/backends.py`: métodos `tabla_existe()` y `columna_existe()` del backend de autenticación reescritos con la misma técnica parametrizada.
  - `scripts/validate_schema.py`: función `get_table_columns()` reescrita para usar `information_schema.columns` con `%s`.
  - Se reemplazaron los `except:` vacíos por `except Exception:` para evitar enmascarar errores.
  - Ver [[DECISIONS#ADR-015]].

### Security (2026-09-07)
- **Agregado `@login_required` a 4 vistas de carrito sin protección** (RNF-S02):
  - `apps/ventas/controllers/carrito_controller.py`: `detalle_carrito()`, `agregar_al_carrito()`, `actualizar_carrito()`, `eliminar_del_carrito()` ahora requieren usuario autenticado. Redirigen a `usuarios:login` (LOGIN_URL ya configurado).

### Removed (2026-09-07)
- **Eliminada clase `TemporalUsuario` (código muerto peligroso)**:
  - `apps/usuarios/models/profile_model.py`: eliminada la clase cuyo método `check_password()` siempre retornaba `True` y exponía una contraseña hardcodeada (`"temp_password"`). No tenía imports ni instanciación en todo el proyecto.
- **Eliminados modelos obsoletos** ([[DATABASE#4. Tablas Obsoletas]]):
  - `apps/ventas/models/solicitud.py` (SolicitudCompra, DetalleSolicitudCompra): eliminado.
  - `apps/ventas/models/venta.py` (Venta, DetalleVenta): eliminado.
  - `apps/ventas/forms/solicitud_form.py`: eliminado (form huérfano).
  - `apps/ventas/forms/venta_form.py`: eliminado (form huérfano).
  - `apps/ventas/models/__init__.py`: limpiadas referencias comentadas.
  - `apps/ventas/forms/__init__.py`: ahora exporta solo `CalificacionForm`.

### Changed (2026-09-07)
- **Consolidado modelo duplicado `TipoMovimiento`**:
  - `apps/inventario/models/producto.py`: eliminada la definición duplicada de `TipoMovimiento`. Ahora `apps.inventario.models` re-exporta el canónico desde `apps.ventas.models.movimiento`.
  - `apps/inventario/admin.py`: import de `TipoMovimiento` redirigido a `apps.ventas.models.movimiento`.
  - `scripts/asegurar_tipos_movimiento.py`: import actualizado a la fuente canónica.
- **Agregado `managed = False` a modelo `Cliente`**:
  - `apps/clientes/models/cliente.py`: el modelo ahora declara `managed = False` para evitar que Django intente crear/modificar la tabla `clientes` (schema legacy gestionado externamente).

### Removed (2026-09-07)
- **Eliminado `scripts/crear_tabla_producto_imagenes.sql`**: el script se retiró del repositorio (el schema de `tblproducto_imagenes` se gestiona directamente en MariaDB). Nota: la tabla debe existir en BD para que funcione el carrusel; referencias actualizadas en `DECISIONS#ADR-014` y `03-BASE-DATOS`.

### Changed (2026-09-07)
- **Sincronización de documentación SDD con el estado real del código** (tras revisión completa del proyecto):
  - `REQUIREMENTS.md`: RF-U08 (recuperación de contraseña) marcado como ✅ Implementado (Brevo); nuevo requisito **RF-I16** (galería/carrusel de múltiples imágenes); corregida referencia GAP-02 → ADR-013/ADR-014.
  - `USER_STORIES.md`: nueva historia **US-16** (galería de múltiples imágenes con carrusel); resumen actualizado (16 completadas, RF-U08 ya no parcial).
  - `ARCHITECTURE.md`: añadido modelo `ProductoImagen` y tabla `tblproducto_imagenes` en la sección de inventario.
  - `DATABASE.md`: añadida relación `tblproducto_imagenes` al diagrama ER.
  - `API.md`: documentados los endpoints de recuperación de contraseña (`/usuarios/password-reset/...`), campo `imagenes[]` en respuestas de inventario/marketplace y carga múltiple en crear/editar producto; totales actualizados.
  - `ROADMAP.md`: password reset y galería/carrusel marcados como completados; corregidas referencias ADR.
  - `00-INDEX.md`: cifras actualizadas (47 RF, 27 RNF, 16 historias, 13 tablas, 14 ADR, 44 endpoints documentados / 63 rutas registradas).
  - `03-BASE-DATOS.md`: tablas `user_profiles`, `user_devices`, `user_addresses` corregidas como existentes en MariaDB; añadida tabla `tblproducto_imagenes` y ER.
  - `08-FRONTEND.md`: entrada `layout`/`LayoutApp.vue`, carrusel de imágenes, botón "Venta Directa" eliminado del carrito.
  - `05-MODULO-INVENTARIO.md`: campo `imagen` múltiple en `ProductoForm`, modelo `ProductoImagen`, flujos crear/editar con galería.
  - `04-MODULO-USUARIOS.md`: recuperación de contraseña documentada como implementada; rutas completas del flujo; `historial/` sigue activo (enlaces UI removidos).
  - `10-API-ENDPOINTS.md`: añadido `imagenes[]` a la respuesta AJAX de inventario/marketplace.
  - `12-BRECHAS-Y-ROADMAP.md`: password reset y galería/carrusel marcados como resueltos.

### Added (2026-09-04)
- **Homologación de tamaño de imágenes y soporte de carrusel de múltiples imágenes** (ver [[DECISIONS#ADR-014]]):
  - `scripts/crear_tabla_producto_imagenes.sql` [NEW]: Script SQL idempotente para la creación de la tabla `tblproducto_imagenes`.
  - `apps/inventario/models/producto.py`: Nuevo modelo `ProductoImagen` y método `get_imagenes()` en `Producto` para consolidar todas las imágenes disponibles.
  - `apps/inventario/forms/producto_form.py`: Soporte de carga múltiple en el campo `imagen` (`multiple=True`).
  - `apps/inventario/controllers/producto_controller.py`: Guardado de múltiples archivos de imagen en `crear_producto`/`editar_producto` y serialización del arreglo `imagenes` para el frontend.
  - `frontend/src/inventario/InventarioApp.vue` y `frontend/src/marketplace/MarketApp.vue`: Contenedores de imagen estandarizados a 220px con `object-fit: cover` e integración de carrusel interactivo con flechas de navegación, dots indicadores y contador de fotos.
  - `apps/inventario/templates/inventario/producto_form.html`: Galería de fotos actuales y previsualización interactiva de nuevas imágenes seleccionadas.
  - `apps/inventario/templates/inventario/Productosdetalles.html`: Carrusel principal responsive con tira de miniaturas interactivas.
  - Recompilación de bundles frontend mediante Vite (`npm run build`).

### Fixed (2026-09-04)
- **Corrección integral de dimensionamiento de imágenes y funcionamiento de carruseles**:
  - `frontend/src/style.css`: Incorporadas al archivo CSS global las clases `.product-image-container` (altura fija de 220px), `.product-image`, `.object-fit-cover`, `.image-wrapper`, estilos de botones de carrusel `.carousel-nav-btn`, dots y badges de conteo.
  - `apps/inventario/templates/inventario/Productosdetalles.html`: Implementada galería interactiva y carrusel independiente con altura estandarizada de 380px, `object-fit: cover`, botones de navegación anterior/siguiente, contador de fotos, miniaturas seleccionables con borde de activación y soporte visual para productos relacionados.
  - `frontend/src/inventario/InventarioApp.vue` y `frontend/src/marketplace/MarketApp.vue`: Corregida la reactividad en el cambio de índice activo (`activeIndexes`) para garantizar la transición instantánea entre fotos al hacer clic en flechas o dots.
  - `frontend/src/inventario/main.js` y `frontend/src/marketplace/main.js`: Eliminado automáticamente el contenedor de fallback al montar la aplicación Vue para evitar duplicación de tarjetas.
  - `apps/inventario/controllers/producto_controller.py`: Corregido el guardado de imágenes secundarias para evitar registrar URLs duplicadas de la foto principal en el carrusel.
  - `apps/inventario/views/producto_views.py`: Contexto de detalle de producto enriquecido con la lista de imágenes para renderizado directo sin bloqueos.
  - Recompilación completa de assets (`npm run build`).
- **Corrección de compatibilidad con carga múltiple en formularios Django y sintaxis en plantilla de detalle**:
  - `apps/inventario/forms/producto_form.py`: Definidos `MultipleFileInput` y `MultipleFileField` con `allow_multiple_selected = True` para evitar la excepción `ValueError: FileInput doesn't support uploading multiple files` generada por Django al recibir `multiple=True`.
  - `apps/inventario/templates/inventario/Productosdetalles.html`: Corregida la sintaxis del tag Django para la llamada de miniatura (`{{ forloop.counter0 }}`).
- **Corrección de errores y validación completa en "Cambiar Contraseña" (`cambiar_password.html`)**:
  - `apps/usuarios/controllers/auth_controller.py`: Implementado `update_session_auth_hash(request, request.user)` para evitar el cierre involuntario de sesión tras el cambio exitoso de contraseña.
  - `apps/usuarios/controllers/auth_controller.py`: Añadidas las validaciones de negocio en el backend (mínimo 8 caracteres, no solo números, y contraseña diferente a la actual).
  - `apps/usuarios/templates/usuarios/cambiar_password.html`: Corregido el color de sombra en foco (cambiado de azul a verde bosque `rgba(60, 141, 60, 0.15)`), mejorado el estilo de alertas de error y añadido script de validación client-side en tiempo real.

### Changed (2026-09-04)
- **Homologación de colores en los apartados "Registrarse" y "Seguridad" al color verde bosque de "Mi Perfil" (`var(--primary-color)`)**:
  - `apps/usuarios/templates/usuarios/registro.html`: Actualizado el degradado del encabezado y sombras de botones al color principal `linear-gradient(135deg, var(--primary-color) 0%, var(--primary-dark) 100%)`.
  - `apps/usuarios/templates/usuarios/cambiar_password.html`: Actualizado el encabezado y el botón principal del apartado "Seguridad" para usar el mismo tema de color verde de "Mi Perfil".
  - Recompilación de assets frontend con Vite (`npm run build`).

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

> ✅ Completado (2026-06-30): backend de password reset con envío real de email vía Brevo.

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
