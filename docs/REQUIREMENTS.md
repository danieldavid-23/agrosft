# REQUIREMENTS.md — AgroSFT

> Requisitos funcionales y no funcionales del sistema.  
> **Fuente**: Ficha de Proyecto SENA 2988405 + Análisis de código existente  
> **Metodología**: Specification-Driven Development (SDD)

---

## 1. Requisitos Funcionales

### 1.1 Módulo de Usuarios

| ID | Requisito | Prioridad | Estado |
|---|---|---|---|
| RF-U01 | El sistema debe permitir el registro de nuevos usuarios con nombres, apellidos, correo, teléfono y contraseña | Alta | ✅ Implementado |
| RF-U02 | El sistema debe autenticar usuarios mediante correo y contraseña | Alta | ✅ Implementado |
| RF-U03 | El sistema debe permitir cerrar sesión de forma segura | Alta | ✅ Implementado |
| RF-U04 | El sistema debe permitir visualizar y editar el perfil del usuario | Media | ✅ Implementado |
| RF-U05 | El sistema debe permitir cambiar la contraseña del usuario autenticado | Media | ✅ Implementado |
| RF-U06 | El sistema debe permitir la autenticación mediante Google OAuth2 | Baja | ⚙️ Configurado (no activo) |
| RF-U07 | El sistema debe gestionar la aceptación de términos y condiciones | Media | ✅ Implementado |
| RF-U08 | El sistema debe permitir recuperar contraseña por correo electrónico | Media | 🔶 Parcial (UI presente, backend no conectado) |
| RF-U09 | El sistema debe permitir subir y eliminar foto de perfil | Baja | ✅ Implementado |

### 1.2 Módulo de Inventario

| ID | Requisito | Prioridad | Estado |
|---|---|---|---|
| RF-I01 | El sistema debe permitir crear productos con nombre, descripción, categoría, precio, cantidad y stock mínimo | Alta | ✅ Implementado |
| RF-I02 | El sistema debe listar los productos del usuario actual (Mi Inventario) | Alta | ✅ Implementado |
| RF-I03 | El sistema debe permitir editar productos existentes | Alta | ✅ Implementado |
| RF-I04 | El sistema debe permitir eliminar productos (soft delete) | Alta | ✅ Implementado |
| RF-I05 | El sistema debe mostrar un marketplace con productos de otros usuarios aprobados | Alta | ✅ Implementado |
| RF-I06 | El sistema debe permitir buscar productos por nombre | Media | ✅ Implementado |
| RF-I07 | El sistema debe permitir filtrar productos por categoría | Media | ✅ Implementado |
| RF-I08 | El sistema debe permitir ordenar productos por precio y nombre | Media | ✅ Implementado |
| RF-I09 | El sistema debe permitir al admin aprobar o rechazar productos publicados | Alta | ✅ Implementado |
| RF-I10 | El sistema debe paginar los resultados del marketplace (12 por página) | Media | ✅ Implementado |
| RF-I11 | El sistema debe paginar los resultados del inventario personal (10 por página) | Media | ✅ Implementado |
| RF-I12 | El sistema debe registrar movimiento de stock al crear/editar productos | Alta | ✅ Implementado |
| RF-I13 | El sistema debe alertar cuando el stock esté por debajo del mínimo | Media | 🔶 Parcial (badge visual) |
| RF-I14 | El sistema debe permitir verificar stock vía API endpoint | Baja | ✅ Implementado |

### 1.3 Módulo de Ventas

| ID | Requisito | Prioridad | Estado |
|---|---|---|---|
| RF-V01 | El sistema debe permitir agregar productos al carrito de compras | Alta | ✅ Implementado |
| RF-V02 | El sistema debe permitir modificar cantidades en el carrito | Alta | ✅ Implementado |
| RF-V03 | El sistema debe permitir eliminar productos del carrito | Alta | ✅ Implementado |
| RF-V04 | El carrito debe persistir en la sesión del usuario | Alta | ✅ Implementado (cache-backed session) |
| RF-V05 | El sistema debe validar stock disponible al agregar al carrito | Alta | ✅ Implementado |
| RF-V06 | El sistema debe crear una solicitud de compra desde el checkout | Alta | ✅ Implementado |
| RF-V07 | El sistema debe listar las solicitudes recibidas por el vendedor | Alta | ✅ Implementado |
| RF-V08 | El sistema debe permitir al vendedor aceptar una solicitud | Alta | ✅ Implementado |
| RF-V09 | El sistema debe permitir al vendedor rechazar una solicitud | Alta | ✅ Implementado |
| RF-V10 | El sistema debe permitir marcar una solicitud como vendida | Alta | ✅ Implementado |
| RF-V11 | El sistema debe listar las ventas con estados visibles: "En proceso" y "Vendido" | Media | ✅ Implementado |
| RF-V12 | El sistema debe mostrar el detalle de una venta específica | Media | ✅ Implementado |
| RF-V16 | El sistema debe permitir marcar una venta como "Vendido" desde el módulo de ventas | Alta | ✅ Implementado |
| RF-V17 | Al marcar como "Vendido", el stock debe actualizarse automáticamente (trigger en BD) | Alta | ✅ Implementado |
| RF-V18 | Al aceptar una solicitud, el sistema debe generar un enlace de WhatsApp (wa.me) con mensaje predefinido para contactar al comprador | Alta | ✅ Implementado |
| RF-V19 | El sistema debe mostrar el número de teléfono del comprador como enlace cliqueable de WhatsApp cuando la solicitud está aceptada | Media | ✅ Implementado |
| RF-V13 | El sistema debe permitir calificar una transacción (1.0–5.0, pasos de 0.5) | Media | ✅ Implementado |
| RF-V14 | El sistema debe mostrar historial de movimientos del usuario | Media | ✅ Implementado |
| RF-V15 | El frontend de solicitudes debe funcionar sin conexión a base de datos | Alta | ❌ Eliminado — Se revirtió a renderizado Django server-side |

### 1.4 Módulo de Clientes

| ID | Requisito | Prioridad | Estado |
|---|---|---|---|
| RF-C01 | El sistema debe listar usuarios que han realizado movimientos | Media | ✅ Implementado |
| RF-C02 | El sistema debe mostrar el historial de compras de un cliente | Media | ✅ Implementado |
| RF-C03 | El sistema debe mostrar estadísticas de compras/ventas por usuario | Baja | ✅ Implementado |

---

## 2. Requisitos No Funcionales

### 2.1 Seguridad

| ID | Requisito | Prioridad | Estado |
|---|---|---|---|
| RNF-S01 | Las contraseñas deben almacenarse cifradas con Django hashers | Alta | ✅ Implementado |
| RNF-S02 | Todas las vistas sensibles requieren autenticación (`@login_required`) | Alta | ⚠️ Parcial (carrito sin @login_required) |
| RNF-S03 | Protección contra CSRF en todos los formularios | Alta | ✅ Implementado |
| RNF-S04 | Headers de seguridad (XSS, clickjacking, content-type) | Alta | ✅ Implementado |
| RNF-S05 | SSL/HTTPS en producción (HSTS, secure cookies) | Alta | ✅ Implementado (condicional a DEBUG=False) |
| RNF-S06 | Prevención de caché del navegador tras logout | Media | ✅ Implementado (NoCacheMiddleware) |
| RNF-S07 | Sesiones expiran al cerrar navegador (30 min max) | Media | ✅ Implementado |
| RNF-S08 | Validación de contraseña mínima (8 caracteres) | Alta | ✅ Implementado |
| RNF-S09 | Protección contra SQL injection en queries auxiliares | Alta | ❌ Vulnerabilidad en `tabla_existe()` y `columna_existe()` |

### 2.2 Rendimiento

| ID | Requisito | Prioridad | Estado |
|---|---|---|---|
| RNF-P01 | Caché de categorías y estados (1 hora) | Media | ✅ Implementado |
| RNF-P02 | Queries optimizadas con `select_related` | Media | ✅ Implementado |
| RNF-P03 | Paginación de resultados | Media | ✅ Implementado |
| RNF-P04 | Code splitting en frontend (Vite chunks) | Media | ✅ Implementado |

### 2.3 Usabilidad

| ID | Requisito | Prioridad | Estado |
|---|---|---|---|
| RNF-U01 | Interfaz responsiva con Bootstrap 5 | Alta | ✅ Implementado |
| RNF-U02 | Notificaciones toast para feedback al usuario | Media | ✅ Implementado |
| RNF-U03 | Formato de precios en COP (pesos colombianos) | Media | ✅ Implementado |
| RNF-U04 | Iconografía clara con Font Awesome | Media | ✅ Implementado |
| RNF-U05 | Soporte para WhatsApp (enlace wa.me con mensaje predefinido al aceptar solicitud) | Media | ✅ Implementado |

### 2.4 Mantenibilidad

| ID | Requisito | Prioridad | Estado |
|---|---|---|---|
| RNF-M01 | Arquitectura por capas (Controller-Service-Repository) | Alta | ✅ Implementado |
| RNF-M02 | Nomenclatura consistente en español | Media | ✅ Implementado |
| RNF-M03 | Logging centralizado (archivo + consola) | Media | ✅ Implementado |
| RNF-M04 | Documentación completa para Obsidian | Alta | ✅ Implementado |
| RNF-M05 | Código frontend modular por componente Vue | Media | ✅ Implementado |

### 2.5 Compatibilidad

| ID | Requisito | Prioridad | Estado |
|---|---|---|---|
| RNF-C01 | Base de datos legacy MariaDB (Django no gestiona schema) | Alta | ✅ Implementado |
| RNF-C02 | Zona horaria America/Bogota | Media | ✅ Implementado |
| RNF-C03 | Idioma principal: español | Alta | ✅ Implementado |
| RNF-C04 | Navegadores modernos (Chrome, Firefox, Edge) | Media | ✅ Implementado |

---

## 3. Requisitos Pendientes (Brechas)

Requisitos identificados en la ficha del proyecto SENA que **no están implementados**:

| ID | Requisito | Prioridad | Complejidad |
|---|---|---|---|
| GAP-01 | Chat/mensajería entre comprador y vendedor | Alta | Alta |
| GAP-02 | Fotografías de productos | Alta | Media |
| GAP-03 | Geolocalización de productos y agricultores | Media | Media |
| GAP-04 | Notificaciones push en tiempo real | Media | Alta |
| GAP-05 | Precios por volumen (descuentos por cantidad) | Media | Media |
| GAP-06 | Verificación de agricultores | Baja | Media |
| GAP-07 | Alertas de mercado (precios, disponibilidad) | Baja | Alta |
| GAP-08 | Reportes y estadísticas avanzadas | Baja | Media |

> Ver [[ROADMAP]] para el plan de implementación de estas brechas.

---

## Enlaces Relacionados

- [[PROJECT_CONTEXT]] — Contexto global del proyecto
- [[USER_STORIES]] — Historias de usuario derivadas de estos requisitos
- [[ARCHITECTURE]] — Cómo la arquitectura satisface estos requisitos
- [[ROADMAP]] — Plan de implementación de requisitos pendientes
