# DECISIONS.md — AgroSFT

> Registro de Decisiones Técnicas (ADR — Architecture Decision Records).  
> Cada decisión documenta el contexto, la opción elegida y las consecuencias.

---

## ADR-001: Base de Datos Legacy con `managed = False`

**Fecha**: Pre-proyecto (heredado)  
**Estado**: Aceptada

### Contexto

El proyecto AgroSFT se construye sobre una base de datos MariaDB 10.4 preexistente. El schema fue diseñado y creado externamente antes de la implementación del backend Django.

### Decisión

Todos los modelos Django usan `managed = False` y `MIGRATION_MODULES = {app: None}`. Django actúa únicamente como capa de lectura/escritura sobre tablas existentes, sin capacidad de modificar el schema.

### Consecuencias

- ✅ No hay riesgo de que Django modifique accidentalmente la estructura de la BD
- ✅ Permite evolución independiente del schema y del código
- ❌ No se pueden usar migraciones de Django para versionar cambios de schema
- ❌ Los cambios de schema deben hacerse manualmente en MariaDB
- ❌ `makemigrations` y `migrate` no funcionan para las apps personalizadas

---

## ADR-002: Stock Gestionado por Trigger de BD

**Fecha**: Pre-proyecto (heredado) — **Última actualización**: 2026-06-24  
**Estado**: Aceptada (evolucionado)

### Contexto

La base de datos incluye triggers que gestionan automáticamente el stock y calificaciones. Originalmente existía solo `trg_actualizar_stock_oferta` que descontaba stock en toda inserción. El 2026-06-17 se modificó el flujo:

1. Se separó la lógica de calificación en 3 triggers independientes (INSERT, UPDATE, DELETE)
2. Se modificó `trg_actualizar_stock_oferta` para ignorar movimientos tipo `'compra'`
3. Se agregó `trg_descontar_stock_vendida` que descuenta stock solo al marcar `'vendida'`

### Decisión

Los triggers son la única fuente de verdad para:
- Actualizar `cantidad` en `tblproductos_has_tblusuarios` (stock)
- Recalcular `calificacion_promedio` en operaciones INSERT/UPDATE/DELETE

El código Python **NUNCA** debe actualizar estos campos manualmente.

### Consecuencias

- ✅ Consistencia garantizada a nivel de BD (independiente del código)
- ✅ Evita condiciones de carrera en actualizaciones concurrentes
- ✅ El stock ya no se descuenta en solicitudes de compra (`'compra'`), solo al confirmar (`'vendida'`)
- ❌ Lógica de negocio invisible en el código Python
- ❌ Difícil de depurar sin acceso a la definición del trigger
- ❌ Testing requiere BD real (no se puede mockear fácilmente)

### Evolución

| Fecha | Cambio | Trigger |
|---|---|---|
| Original | Stock se descuenta en TODA inserción | `trg_actualizar_stock_oferta` |
| 2026-06-17 | `'compra'` ya no descuenta stock. Stock solo descuenta en `'vendida'` | `trg_actualizar_stock_oferta` (modificado) + `trg_descontar_stock_vendida` (nuevo) |
| 2026-06-17 | Calificación separada en 3 triggers | `trg_actualizar_calificacion_promedio`, `_update`, `_delete` |

---

## ADR-003: Módulo de Solicitudes en JavaScript Puro (Sin BD)

**Fecha**: 2026-06-17  
**Estado**: Reemplazada por ADR-012

### Contexto

El usuario solicitó que el módulo de solicitudes funcione completamente en JavaScript, sin conexión a la base de datos y sin necesidad de registrar solicitudes reales.

### Decisión (Original)

Refactorizar `SolicitudApp.vue` para:
1. No usar `fetch()` hacia endpoints Django
2. No requerir `csrf.js` ni tokens CSRF
3. Operar completamente sobre estado Vue reactivo
4. Cargar datos desde JSON inyectado por Django (si existe) o datos mock locales (fallback)
5. Simplificar `main.js` para montar sin props

### Consecuencias (Originales)

- ✅ El componente funciona de forma autónoma sin backend
- ✅ Ideal para demostraciones y pruebas de UI
- ✅ No requiere configuración de BD para desarrollo frontend
- ❌ Los cambios de estado no persisten (se pierden al recargar la página)
- ❌ Desconexión entre frontend y backend para este módulo

### Archivos Afectados (Originales)

- `frontend/src/solicitudes/SolicitudApp.vue` — Refactorizado a Vue puro
- `frontend/src/solicitudes/main.js` — Simplificado sin props
- `apps/ventas/controllers/solicitud_controller.py` — Backend mantiene endpoints pero frontend no los usa

---

## ADR-004: Carrito Basado en Sesión (Sin Tabla Propia)

**Fecha**: Pre-proyecto  
**Estado**: Aceptada

### Contexto

El carrito de compras necesita persistir items entre requests sin crear una tabla dedicada.

### Decisión

Usar la sesión de Django (`request.session['carrito']`) como almacenamiento del carrito. La sesión se almacena en `LocMemCache` (caché en memoria).

### Consecuencias

- ✅ Sin overhead de tabla adicional en BD
- ✅ Performance alta (lectura/escritura en memoria)
- ❌ Los carritos se pierden si el servidor se reinicia
- ❌ No funciona con múltiples workers (cada worker tiene su propia memoria)
- ❌ Limitado a un solo servidor en producción

### Alternativa Futura

Para producción multi-servidor, migrar a `SESSION_ENGINE = 'django.contrib.sessions.backends.redis'`.

---

## ADR-005: Convención de Cantidades Negativas en Movimientos

**Fecha**: Pre-proyecto (heredado)  
**Estado**: Aceptada

### Contexto

La tabla `tblproductos_has_tblusuarios_has_movimiento` almacena la cantidad movida en cada transacción.

### Decisión

- **Cantidad positiva**: Entrada de stock (abastecimiento, reposición)
- **Cantidad negativa**: Salida de stock (venta, compra por cliente)

El trigger de BD suma algebraicamente la cantidad al stock actual.

### Consecuencias

- ✅ Un solo campo para todos los tipos de movimiento
- ✅ El trigger calcula stock automáticamente con suma simple
- ❌ Confuso para desarrolladores nuevos (usar `abs()` para mostrar)
- ❌ Los totales de venta requieren `abs(cantidad) * precio`

---

## ADR-006: SPA Parcial con Vue 3 + Vite

**Fecha**: Pre-proyecto  
**Estado**: Aceptada

### Contexto

El proyecto necesita interactividad rica en ciertas páginas (marketplace, carrito, inventario) sin convertirse en una SPA completa.

### Decisión

Usar componentes Vue 3 aislados montados en divs específicos dentro de templates Django. Los datos iniciales se inyectan como JSON en `<script>` tags. Vite compila cada componente como entry point independiente.

### Consecuencias

- ✅ Mejor UX donde se necesita (filtros reactivos, AJAX)
- ✅ No requiere reescribir todo el frontend
- ✅ SEO amigable (contenido inicial renderizado por Django)
- ❌ Complejidad de integración (JSON inyectado, CSRF en fetch)
- ❌ No hay router Vue ni estado global compartido

---

## ADR-007: Backend de Autenticación Personalizado

**Fecha**: Pre-proyecto  
**Estado**: Aceptada

### Contexto

La tabla `tblusuarios` tiene estructura personalizada (correo como username, campo `contraseña` con tilde) que no es compatible con `django.contrib.auth` estándar.

### Decisión

Crear `TblusuariosAuthBackend` que autentica manualmente contra la tabla `tblusuarios` usando `check_password` de Django.

### Consecuencias

- ✅ Compatible con la estructura de BD existente
- ✅ Permite usar `request.user`, `@login_required`, etc.
- ❌ No se benefician de features built-in de Django auth
- ⚠️ Vulnerabilidad: `tabla_existe()` usa f-strings en SQL (ver [[ROADMAP#Fase 1]])

---

## ADR-008: Documentación con Obsidian y Wikilinks

**Fecha**: 2026-06-17  
**Estado**: Aceptada

### Contexto

El proyecto necesita una base de conocimiento completa para que cualquier desarrollador o IA pueda entenderlo.

### Decisión

Usar formato Markdown con sintaxis de Obsidian (`[[wikilinks]]`, callouts `> [!note]`, diagramas Mermaid) en carpeta `docs/`.

### Consecuencias

- ✅ Navegación intuitiva con graph view de Obsidian
- ✅ Referencias cruzadas automáticas
- ✅ Diagramas renderizados nativamente
- ❌ Requiere Obsidian para experiencia óptima (aunque Markdown es portable)

---

---

## ADR-010: Paleta de Colores "Raíz y Confianza"

**Fecha**: 2026-06-24  
**Estado**: Aceptada

### Contexto

La interfaz de AgroSFT utilizaba una paleta de colores genérica basada en azul profesional (#2563eb), verde esmeralda (#059669) y ámbar (#d97706). Se definió una nueva identidad visual con fundamento psicológico para alinear la interfaz con los valores del proyecto: conexión con la tierra, confianza en la transacción y transparencia.

### Decisión

Adoptar la paleta **"Raíz y Confianza"** con los siguientes colores:

| Rol | Color | Hex | Psicología |
|---|---|---|---|
| **Primario** | Verde Fresco | `#3C8D3C` | Crecimiento, vitalidad, frescura agrícola |
| **Secundario** | Naranja Cosecha | `#E8853B` | Cosecha madura, calidez, acción |
| **Acento** | Azul Cielo | `#3A8BC8` | Confianza, transparencia, comunicación |
| **Fondo** | Crema Natural | `#F5F1E8` | Pureza, calidez, artesanal |
| **Texto** | Gris Pizarra Suave | `#3D5245` | Legibilidad, sofisticación rural |
| **Éxito** | Verde Musgo | `#5A9C69` | Confirmación, ciclo de recompensa |
| **Alerta** | Terracota | `#C75B3F` | Urgencia amable, atención sin alarma |
| **Info** | Azul Niebla | `#7BAFD4` | Información, guía sin presión |
| **Rating** | Naranja Reputación | `#E07C3A` | Reputación, excelencia, competencia |

El navbar se mantiene con fondo claro (blanco/blur) con acentos verdes. El panel admin se rebrandea completamente con la nueva paleta.

### Consecuencias

- ✅ Identidad visual coherente con el dominio agrícola
- ✅ WCAG 2.1 AA/AAA en todos los pares de contraste críticos
- ✅ Psicología del color aplicada intencionalmente por contexto de uso
- ❌ Requiere actualización de todos los templates con colores hardcodeados
- ❌ El admin de Django pierde el tema azul profesional estándar

### Archivos Afectados

- `templates/base.html` — Variables CSS, botones, navbar, footer
- `static/admin/css/admin-custom.css` — Rebranding completo
- `templates/admin/base_site.html` — Color de enlace
- `templates/usuarios/admin_usuarios_list.html` — Avatares por rol
- `templates/usuarios/admin_estadisticas.html` — Gradient de card
- `frontend/src/solicitudes/SolicitudApp.vue` — Hover color

---

## ADR-009: Sincronización de Documentación con BD Real

**Fecha**: 2026-06-24  
**Estado**: Aceptada

### Contexto

La documentación SDD original (2026-06-17) fue generada mediante análisis de código, pero contenía discrepancias con la base de datos real alojada en MariaDB vía XAMPP. Se identificaron:

1. **`tipo_movimiento`**: documentados 4 valores, pero la BD real tiene 5 (`cancelada`)
2. **Triggers**: documentados 2, pero la BD real tiene 5 (3 separados para calificación)
3. **Tablas verificadas**: `user_profiles`, `user_devices`, `user_addresses` — se confirmó que **sí existen** en MariaDB con FK `ON DELETE CASCADE` a `tblusuarios`
4. **Flujo de stock**: la descripción indicaba que `compra` descuenta stock, pero el trigger actual ignora `compra` y solo descuenta en `vendida`

### Decisión

Actualizar toda la documentación SDD para reflejar fielmente el estado real de la base de datos MariaDB, marcando claramente:

- Los 5 tipos de movimiento y su significado
- Los 5 triggers activos con sus eventos específicos
- Las tablas que existen solo como modelos Django sin respaldo en BD (SolicitudCompra, Venta, DetalleVenta, DetalleSolicitudCompra)
- Las tablas `user_profiles`, `user_devices`, `user_addresses` confirmadas como existentes en MariaDB
- El flujo real de stock: `compra`/`venta`/`rechazada`/`cancelada` no afectan stock; solo `vendida` descuenta

### Consecuencias

- ✅ La documentación ahora es la fuente única de verdad (principio SDD #1)
- ✅ Desarrolladores e IAs pueden entender la BD real sin acceso a phpMyAdmin
- ✅ Las discrepancias entre código y BD están explícitamente documentadas
- ✅ Las tablas `user_profiles`, `user_devices`, `user_addresses` se confirmaron existentes y funcionales
- ❌ Las tablas `SolicitudCompra`, `Venta`, `DetalleVenta`, `DetalleSolicitudCompra` quedan como modelos obsoletos sin respaldo en BD

### Archivos Afectados

- `docs/DATABASE.md` — Reestructuración completa de triggers, tipos, tablas y flujo de stock
- `docs/ARCHITECTURE.md` — Agregado `cancelada` a tabla de estados
- `docs/USER_STORIES.md` — Agregado `Cancelada` al diagrama de flujo
- `docs/03-BASE-DATOS.md` — Sincronizado con DATABASE.md
- `docs/CHANGELOG.md` — Registro del cambio de documentación

---

## ADR-011: Sesiones por Cookie Firmada (signed_cookies)

**Fecha**: 2026-06-30  
**Estado**: Aceptada

### Contexto

Al intentar iniciar sesión en `/usuarios/login/`, Django lanzaba el error `ProgrammingError: Table 'agrosft.django_session' doesn't exist`. Esto ocurría porque:

1. El backend de sesiones estaba configurado como `django.contrib.sessions.backends.db`
2. La tabla `django_session` nunca fue creada en MariaDB (schema legacy, `managed=False`, migraciones deshabilitadas para apps personalizadas)
3. Django intenta almacenar/recuperar sesiones en esta tabla al llamar a `login()`, específicamente al ejecutar `session.cycle_key()` → `session.create()` → `session.exists()`

### Opciones Consideradas

| Opción | Requisito | Problema |
|---|---|---|
| **Ejecutar `migrate sessions`** | Crear tabla `django_session` en BD | Contradice managed=False y la BD como fuente única de verdad externa |
| **File-based sessions** | Sistema de archivos | Archivos huérfanos sin limpieza automática |
| **Cache-based sessions** | Backend de caché | LocMemCache es volátil (se pierde al reiniciar servidor) |
| **Signed cookie sessions** | Solo SECRET_KEY | Ninguno significativo |

### Decisión

Cambiar a `django.contrib.sessions.backends.signed_cookies`. Los datos de sesión se almacenan íntegramente en la cookie del navegador, firmados criptográficamente con `SECRET_KEY` de Django.

### Consecuencias

- ✅ **Sin dependencia de tabla `django_session`** — el error desaparece sin crear tablas en BD
- ✅ **Sin archivos en disco** — a diferencia de file-based sessions
- ✅ **Persistencia跨 requests** — el navegador conserva la cookie incluso si el servidor se reinicia (a diferencia de LocMemCache)
- ✅ **Seguridad** — los datos están firmados con HMAC, no pueden ser manipulados por el cliente
- ✅ **Google OAuth** — funciona sin cambios (solo almacena `_auth_user_id`, `_auth_user_backend`, `_auth_user_hash` en la cookie)
- ✅ **Carrito en sesión** — datos pequeños (~200 bytes por item) caben en el límite de ~4KB de la cookie

- ❌ **Límite de ~4KB** — si el carrito crece demasiado (50+ items), habría que migrarlo a localStorage del frontend
- ❌ **Sesiones invalidadas al cambiar SECRET_KEY** — todos los usuarios pierden su sesión
- ❌ **No apto para datos sensibles grandes** — los datos viajan en cada request HTTP

### Archivos Afectados

- `config/settings.py` — `SESSION_ENGINE` cambiado de `db` a `signed_cookies`

---

## ADR-012: Reversión de Solicitudes a Renderizado Django Server-Side

**Fecha**: 2026-06-25  
**Estado**: Aceptada

### Contexto

El módulo de solicitudes se había migrado a un componente Vue (`SolicitudApp.vue`) con datos mock y conexión AJAX a Django. Tras evaluar el mantenimiento, la duplicación de lógica y la complejidad añadida, se decidió revertir a la implementación original con templates y controller Django server-side.

### Decisión

Eliminar el módulo Vue de solicitudes (`SolicitudApp.vue`, `solicitudes/main.js`, entrada Vite) y mantener `solicitud_controller.py` + templates server-side como única implementación. Esto reemplaza la decisión ADR-003.

### Consecuencias

- ✅ Menor complejidad — lógica de negocio unificada en Django
- ✅ Eliminación de datos mock — la fuente de datos es la BD real vía el controller
- ✅ Menos código frontend que mantener (1 componente Vue menos)
- ❌ Pérdida de interactividad SPA en esa pantalla (filtros/orden ahora recargan página)

### Archivos Afectados

- `frontend/src/solicitudes/SolicitudApp.vue` — Eliminado
- `frontend/src/solicitudes/main.js` — Eliminado
- `vite.config.js` — Eliminada entrada `solicitudes`
- `apps/ventas/templates/ventas/solicitudes/solicitud_list.html` — Removido montaje Vue

---

## ADR-013: Soporte de Imágenes (Producto y Perfil de Usuario)

**Fecha**: 2026-08-20  
**Estado**: Aceptada

### Contexto

El proyecto requería soportar dos tipos de imágenes: foto de perfil de usuario (`user_profiles.imagen_perfil`) y foto de producto (`tblproducto.imagen`). Se necesitaba definir el mecanismo de almacenamiento, subida, validación y exposición pública de las mismas.

### Consideraciones Clave

1. **Sin migraciones Django**: el proyecto define `MIGRATION_MODULES = {app: None}` para las apps personalizadas y todos los modelos usan `managed = False`. El schema se gestiona externamente en MariaDB. Generar migraciones Django es inviable y violaría la regla de oro del proyecto (ver [[PROJECT_CONTEXT#6]]).
2. **Columnas ya existentes en BD** (verificado en `information_schema` el 2026-08-20):
   - `tblproducto.imagen` → `VARCHAR(255) NULL` (posición 7, tras `descripcion`)
   - `user_profiles.imagen_perfil` → `VARCHAR(255) NULL`
3. **Sin Django REST Framework**: el proyecto usa Django clásico con formularios; no hay serializers ni parsers DRF. Django maneja `multipart/form-data` nativamente pasando `request.FILES` a los formularios.
4. **Validación**: los validators de modelo (`FileExtensionValidator` + `validate_image_size`) no se ejecutan en el flujo de `forms.Form`/`ModelForm.save()`; se deben repetir en los campos de los formularios para que `is_valid()` los aplique.

### Opciones Consideradas

| Opción | Decisión | Motivo |
|---|---|---|
| **Migración Django** | ❌ Rechazada | `MIGRATION_MODULES=None` + `managed=False`; la BD es la fuente de verdad externa |
| **ALTER manual** | ✅ Columnas ya aplicadas | Verificado en `information_schema`; se documenta con script idempotente de referencia |
| **DRF + serializers + parsers** | ❌ No aplica | El proyecto no usa DRF; Django Forms + `request.FILES` cubren el caso |
| **Validación solo en modelo** | ❌ Rechazada | No se ejecuta en el flujo de formularios; se duplicó en los forms |
| **upload_to 'perfiles/'** | ❌ Rechazada | Se conserva `profile_pictures/` existente para no romper rutas previas |

### Decisión

1. **Modelo**: `Producto.imagen` y `UserProfile.imagen_perfil` como `ImageField` con `validators=[FileExtensionValidator(['jpg','jpeg','png','webp']), validate_image_size]`.
2. **Formularios**: replicar los mismos validators en `ProductoForm.imagen` y `PerfilForm.imagen_perfil` para validación server-side real.
3. **Storage**: `MEDIA_URL='/media/'`, `MEDIA_ROOT=BASE_DIR/'media'` (ya configurados); servir media en desarrollo vía `static()` en `config/urls.py`.
4. **BD**: sin cambios — ambas columnas ya existen. Script de referencia idempotente en `scripts/agregar_imagen_producto.sql`.
5. **Templates**: los dicts del controller exponen la URL resuelta (`producto.imagen`); los templates que reciben modelos usan `producto.imagen.url`.

### Consecuencias

- ✅ Fotografías funcionales en marketplace, inventario, detalle y perfil
- ✅ Validación consistente (extensión + 5MB) en servidor (modelo y formulario) y cliente (`accept` + JS)
- ✅ Sin riesgo para triggers de stock/calificación ni FKs existentes
- ❌ `editar_producto` no permite eliminar la imagen (solo reemplazar); pendiente de mejora
- ✅ Compresión/redimensionado con Pillow implementado (2026-09-07): `save()` de `Producto`, `ProductoImagen` y `UserProfile` aplican `img.thumbnail()` a máx. 600×600 px preservando la relación de aspecto (`core/utils/helpers.resize_uploaded_image`); solo se procesan uploads recién asignados (`_committed = False`)
- ✅ Refinado (2026-09-07): el redimensionado se aplica **antes** de persistir mediante `ResizableImageField` / `ResizableImageFieldFile` (`attr_class`), interceptando `FieldFile.save()` que invoca `FileField.pre_save` (`core/models/resizable_image.py`); se eliminan así los `save()` sobrescritos en los modelos
- ✅ Backfill (2026-09-07): management command `manage.py redimensionar_imagenes` reprocesa en su lugar (`storage.delete` + `storage.save`, sin cambiar rutas en BD) las imágenes ya almacenadas en `MEDIA_ROOT` que superen 600 px; ejecutado y verificado idempotente
- ✅ Límite reducido de 600 → **400 px** y compresión reforzada (2026-09-07): PNG a paleta 256 colores (`quantize`), JPEG `quality=72` + progressive, WEBP `method=6` → pesos de ~5–87 KB; cache-busting `?v=20260907` vía `image_cache_bust()` en `get_imagenes()` y la API; galería de detalle compacta (máx. 460 px de ancho)

### Archivos Afectados

- `apps/inventario/models/producto.py` — campo `imagen`
- `apps/usuarios/models/profile_model.py` — campo `imagen_perfil`
- `apps/inventario/forms/producto_form.py` — validators en `imagen`
- `apps/usuarios/forms/auth_forms.py` — validators en `imagen_perfil`
- `apps/inventario/controllers/producto_controller.py` — `request.FILES` y exposición de URL
- `apps/usuarios/controllers/auth_controller.py` — guardado de imagen de perfil
- `core/utils/helpers.py` — `validate_image_size`, `resize_uploaded_image` y `MAX_IMAGE_DIMENSION`
- `core/models/resizable_image.py` — `ResizableImageField` / `ResizableImageFieldFile` (nuevo)
- `apps/inventario/management/commands/redimensionar_imagenes.py` — backfill in-place (nuevo)
- Templates de inventario (`marketplace`, `producto_list`, `producto_detail`) — renderizado de imagen
- `scripts/agregar_imagen_producto.sql` — script de referencia (nuevo)

---

## ADR-014: Homologación de Tamaño de Imágenes y Soporte de Carrusel de Múltiples Imágenes

**Fecha**: 2026-09-04  
**Estado**: Aceptada

### Contexto

Las imágenes cargadas por los usuarios contaban con proporciones dispares y fondos heterogéneos, provocando desalineaciones y alturas desiguales en las tarjetas de producto del inventario y marketplace. Adicionalmente, existía la necesidad de publicar múltiples fotos por producto y explorarlas mediante un carrusel interactivo directamente en cada tarjeta y en la vista de detalle.

### Decisión

1. **Estandarización de Imagen en Tarjetas**: Fijar la altura del contenedor en `220px` con `width: 100%`, `overflow: hidden` y regla `object-fit: cover; object-position: center;`.
2. **Entidad `tblproducto_imagenes`**: Crear tabla relacional `tblproducto_imagenes` para registrar múltiples imágenes por producto, manteniendo `tblproducto.imagen` como portada principal para compatibilidad con código y consultas legacy.
3. **Componente de Carrusel Interactivo**:
   - En `InventarioApp.vue` y `MarketApp.vue`: Navegación con flechas anterior/siguiente (`<` / `>`), dots de posición y contador numérico de fotos con prevención de propagación de eventos (`@click.stop`).
   - En `Productosdetalles.html`: Carrusel principal con tira de miniaturas interactivas.

### Consecuencias

- ✅ Grid de productos uniforme y alineado independientemente de la resolución o proporción original de la imagen
- ✅ Soporte nativo para galerías de fotos por producto con carrusel ágil y responsive
- ✅ Carga múltiple intuitiva con previsualización en el formulario de registro y edición
- ✅ Total compatibilidad con la base de datos MariaDB existente

### Archivos Afectados

- `scripts/crear_tabla_producto_imagenes.sql` [NEW] *(archivo eliminado 2026-09-07; el schema se gestiona directamente en MariaDB)*
- `apps/inventario/models/producto.py` — modelo `ProductoImagen` y método `get_imagenes()`
- `apps/inventario/forms/producto_form.py` — soporte `multiple` en campo `imagen`
- `apps/inventario/controllers/producto_controller.py` — procesamiento de múltiples archivos y array `imagenes`
- `frontend/src/inventario/InventarioApp.vue` — carrusel interactivo en tarjetas
- `frontend/src/marketplace/MarketApp.vue` — carrusel interactivo en tarjetas
- `apps/inventario/templates/inventario/producto_form.html` — previsualización y galería de imágenes
- `apps/inventario/templates/inventario/Productosdetalles.html` — carrusel de detalle con miniaturas

---

## ADR-015: Acceso Bidireccional y Generación de Facturas en Módulo Ventas

### Contexto

El sistema permitía a los compradores generar y descargar facturas PDF desde la vista de "Mis Compras" (`compra_list.html`), pero los vendedores no disponían del botón de generación de factura en su historial de ventas (`venta_list.html` y `venta_detail.html`). Adicionalmente, el controlador `generar_factura_pedido` restringía la consulta a `movimiento.id_usuario == request.user`, lo cual provocaba error 404 al intentar ser consultado por el vendedor, dado que en un movimiento comercial `id_usuario` es el comprador.

### Decisión

1. **Control de Acceso Bidireccional**: Se amplía la validación en `generar_factura_pedido`, `generar_pdf_factura` y `detalle_factura` para permitir el acceso tanto al comprador (`movimiento.id_usuario == request.user`) como al vendedor propietario de los productos asociados a dicho movimiento (`ProductoUsuarioMovimiento` donde `id_producto_usuario.id_usuario == request.user`), además de usuarios administradores (`is_staff`).
2. **Reutilización y Unicidad de Factura**: `FacturaService.obtener_o_crear_factura_desde_movimiento` busca la factura existente asociada al `movimiento` (`Factura.objects.filter(movimiento=movimiento).first()`). Si existe, la reutiliza; si no, la crea asignando al comprador como titular del comprobante contable (`usuario=movimiento.id_usuario`), evitando duplicidad contable entre comprador y vendedor.
3. **Consistencia Visual en Módulo Ventas**: Se incorpora el botón de "Factura" con ícono `fas fa-file-invoice-dollar` y clase `btn-sm btn-success rounded-pill` en el listado de ventas (`venta_list.html`) y en la vista de detalle (`venta_detail.html`), homologando la experiencia visual de "Mis Compras" y manteniéndolo fuera de la fase preliminar de solicitudes.

### Consecuencias

- **Positivas**:
  - El vendedor tiene acceso inmediato al comprobante legal una vez la transacción forma parte de sus ventas registradas.
  - Se mantiene la integridad contable con una sola entidad `Factura` por `Movimiento`.
  - Experiencia de usuario uniforme e intuitiva entre compras y ventas.
- **Negativas / Consideraciones**:
  - Se requiere verificar las relaciones de productos para asegurar que únicamente los participantes autorizados de la transacción tengan acceso.

### Archivos Afectados

- `apps/facturacion/services/factura_service.py`
- `apps/facturacion/controllers/factura_controller.py`
- `apps/ventas/templates/ventas/venta_list.html`
- `apps/ventas/templates/ventas/venta_detail.html`

---

## ADR-015: Eliminación de Vulnerabilidades y Limpieza de Código Muerto (Fase 1)

**Fecha**: 2026-09-07
**Estado**: Aceptada

### Contexto

La Fase 1 del ROADMAP identificó seis tareas de estabilización y seguridad pendientes que comprometían la integridad del sistema y violaban requisitos no funcionales (RNF-S02, RNF-S09).

### Decisiones

1. **Corrección de SQL injection (RNF-S09)**: Se reemplazaron las f-queries inseguras (`SELECT 1 FROM {table}`, `DESCRIBE {table}`) en `tabla_existe()`, `columna_existe()` y `get_table_columns()` por consultas parametrizadas contra `information_schema` (`WHERE table_name = %s`). MySQL/MariaDB no permite parametrizar identificadores (tablas/columnas), por lo que la consulta al catálogo del motor con `%s` es la única forma de lograrlo sin interpolar nombres.
2. **`@login_required` en carrito (RNF-S02)**: Se protegieron las 4 vistas de carrito que carecían de autenticación (`detalle_carrito`, `agregar_al_carrito`, `actualizar_carrito`, `eliminar_del_carrito`).
3. **Eliminación de `TemporalUsuario`**: clase muerta con `check_password()` que siempre retornaba `True` — se eliminó por riesgo de seguridad y ausencia total de uso.
4. **Consolidación de `TipoMovimiento`**: eliminada la definición duplicada en `apps.inventario.models.producto`; se re-exporta el canónico desde `apps.ventas.models.movimiento` (ya documentado como autoridad en [[DATABASE#2.8]]).
5. **Eliminación de modelos obsoletos**: `SolicitudCompra`, `DetalleSolicitudCompra`, `Venta`, `DetalleVenta` y sus forms huérfanos fueron eliminados (tablas inexistentes, sin uso en código).
6. **`managed = False` en `Cliente`**: agregado para alinear el modelo con la política de schema gestionado externamente.

### Consecuencias

- ✅ RNF-S09 y RNF-S02 ahora cumplidos.
- ✅ Menos código (eliminados ~6 archivos obsoletos y una clase peligrosa).
- ✅ Modelo `TipoMovimiento` único y consistente.
- ✅ `Cliente` alineado con la regla de oro `managed = False`.
- ❌ `information_schema` queries son ligeramente más costosas que `DESCRIBE`, pero solo se ejecutan durante login/registro/perfil (no en hot paths).

### Archivos Afectados

- `apps/usuarios/controllers/auth_controller.py`
- `apps/usuarios/backends.py`
- `scripts/validate_schema.py`
- `apps/ventas/controllers/carrito_controller.py`
- `apps/usuarios/models/profile_model.py`
- `apps/inventario/models/producto.py`, `apps/inventario/models/__init__.py`, `apps/inventario/admin.py`
- `apps/ventas/models/__init__.py`, `apps/ventas/forms/__init__.py`, `scripts/asegurar_tipos_movimiento.py`
- `apps/ventas/models/solicitud.py`, `apps/ventas/models/venta.py`, `apps/ventas/forms/solicitud_form.py`, `apps/ventas/forms/venta_form.py` (eliminados)
- `apps/clientes/models/cliente.py`

---

## ADR-016: App de Facturación con Migraciones Django (`managed = True`)

**Fecha**: 2026-09-07
**Estado**: Aceptada

### Contexto

La política del proyecto (ADR-001/ADR-002) establece que todo el schema se gestiona externamente en MariaDB y que los modelos usan `managed = False`. Sin embargo, existe `apps.facturacion` (módulo "Documentos comerciales") cuyas tablas `factura` e `item_factura` **sí** son generadas y gestionadas por migraciones Django (`python manage.py migrate facturacion`), rompiendo esa regla.

Esto es intencional: la app `facturacion` es la única que no depende del schema legacy y sus tablas se crean vía `0001_initial` / `0002_...` en `apps/facturacion/migrations/`. Debe documentarse como excepción explícita para no ser "corregida" por error en futuras limpiezas.

### Decisión

1. **`facturacion` usa migraciones Django (modelos `managed = True`)** en lugar de la regla global `managed = False`. Sus modelos (`Factura`, `ItemFactura`) definen el schema real.
2. **La expulsión de `MIGRATION_MODULES` no aplica a esta app**: es la única app personalizada con migraciones activas.
3. **Regla de oro #1 matizada**: `managed = False` aplica a `usuarios`, `inventario`, `ventas` y `clientes`; `facturacion` es la excepción documentada en [[PROJECT_CONTEXT]], [[ARCHITECTURE#2.6]] y [[DATABASE#2.12]].

### Consecuencias

- ✅ Las tablas `factura` e `item_factura` tienen schema declarativo en Python (versionable y reproducible).
- ✅ El flujo de facturación (crear desde carrito, PDF, historial) queda autocontenido.
- ❌ Conviven dos paradigmas de gestión de schema (externo vs. migraciones), aumentando la complejidad cognitiva; mitigado por esta ADR y los avisos en los docs.

### Archivos Afectados

- `apps/facturacion/models.py`, `apps/facturacion/migrations/0001_initial.py`, `apps/facturacion/migrations/0002_*.py`
- `config/settings.py` (`INSTALLED_APPS` incluye `apps.facturacion`)
- Documentación: [[ARCHITECTURE#2.6]], [[DATABASE#2.12]], [[DATABASE#2.13]], [[PROJECT_CONTEXT]]

---

## ADR-017: Eliminación del Residuo Flask en `apps/inventario`

**Fecha**: 2026-09-07
**Estado**: Aceptada

### Contexto

`apps/inventario/app.py` contenía una app Flask + SQLite aislada al proyecto AgroSFT (marcadores propios, CSS interno, esquema SQLite con `productos`, `usuarios`, `categorias`). Se detectó como **código muerto**: no se importa desde ningún módulo Python del proyecto ni desde los settings de Django; no existe ningún `if __name__ == "__main__"` para ejecutarla como script utilizable.

### Decisión

Eliminar `apps/inventario/app.py` por completo. El inventario del sistema real vive exclusivamente en `apps/inventario` (vistas Django + MariaDB); el archivo FLask era un vestigio de una prueba anterior ajena a la arquitectura.

### Consecuencias

- ✅ Menos código muerto y confusión (la existencia de una app Flask en un proyecto Django podía inducir a error).
- ✅ Sin impacto funcional: nada importa ni ejecuta ese archivo (verificado por búsqueda de imports antes de eliminar).

### Archivos Afectados

- `apps/inventario/app.py` (eliminado)

---

## ADR-018: Redirección Post-Login por Rol (`is_staff`)

**Fecha**: 2026-09-08
**Estado**: Aceptada

### Contexto

`LoginView.post` (`apps/usuarios/controllers/auth_controller.py`) redirigía a todos los usuarios autenticados a `inventario:marketplace`, sin distinguir usuarios administrativos. Un administrador que iniciaba sesión por la pantalla normal no aterrizaba en su panel, y el navbar no exponía acceso directo al panel de administración.

### Decisión

Tras un login exitoso, respetar la URL `?next=` cuando se proporciona; en caso contrario, redirigir a `usuarios:admin_usuarios_list` si `user.is_staff` es `True`, y a `inventario:marketplace` en el resto de casos.

### Consecuencias

- ✅ Los administradores aterrizan directamente en el panel de gestión de usuarios tras iniciar sesión.
- ✅ `?next=` mantiene su precedencia (usado por Django Admin y decoradores `@login_required`).
- ✅ Sin impacto en el flujo de usuarios no-staff.
- ❌ La detección de staff se basa únicamente en `is_staff` (sin granularidad de permisos por módulo).

### Archivos Afectados

- `apps/usuarios/controllers/auth_controller.py` (bloque de redirección de `LoginView.post`)

---

## ADR-019: Navbar Específico para Staff (`is_staff`)

**Fecha**: 2026-09-08
**Estado**: Aceptada

### Contexto

La redirección post-login (ADR-018) llevaba a los administradores a su panel, pero la barra de navegación seguía mostrando los mismos enlaces que un usuario común (Inicio, Mi Inventario, Clientes, Ventas, Solicitudes, Mis Compras, carrito), sin acceso organizado a los módulos de administración. `NavbarApp.vue` es un único componente compartido por todas las páginas vía `base.html`.

### Decisión

`NavbarApp.vue` ramifica su contenido autenticado según `user.is_staff`:
- **staff**: solo los 5 módulos del panel de administración (Usuarios, Categorías, Moderación, Estadísticas, Auditoría) + dropdown de usuario compartido.
- **no-staff**: navegación de usuario actual (Inicio, Mi Inventario, Clientes, Ventas, Solicitudes, Mis Compras, carrito) + dropdown de usuario compartido.

`core.context_processors.layout_data` expone las URLs admin en el JSON `urls` (via `_url()`): `admin_usuarios`, `admin_categorias`, `admin_moderacion`, `admin_estadisticas`, `admin_auditoria`.

### Consecuencias

- ✅ El navbar refleja el rol del usuario: los administradores solo ven los 5 módulos admin, sin enlaces de usuario ni carrito.
- ✅ Un único componente se mantiene (Sin duplicación de navbar); el estado staff se expone desde `layout_data.user.is_staff`.
- ✅ Sin cambios en BD (los roles siguen siendo flags de aplicación, sin validación a nivel de base de datos).
- ❌ La detección sigue siendo binaria (`is_staff`); no hay granularidad por módulo (todos los staff ven los mismos 5 enlaces).

### Archivos Afectados

- `frontend/src/layout/NavbarApp.vue` (rama `v-if="user.is_staff"` / `v-else`)
- `core/context_processors.py` (URLs admin en `layout_data.urls`)
- `static/dist/layout.js` (bundle recompilado)

---

## ADR-020: Acceso al Panel de Administración y Privilegios para Superusuarios (`is_superuser`)

**Fecha**: 2026-09-08
**Estado**: Aceptada

### Contexto

Aunque un usuario tuviera la bandera `is_superuser = True`, si su campo `is_staff` estaba en `False` (o si no contaba con dicha bandera explícita), el sistema lo redirigía post-login al marketplace de usuario común (`inventario:marketplace`), el decorador `_require_staff` denegaba su acceso a las vistas de administración, el método `has_perm` no lo habilitaba, el navbar no mostraba las rutas de administración y `home_redirect` en `/` lo devolvía al marketplace.

### Decisión

Unificar la condición de privilegios administrativos para que tanto `is_staff` como `is_superuser` confieran acceso pleno al panel de administración y sus operaciones asociadas:
1. **Redirección post-login y home**: `auth_controller.py` y `config/urls.py` redirigen a `usuarios:admin_usuarios_list` si `user.is_staff or user.is_superuser`.
2. **Control de acceso**: El decorador `_require_staff` en `admin_usuarios_controller.py` permite la ejecución si `request.user.is_staff or request.user.is_superuser`.
3. **Permisos de modelo**: `Tblusuarios.has_perm` y `has_module_perms` devuelven `True` para usuarios activos con `self.is_staff or self.is_superuser`.
4. **Moderación y gestión de inventario**: `producto_controller.py` y las plantillas (`listar_productos.html`, `Productosdetalles.html`, `producto_detail.html`) admiten superusuarios en aprobación/rechazo y edición global.
5. **Navegación**: `NavbarApp.vue` evalúa `user.is_staff || user.is_superuser` para renderizar la rama con los 5 módulos administrativos.

### Consecuencias

- ✅ Los superusuarios pueden iniciar sesión y acceder inmediatamente al panel de administración sin requerir `is_staff=True` manual.
- ✅ Coherencia total entre backend, decorators, modelos, templates y frontend Vue.
- ✅ Mantiene compatibilidad regresiva con administradores que solo tienen `is_staff=True`.
- ❌ No implementa RBAC granular por permisos específicos; ambos roles comparten acceso a todos los módulos admin.

### Archivos Afectados

- `apps/usuarios/controllers/auth_controller.py`
- `apps/usuarios/controllers/admin_usuarios_controller.py`
- `apps/usuarios/models/profile_model.py`
- `apps/inventario/controllers/producto_controller.py`
- `config/urls.py`
- `frontend/src/layout/NavbarApp.vue`
- `apps/inventario/templates/inventario/listar_productos.html`
- `apps/inventario/templates/inventario/Productosdetalles.html`
- `apps/inventario/templates/inventario/producto_detail.html`

---

## ADR-021: Eliminación del Panel Web de Administración y Unificación de Experiencia

**Fecha**: 2026-09-08
**Estado**: Aceptada (Reemplaza a ADR-018, ADR-019 y ADR-020)

### Contexto

El sistema contaba con un panel de administración web personalizado (`admin_usuarios_controller.py`, vistas de estadísticas, categorías, moderación de productos, reportes y gestión de usuarios) y bifurcaciones de navegación condicional en el navbar para usuarios staff y superusuarios. El requerimiento del proyecto exige eliminar cualquier interfaz o rastro visual de panel administrativo personalizado en la aplicación principal, manteniendo una experiencia uniforme orientada exclusivamente al flujo natural de usuario/marketplace.

### Decisión

1. **Eliminación del Controlador y Rutas Admin**: Se elimina completamente `apps/usuarios/controllers/admin_usuarios_controller.py` y sus correspondientes rutas en `apps/usuarios/urls.py` (`admin-usuarios/`, `admin-categorias/`, `admin-moderacion/`, `admin-estadisticas/`, `admin-reporte/`).
2. **Eliminación de Plantillas Admin**: Se borran las plantillas asociadas en `templates/usuarios/` (`admin_usuarios_list.html`, `admin_usuario_form.html`, `admin_categorias.html`, `admin_categoria_form.html`, `admin_moderacion.html`, `admin_estadisticas.html`).
3. **Unificación de Navegación (NavbarApp.vue)**: Se remueve la rama condicional de staff/superusuario. Todos los usuarios autenticados disponen de la navegación estándar: *Inicio*, *Mi Inventario*, *Clientes*, *Ventas*, *Solicitudes*, *Mis Compras* y *Carrito*.
4. **Redirección Estándar**: `LoginView.post` y `home_redirect` en `/` redirigen a todos los usuarios autenticados al marketplace (`inventario:marketplace`).
5. **Limpieza de Context Processors**: Se retiran del objeto `urls` global de `layout_data` todas las claves `admin_*`.

### Consecuencias

- ✅ Experiencia de usuario uniforme y simplificada; no hay menús paralelos ni paneles secundarios en la interfaz de usuario.
- ✅ Reducción significativa de superficie de código y mantenimiento al eliminar controladores y plantillas no deseadas.
- ✅ Reemplaza y anula las decisiones de redirección y bifurcación previa (ADR-018, ADR-019, ADR-020).
- ✅ El backend Django Admin nativo (`/admin/`) permanece intacto para labores técnicas internas.

### Archivos Afectados

- `apps/usuarios/controllers/admin_usuarios_controller.py` (eliminado)
- `apps/usuarios/urls.py`
- `apps/usuarios/controllers/auth_controller.py`
- `config/urls.py`
- `core/context_processors.py`
- `frontend/src/layout/NavbarApp.vue`
- `templates/base.html`
- `templates/usuarios/admin_*.html` (eliminadas)

---

## ADR-022: Selectores Dinámicos para Categoría y Nombre de Producto en Formulario de Registro

**Fecha**: 2026-09-08  
**Estado**: Aceptada  

### Contexto

En el formulario de registro y edición de productos (`producto_form.html`), la selección de **Categoría** usaba un `<select>` estático derivado del campo `ModelChoiceField` de Django que no permitía agregar nuevas categorías al instante. Por otro lado, el **Nombre del Producto** usaba un campo de texto libre `<input text>` que impedía reutilizar nombres de productos ya registrados en el catálogo.

### Decisión

1. **Selector Dinámico de Categoría**:
   - Se mantiene el modelo y la persistencia de MariaDB (`tblcategoria`).
   - Se agrega el endpoint AJAX `api_crear_categoria` (POST JSON) para la creación de categorías en tiempo real.
   - El selector muestra una opción visual `+ Agregar categoría` que despliega un formulario inline con validación sin recargar la página.
2. **Selector Dinámico de Nombre de Producto**:
   - Se agrega el endpoint AJAX `api_nombres_producto` (GET) que devuelve la lista deduplicada de nombres de productos de la base de datos.
   - El input de texto original se transforma en un `<select>` interactivo que ofrece sugerencias de productos existentes o la opción `+ Agregar nuevo producto` mediante un formulario inline.
3. **Compatibilidad Transparente con Django Form**:
   - No se modificó la clase `ProductoForm` de Django.
   - La selección del usuario se sincroniza mediante JS en campos ocultos que alimentan los nombres de input esperados por Django (`nombre` e `id_categoria`), garantizando que la validación y el guardado del controlador continúen operando exactamente igual.

### Consecuencias

- ✅ Agiliza el registro de productos eliminando la necesidad de navegar a otras pantallas para crear categorías.
- ✅ Favorece la estandarización de nombres en el catálogo de inventario.
- ✅ Cero breaking changes en la persistencia existente o en `ProductoForm`.

### Archivos Afectados

- `apps/inventario/controllers/producto_controller.py`
- `apps/inventario/urls.py`
- `apps/inventario/templates/inventario/producto_form.html`

---

## ADR-023: Tipo de Movimiento 'reabastecimiento' y Stock Gestionado por Trigger

**Fecha**: 2026-09-09  
**Estado**: Aceptada  

### Contexto

El módulo de edición de producto (`editar_producto()`) permitía anteriormente reducir el stock directamente y registraba los cambios con tipo `venta` (abastecimiento legacy), lo que generaba confusión semántica y permitía valores negativos no deseados. El requerimiento era:
1. Impedir la reducción de stock desde la edición (solo reabastecimiento/ingreso).
2. Registrar cada incremento con un tipo semántico propio: `reabastecimiento`.
3. Mantener la regla de oro: **el trigger de BD es la única fuente de verdad para el stock**.

### Decisión

1. **Nuevo tipo de movimiento**: `reabastecimiento` (INSERT en `tipo_movimiento`, script `insertar_tipo_reabastecimiento.sql`).
2. **Trigger actualizado**: `trg_actualizar_stock_oferta` (script `trigger_reabastecimiento_stock.sql`) suma stock para tipos `venta` (legacy abastecimiento) y `reabastecimiento`; ignora `compra`; protege contra stock negativo.
3. **Backend (`editar_producto`)**:
   - Valida server-side: `nuevo_stock >= stock_actual`. Si menor → error y cancelación.
   - Calcula `diferencia = nuevo_stock - stock_actual`.
   - Si `diferencia > 0`: crea `Movimiento(tipo='reabastecimiento')` + `ProductoUsuarioMovimiento(cantidad=+diferencia)`.
   - **No toca** `ProductoUsuario.cantidad` en Python (trigger lo actualiza).
4. **Frontend**: campo `cantidad` como entero (`step="1"`, `min=stock_actual`), validación JS en vivo que impide valores < stock actual.
5. **Formulario**: `initial['cantidad']` casteado a `int` (elimina `.00` visual).

### Consecuencias

- ✅ Semántica clara: `reabastecimiento` = entrada de stock desde edición.
- ✅ Integridad: BD controla stock (trigger), Python solo registra intención.
- ✅ UX: usuario nunca ve decimales en stock; input bloquea reducción.
- ✅ Trazabilidad: cada reabastecimiento queda en historial de movimientos con tipo propio.
- ⚠️ Requiere ejecutar scripts SQL en BD (`insertar_tipo_reabastecimiento.sql` y `trigger_reabastecimiento_stock.sql`) antes de desplegar.

### Archivos Afectados

- `scripts/insertar_tipo_reabastecimiento.sql` (nuevo)
- `scripts/trigger_reabastecimiento_stock.sql` (nuevo)
- `scripts/asegurar_tipos_movimiento.py`
- `apps/inventario/controllers/producto_controller.py`
- `apps/inventario/forms/producto_form.py`
- `apps/inventario/templates/inventario/producto_form.html`
- `docs/REQUIREMENTS.md`, `USER_STORIES.md`, `ARCHITECTURE.md`, `DATABASE.md`, `09-CONFIGURACION.md`, `CHANGELOG.md`

---

## ADR-024: Nombre y Categoría Inmutables en Edición + Fotografía Obligatoria

**Fecha**: 2026-09-09  
**Estado**: Aceptada  

### Contexto

En el módulo de edición de producto se permitía modificar el `nombre` y la `categoría` de un producto ya publicado, lo que podía romper la trazabilidad del catálogo maestro. Adicionalmente, el registro de productos permitía crear publicaciones sin ninguna fotografía, degradando la experiencia del marketplace.

### Decisión

1. **Nombre y categoría inmutables en edición**:
   - En `editar_producto()`, se eliminan las asignaciones `producto.nombre` y `producto.id_categoria` (el backend ya no los sobrescribe).
   - En `producto_form.html`, en modo edición (`accion == 'editar'`) los selectores dinámicos se sustituyen por campos de solo lectura (`disabled readonly`) con el valor actual, manteniendo ocultos `{{ form.nombre }}` y `{{ form.id_categoria }}` para que el formulario siga validando.
2. **Fotografía obligatoria**:
   - `ProductoForm` acepta el kwarg `requerir_imagen` que marca `imagen.required = True`.
   - `MultipleFileField.clean` permite que `required` aplique también a listas vacías (antes devolvía `[]` sin validar).
   - En `crear_producto`, la imagen es **siempre** obligatoria.
   - En `editar_producto`, es obligatoria **solo** si la publicación no tiene imagen (`tiene_imagen == False`).

### Consecuencias

- ✅ Evita cambiar identidad de un producto ya publicado (integridad del catálogo).
- ✅ Garantiza que toda publicación nueva tenga al menos una fotografía.
- ✅ Validación doble: frontend (UI de solo lectura y nota de obligatorio) y backend (required).
- ⚠️ Publicaciones existentes sin imagen seguirán apareciendo hasta que se editen (se les exigirá imagen en el próximo guardado).

### Archivos Afectados

- `apps/inventario/forms/producto_form.py`
- `apps/inventario/controllers/producto_controller.py`
- `apps/inventario/templates/inventario/producto_form.html`
- `docs/REQUIREMENTS.md`, `USER_STORIES.md`, `CHANGELOG.md`

---

## Resumen de Decisiones

| ID | Decisión | Estado | Impacto |
|---|---|---|---|
| ADR-001 | BD legacy con managed=False | Aceptada | Arquitectura completa |
| ADR-002 | Stock por trigger BD | Aceptada (evolucionado) | Todas las transacciones |
| ADR-003 | Solicitudes JS puro | Reemplazada (ADR-012) | Módulo ventas |
| ADR-004 | Carrito en sesión | Aceptada | Módulo carrito |
| ADR-005 | Cantidades negativas | Aceptada | Modelo de datos |
| ADR-006 | SPA parcial Vue+Vite | Aceptada | Frontend completo |
| ADR-007 | Auth backend custom | Aceptada | Seguridad |
| ADR-008 | Docs Obsidian | Aceptada | Documentación |
| ADR-009 | Sincronización docs con BD real | Aceptada | Documentación |
| ADR-010 | Paleta Raíz y Confianza | Aceptada | Frontend / UI |
| ADR-011 | Sesiones por cookie firmada | Aceptada | Sesiones / Auth |
| ADR-012 | Solicitudes server-side (reversión) | Aceptada | Módulo ventas |
| ADR-013 | Soporte de imágenes (producto + perfil) | Aceptada | Inventario / Usuarios |
| ADR-014 | Carrusel de imágenes y tamaño uniforme | Aceptada | Inventario / Marketplace |
| ADR-018 | Redirección post-login por rol (is_staff) | Reemplazada (ADR-021) | Auth / Usuarios |
| ADR-019 | Navbar específico para staff (is_staff) | Reemplazada (ADR-021) | Frontend / Auth |
| ADR-020 | Acceso y privilegios admin para superusuarios (is_superuser) | Reemplazada (ADR-021) | Auth / Admin / Frontend |
| ADR-021 | Eliminación de panel web admin y unificación de experiencia | Aceptada | Arquitectura / UI / Usuarios |
| ADR-022 | Selectores dinámicos para Categoría y Nombre de Producto | Aceptada | Inventario / UI / UX |
| ADR-023 | Tipo 'reabastecimiento' + stock por trigger | Aceptada | Edición inventario + BD |
| ADR-024 | Nombre/Categoría inmutables + fotografía obligatoria | Aceptada | Formulario producto |

---

## Enlaces Relacionados

- [[PROJECT_CONTEXT]] — Contexto global del proyecto
- [[ARCHITECTURE]] — Arquitectura derivada de estas decisiones
- [[ROADMAP]] — Plan para revisar/mitigar decisiones existentes

