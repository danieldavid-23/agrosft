# AgroSFT — Base de Conocimiento

> **Centro de documentación técnica del proyecto AgroSFT.**  
> Diseñado para Obsidian: todos los enlaces usan `[[wikilinks]]` y están organizados por módulo.  
> **Metodología**: Specification-Driven Development (SDD)

---

## Especificaciones SDD (Fuente Única de Verdad)

| Documento | Contenido | Rol SDD |
|---|---|---|
| [[PROJECT_CONTEXT]] | Contexto global, stack, flujos principales | Punto de entrada SDD |
| [[REQUIREMENTS]] | 45 requisitos funcionales + 17 no funcionales + 8 brechas | Qué debe hacer el sistema |
| [[USER_STORIES]] | 13 historias de usuario con criterios de aceptación | Cómo lo usa el usuario |
| [[ARCHITECTURE]] | Arquitectura, módulos, patrones, diagramas Mermaid | Cómo está construido |
| [[DATABASE]] | 9 tablas reales en MariaDB, triggers (5), ER diagram, convenciones | Dónde se guardan los datos |
| [[API]] | 36 endpoints con contratos request/response | Cómo se comunica |
| [[ROADMAP]] | Plan de evolución en 4 fases | Qué sigue |
| [[DECISIONS]] | 9 registros de decisiones técnicas (ADR) | Por qué se hizo así |
| [[CHANGELOG]] | Historial cronológico de cambios | Qué cambió y cuándo |

---

## Documentación Detallada por Módulo

| # | Documento | Contenido |
|---|---|---|
| 01 | [[01-VISION-GENERAL]] | Descripción del proyecto, objetivos, alcance y ficha técnica SENA |
| 02 | [[02-ARQUITECTURA]] | Arquitectura del sistema, capas, patrones de diseño y decisiones técnicas |
| 03 | [[03-BASE-DATOS]] | Esquema de base de datos MariaDB, modelos Django, triggers y relaciones |
| 04 | [[04-MODULO-USUARIOS]] | Autenticación, registro, perfil, términos y condiciones |
| 05 | [[05-MODULO-INVENTARIO]] | Catálogo de productos, CRUD, marketplace y aprobación |
| 06 | [[06-MODULO-VENTAS]] | Carrito, solicitudes, ventas y calificaciones |
| 07 | [[07-MODULO-CLIENTES]] | Historial de compradores y actividad de usuarios |
| 08 | [[08-FRONTEND]] | Componentes Vue 3, Vite, integración con Django templates |
| 09 | [[09-CONFIGURACION]] | Instalación, variables de entorno, servidor de desarrollo |
| 10 | [[10-API-ENDPOINTS]] | Referencia completa de todas las rutas URL del sistema |
| 11 | [[11-CONVENCIONES]] | Estándares de código, nomenclatura y prácticas del proyecto |
| 12 | [[12-BRECHAS-Y-ROADMAP]] | Funcionalidades faltantes vs. ficha del proyecto y plan de evolución |

---

## Acceso Rápido por Tema

### ¿Eres nuevo en el proyecto?
1. Lee [[PROJECT_CONTEXT]] para entender el propósito y arquitectura
2. Revisa [[REQUIREMENTS]] para conocer qué debe hacer el sistema
3. Consulta [[09-CONFIGURACION]] para montar tu entorno

### ¿Vas a implementar una funcionalidad? (Flujo SDD)
1. Lee [[PROJECT_CONTEXT]] — contexto global
2. Lee [[REQUIREMENTS]] — requisitos afectados
3. Lee [[USER_STORIES]] — historias de usuario relacionadas
4. Lee [[ARCHITECTURE]] — componentes afectados
5. Valida que la funcionalidad exista en la especificación
6. **Solo entonces** genera código
7. Actualiza [[CHANGELOG]] y documentación afectada

### ¿Vas a trabajar con la base de datos?
1. Lee [[03-BASE-DATOS]] completo
2. **Regla de oro**: todos los modelos son `managed = False` — Django NO gestiona el schema

### ¿Necesitas entender el frontend?
1. Lee [[08-FRONTEND]] para el mapa de componentes Vue
2. Cada componente recibe datos vía JSON inyectado en templates Django

---

## Información Clave del Stack

| Tecnología | Versión | Rol |
|---|---|---|
| Django | 6.0.2 | Framework web (backend) |
| MariaDB | 10.4 | Base de datos relacional |
| Vue.js | 3.5 | Componentes frontend SPA |
| Vite | 6 | Bundler de JavaScript |
| Bootstrap | 5.1.3 | Framework CSS |
| Font Awesome | 6.4 | Iconografía |
| Pillow | 10.2.0 | Procesamiento de imágenes |
| social-auth-app-django | — | Google OAuth2 |

---

## Estructura de Directorios

```
agrosft/
├── config/              → Settings, URLs raíz, WSGI/ASGI
├── core/                → Clases base, middleware, utilidades compartidas
├── apps/
│   ├── usuarios/        → [[04-MODULO-USUARIOS]]
│   ├── inventario/      → [[05-MODULO-INVENTARIO]]
│   ├── ventas/          → [[06-MODULO-VENTAS]]
│   └── clientes/        → [[07-MODULO-CLIENTES]]
├── frontend/src/        → [[08-FRONTEND]] (componentes Vue 3)
├── templates/           → Template base de Django
├── static/dist/         → Assets compilados por Vite
├── media/               → Archivos subidos por usuarios
├── scripts/             → Scripts de mantenimiento y validación
└── docs/                → Esta documentación
```

---

> [!note] Convención de documentación
> Toda la documentación está en español. Los comentarios en código fuente están en inglés según [[11-CONVENCIONES]].
>
> [!important] Metodología SDD
> Este proyecto sigue **Specification-Driven Development**: la documentación es la fuente única de verdad. Ninguna funcionalidad se implementa sin estar previamente especificada en [[REQUIREMENTS]] y [[USER_STORIES]]. Ver [[DECISIONS#ADR-008]].
