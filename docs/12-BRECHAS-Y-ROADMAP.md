# Brechas y Roadmap

> Análisis de funcionalidades faltantes vs. la ficha del proyecto SENA y plan de evolución.

---

## Estado Actual vs. Ficha del Proyecto

### ✅ Implementado

| Funcionalidad | Módulo | Detalle |
|---|---|---|
| Registro de usuarios | [[04-MODULO-USUARIOS]] | Formulario completo con validación |
| Login/Logout | [[04-MODULO-USUARIOS]] | Backend personalizado + sesión cache |
| Perfil de usuario | [[04-MODULO-USUARIOS]] | Editar datos + imagen de perfil |
| Cambio de contraseña | [[04-MODULO-USUARIOS]] | Verificación de contraseña actual |
| Términos y condiciones | [[04-MODULO-USUARIOS]] | Simulados (sin tabla BD) |
| CRUD de productos | [[05-MODULO-INVENTARIO]] | Crear, editar, eliminar, listar |
| Catálogo con filtros | [[05-MODULO-INVENTARIO]] | Búsqueda, categoría, orden, paginación |
| Marketplace | [[05-MODULO-INVENTARIO]] | Productos aprobados de otros usuarios |
| Aprobación de productos | [[05-MODULO-INVENTARIO]] | Admin aprueba/rechaza publicaciones |
| Carrito de compras | [[06-MODULO-VENTAS]] | Basado en sesión, CRUD completo |
| Solicitudes de compra | [[06-MODULO-VENTAS]] | Flujo completo con estados |
| Calificaciones | [[06-MODULO-VENTAS]] | 1-5 estrellas, trigger de promedio |
| Historial de clientes | [[07-MODULO-CLIENTES]] | Actividad de compradores/vendedores |
| Stock automático | [[03-BASE-DATOS]] | Triggers de BD |
| Diseño responsive | [[08-FRONTEND]] | Bootstrap 5 + CSS custom |

---

### 🔄 En Progreso / Refactor

| Funcionalidad | Estado | Detalle |
|---|---|---|
| Módulo de Solicitudes | Migrando a JS puro | Sin conexión a BD, datos mock en frontend |

---

### ❌ Faltante (Alta Prioridad)

#### 1. Chat / Mensajería Bidireccional
**Ficha dice**: "Chat integrado con plantillas de mensajes para agilizar acuerdos"

**No existe**: No hay sistema de mensajería entre comprador y vendedor.

**Propuesta**:
- Modelo `Mensaje` con `emisor`, `receptor`, `contenido`, `fecha`
- Vista de conversación por solicitud/producto
- Polling o WebSocket (Django Channels) para tiempo real
- Plantillas de mensajes predefinidos

**Impacto**: Componente central del alcance — sin chat, no hay comunicación directa.

---

#### 2. Fotos de Productos
**Ficha dice**: "Subida de datos de productos (fotos, precios, stock, ubicación)"

**No existe**: El modelo `Producto` no tiene campo de imagen. Solo `UserProfile` maneja fotos.

**Propuesta**:
- Agregar campo `imagen` a `tblproducto` o crear tabla `producto_imagen`
- Integrar Pillow para redimensionado automático
- Upload con preview en formulario

**Impacto**: Mejora significativa la experiencia del comprador en el marketplace.

---

#### 3. Ubicación de Productos
**Ficha dice**: "Detalles clave: precios por volumen, ubicación, métodos de cultivo"

**No existe**: Ningún modelo tiene campo de ubicación geográfica.

**Propuesta**:
- Agregar campos `municipio`, `departamento` a `Producto` o `ProductoUsuario`
- Mostrar en detalle de producto
- Filtro por región en marketplace

---

#### 4. Sistema de Notificaciones
**Ficha dice**: "Notificación al comprador con detalles de entrega/acuerdo"

**No existe**: Solo `EMAIL_BACKEND = 'console'` — no envía emails reales.

**Propuesta**:
- Modelo `Notificacion` con `usuario`, `tipo`, `mensaje`, `leida`
- Notificaciones in-app (badge en navbar)
- Email real con SMTP (SendGrid, Mailgun)
- Notificar: solicitud recibida, aceptada, rechazada, vendida

---

### ❌ Faltante (Prioridad Media)

#### 5. Precios por Volumen
**Ficha dice**: "Precios por volumen"

**No existe**: Solo hay precio unitario por publicación.

**Propuesta**:
- Tabla `precio_volumen` con `producto_usuario`, `cantidad_min`, `precio`
- Mostrar rangos en detalle de producto

---

#### 6. Verificación de Agricultores
**Ficha dice**: "Registro y verificación de agricultores: Validación de identidad y métodos de cultivo"

**No existe**: El registro es abierto, sin verificación.

**Propuesta**:
- Campo `verificado` en `Tblusuarios`
- Flujo de verificación: subir documento → admin revisa → aprueba
- Badge de "Verificado" en marketplace

---

#### 7. Recuperación de Contraseña (Real)
**Actual**: Las vistas existen pero no envían email ni verifican tokens.

**Propuesta**:
- Integrar `django.contrib.auth.views.PasswordResetView` con backend SMTP
- Configurar `EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'`

---

#### 8. Pagos / Pasarela
**Ficha dice**: "Sin pagos integrados: negociación directa"

**Decisión**: Esto es **by design** — la ficha explícitamente excluye pagos. No implementar.

---

### ❌ Faltante (Prioridad Baja / Futuro)

| Funcionalidad | Descripción | Prioridad |
|---|---|---|
| Alertas de mercado | Precios locales y tendencias | Baja |
| Asesoría técnica | FAQ / guías digitales | Baja |
| Documentos comerciales | Plantillas de facturas descargables | Baja |
| Calendario de cosechas | Alertas por ciclos de siembra | Baja |
| Recomendaciones IA | Sugerencias de precios según mercado | Futuro |
| App móvil | Versión nativa PWA | Futuro |

---

## Problemas Técnicos Detectados

| # | Problema | Severidad | Archivo |
|---|---|---|---|
| 1 | SQL Injection en `tabla_existe()` y `columna_existe()` | 🔴 Alta | `auth_controller.py`, `backends.py` |
| 2 | `TemporalUsuario.check_password()` siempre retorna True | 🔴 Alta | `profile_model.py` |
| 3 | `has_perm()` siempre True en backend | 🟡 Media | `backends.py` |
| 4 | Carrito sin `@login_required` | 🟡 Media | `carrito_controller.py` |
| 5 | Modelo `Cliente` sin `managed = False` | 🟡 Media | `cliente.py` |
| 6 | `TipoMovimiento` duplicado en inventario y ventas | 🟢 Baja | `producto.py`, `movimiento.py` |
| 7 | Modelos obsoletos activos | 🟢 Baja | `solicitud.py`, `venta.py` |
| 8 | Bare `except:` en múltiples sitios | 🟢 Baja | Varios |
| 9 | Password reset sin implementación real | 🟡 Media | `auth_controller.py` |
| 10 | `Termino` duplicado en core y usuarios | 🟢 Baja | Ambos archivos |

---

## Roadmap Sugerido

### Fase 1 — Estabilización (Sprint actual)
- [x] Documentación completa del proyecto
- [x] Refactor módulo solicitudes a JS puro
- [ ] Corregir SQL Injection en helpers
- [ ] Eliminar `TemporalUsuario` o marcar como dev-only
- [ ] Agregar `managed = False` a modelo `Cliente`

### Fase 2 — Funcionalidades Core
- [ ] Implementar chat/mensajería entre usuarios
- [ ] Agregar campo de imagen a productos
- [ ] Implementar notificaciones in-app
- [ ] Completar password reset con email real

### Fase 3 — Enriquecimiento
- [ ] Agregar ubicación a productos
- [ ] Precios por volumen
- [ ] Verificación de agricultores
- [ ] Filtros avanzados en marketplace

### Fase 4 — Escalabilidad
- [ ] Alertas de mercado
- [ ] Documentos comerciales
- [ ] PWA / app móvil
- [ ] Integración con APIs externas (clima, precios)

---

## Enlaces Relacionados

- [[00-INDEX]] — Volver al índice
- [[01-VISION-GENERAL]] — Ficha del proyecto y alcance
- [[11-CONVENCIONES]] — Estándares para implementar
