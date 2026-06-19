# CHANGELOG.md — AgroSFT

> Historial cronológico de cambios significativos en el proyecto.  
> Formato basado en [Keep a Changelog](https://keepachangelog.com/).

---

## [Unreleased]

### Added (2026-06-17)
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
