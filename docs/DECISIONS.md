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
- ❌ Compresión/redimensionado con Pillow pendiente (roadmap GAP-02)

### Archivos Afectados

- `apps/inventario/models/producto.py` — campo `imagen`
- `apps/usuarios/models/profile_model.py` — campo `imagen_perfil`
- `apps/inventario/forms/producto_form.py` — validators en `imagen`
- `apps/usuarios/forms/auth_forms.py` — validators en `imagen_perfil`
- `apps/inventario/controllers/producto_controller.py` — `request.FILES` y exposición de URL
- `apps/usuarios/controllers/auth_controller.py` — guardado de imagen de perfil
- `core/utils/helpers.py` — `validate_image_size`
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

- `scripts/crear_tabla_producto_imagenes.sql` [NEW]
- `apps/inventario/models/producto.py` — modelo `ProductoImagen` y método `get_imagenes()`
- `apps/inventario/forms/producto_form.py` — soporte `multiple` en campo `imagen`
- `apps/inventario/controllers/producto_controller.py` — procesamiento de múltiples archivos y array `imagenes`
- `frontend/src/inventario/InventarioApp.vue` — carrusel interactivo en tarjetas
- `frontend/src/marketplace/MarketApp.vue` — carrusel interactivo en tarjetas
- `apps/inventario/templates/inventario/producto_form.html` — previsualización y galería de imágenes
- `apps/inventario/templates/inventario/Productosdetalles.html` — carrusel de detalle con miniaturas

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

---

## Enlaces Relacionados

- [[PROJECT_CONTEXT]] — Contexto global del proyecto
- [[ARCHITECTURE]] — Arquitectura derivada de estas decisiones
- [[ROADMAP]] — Plan para revisar/mitigar decisiones existentes

