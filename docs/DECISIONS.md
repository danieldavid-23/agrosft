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

**Fecha**: Pre-proyecto (heredado)  
**Estado**: Aceptada

### Contexto

La base de datos incluye el trigger `trg_actualizar_stock_oferta` que se ejecuta automáticamente al insertar registros en `tblproductos_has_tblusuarios_has_movimiento`.

### Decisión

El trigger es la única fuente de verdad para:
- Actualizar `cantidad` en `tblproductos_has_tblusuarios`
- Recalcular `calificacion_promedio` al insertar calificaciones

El código Python **NUNCA** debe actualizar estos campos manualmente.

### Consecuencias

- ✅ Consistencia garantizada a nivel de BD (independiente del código)
- ✅ Evita condiciones de carrera en actualizaciones concurrentes
- ❌ Lógica de negocio invisible en el código Python
- ❌ Difícil de depurar sin acceso a la definición del trigger
- ❌ Testing requiere BD real (no se puede mockear fácilmente)

---

## ADR-003: Módulo de Solicitudes en JavaScript Puro (Sin BD)

**Fecha**: 2026-06-17  
**Estado**: Aceptada

### Contexto

El usuario solicitó que el módulo de solicitudes funcione completamente en JavaScript, sin conexión a la base de datos y sin necesidad de registrar solicitudes reales.

### Decisión

Refactorizar `SolicitudApp.vue` para:
1. No usar `fetch()` hacia endpoints Django
2. No requerir `csrf.js` ni tokens CSRF
3. Operar completamente sobre estado Vue reactivo
4. Cargar datos desde JSON inyectado por Django (si existe) o datos mock locales (fallback)
5. Simplificar `main.js` para montar sin props

### Consecuencias

- ✅ El componente funciona de forma autónoma sin backend
- ✅ Ideal para demostraciones y pruebas de UI
- ✅ No requiere configuración de BD para desarrollo frontend
- ❌ Los cambios de estado no persisten (se pierden al recargar la página)
- ❌ Desconexión entre frontend y backend para este módulo

### Archivos Afectados

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

## Resumen de Decisiones

| ID | Decisión | Estado | Impacto |
|---|---|---|---|
| ADR-001 | BD legacy con managed=False | Aceptada | Arquitectura completa |
| ADR-002 | Stock por trigger BD | Aceptada | Todas las transacciones |
| ADR-003 | Solicitudes JS puro | Aceptada | Módulo ventas |
| ADR-004 | Carrito en sesión | Aceptada | Módulo carrito |
| ADR-005 | Cantidades negativas | Aceptada | Modelo de datos |
| ADR-006 | SPA parcial Vue+Vite | Aceptada | Frontend completo |
| ADR-007 | Auth backend custom | Aceptada | Seguridad |
| ADR-008 | Docs Obsidian | Aceptada | Documentación |

---

## Enlaces Relacionados

- [[PROJECT_CONTEXT]] — Contexto global del proyecto
- [[ARCHITECTURE]] — Arquitectura derivada de estas decisiones
- [[ROADMAP]] — Plan para revisar/mitigar decisiones existentes
