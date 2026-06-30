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
3. **Tablas inexistentes**: `user_profiles`, `user_devices`, `user_addresses` documentadas como tablas reales pero no existen en MariaDB
4. **Flujo de stock**: la descripción indicaba que `compra` descuenta stock, pero el trigger actual ignora `compra` y solo descuenta en `vendida`

### Decisión

Actualizar toda la documentación SDD para reflejar fielmente el estado real de la base de datos MariaDB, marcando claramente:

- Los 5 tipos de movimiento y su significado
- Los 5 triggers activos con sus eventos específicos
- Las tablas que existen solo como modelos Django sin respaldo en BD
- El flujo real de stock: `compra`/`venta`/`rechazada`/`cancelada` no afectan stock; solo `vendida` descuenta

### Consecuencias

- ✅ La documentación ahora es la fuente única de verdad (principio SDD #1)
- ✅ Desarrolladores e IAs pueden entender la BD real sin acceso a phpMyAdmin
- ✅ Las discrepancias entre código y BD están explícitamente documentadas
- ❌ Las tablas `user_profiles`, `user_devices`, `user_addresses` quedan como modelos huérfanos sin funcionalidad real

### Archivos Afectados

- `docs/DATABASE.md` — Reestructuración completa de triggers, tipos, tablas y flujo de stock
- `docs/ARCHITECTURE.md` — Agregado `cancelada` a tabla de estados
- `docs/USER_STORIES.md` — Agregado `Cancelada` al diagrama de flujo
- `docs/03-BASE-DATOS.md` — Sincronizado con DATABASE.md
- `docs/CHANGELOG.md` — Registro del cambio de documentación

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

---

## Enlaces Relacionados

- [[PROJECT_CONTEXT]] — Contexto global del proyecto
- [[ARCHITECTURE]] — Arquitectura derivada de estas decisiones
- [[ROADMAP]] — Plan para revisar/mitigar decisiones existentes

