# MANUAL TÉCNICO  
## AgroSFT — Plataforma de Marketplace Agrícola

---

**Servicio Nacional de Aprendizaje — SENA**  
**Regional Antioquia**  
**Centro de Tecnologías de la Gestión e Información (CTGI)**  
**Programa de Formación:** Análisis y Desarrollo de Software (ADSO)

---

| Campo | Valor |
|-------|-------|
| **Software** | AgroSFT |
| **Versión** | 1.0.0 |
| **Ficha** | 3109846 |
| **Aprendices** | Juan Felipe Quiros Bena, Samuel Pérez Mena, Daniel David Hernandez Baron, Melissa Cabrales Posada |
| **Instructora titular** | Lilliana Uribe G. |
| **Repositorio** | [https://github.com/danieldavid-23/agrosft.git](https://github.com/danieldavid-23/agrosft.git) |
| **Fecha** | [dd/mm/aaaa] |

---

## Portadilla

# MANUAL TÉCNICO  
**AgroSFT**  
Versión 1.0.0  
SENA — Regional Antioquia — Medellín  
[Fecha]

---

## Colaboradores

| Rol | Nombre | Documento | Correo / Contacto |
|-----|--------|-----------|-------------------|
| Aprendiz — Desarrollo | Juan Felipe Quiros Bena | [Documento] | [Correo] |
| Aprendiz — Desarrollo | Samuel Pérez Mena | [Documento] | [Correo] |
| Aprendiz — Desarrollo | Daniel David Hernandez Baron | [Documento] | [Correo] |
| Aprendiz — Desarrollo | Melissa Cabrales Posada | [Documento] | [Correo] |
| Instructora | Lilliana Uribe G. | [Documento] | [Correo] |
| Instructor — Base de datos | Edilfredo Pineda | [Documento] | [Correo] |
| Instructor — Frontend | Hector Maya | [Documento] | [Correo] |
| Instructora — Algoritmos | Erika Florez | [Documento] | [Correo] |
| Revisor técnico | [Nombre y cargo] | --- | [Correo] |
| Cliente o entidad | [Nombre y datos de contacto] | --- | --- |

---

## Control de Versiones y Aprobación

| Versión | Fecha | Responsable | Descripción del cambio | Aprobación |
|---------|-------|-------------|------------------------|------------|
| 1.0.0 | [dd/mm/aaaa] | Equipo AgroSFT | Documentación técnica completa del sistema: arquitectura, base de datos, módulos, seguridad, instalación, operación y pruebas | [Nombre y cargo] |

- **Versión actual:** 1.0.0  
- **Fecha:** [dd/mm/aaaa]  
- **Elaboró:** Equipo de desarrollo AgroSFT  
- **Revisó / aprobó:** [Nombre y cargo]  
- **Estado:** [Borrador / aprobado / publicado]

---

## Tabla de Contenido

1. [Portada](#portada)  
2. [Portadilla](#portadilla)  
3. [Lista de colaboradores](#lista-de-colaboradores)  
4. [Control de versiones y aprobación](#control-de-versiones-y-aprobación)  
5. [Tabla de contenido](#tabla-de-contenido)  
6. [Tabla de imágenes (opcional)](#tabla-de-imágenes-opcional)  
7. [Introducción](#introducción)  
8. [Descripción general del sistema](#descripción-general-del-sistema)  
9. [Arquitectura y diseño](#arquitectura-y-diseño)  
10. [Requerimientos técnicos](#requerimientos-técnicos)  
11. [Ambientes de desarrollo, pruebas y producción](#ambientes-de-desarrollo-pruebas-y-producción)  
12. [Estructura interna](#estructura-interna-programas-módulos-catálogos-y-archivos)  
13. [Base de datos](#base-de-datos)  
14. [Seguridad](#seguridad)  
15. [Instalación, configuración y despliegue](#instalación-configuración-y-despliegue)  
16. [Operación y mantenimiento](#operación-y-mantenimiento)  
17. [Pruebas y calidad](#pruebas-y-calidad)  
18. [Solución de problemas y asistencia técnica](#solución-de-problemas-y-asistencia-técnica)  
19. [Apéndices](#apéndices)  
20. [Glosario](#glosario)  
21. [Bibliografía](#bibliografía)  
22. [Índice analítico](#índice-analítico)

---

## Tabla de Imágenes (Opcional)

| # | Figura | Sección |
|---|--------|---------|
| Figura 1 | Diagrama de capas de la arquitectura | 9.1 |
| Figura 2 | Flujo de autenticación | 9.1 |
| Figura 3 | Diagrama Entidad-Relación | 13.1 |
| Figura 4 | Flujo principal del usuario | 8.3 |

> **Nota:** Las figuras se representan como diagramas Mermaid (renderizables en editores Markdown compatibles). Para la versión Word/PDF, exportar los diagramas como imágenes numeradas.

---

## 1. Introducción

### 1.1 Propósito

Este manual técnico documenta la arquitectura, el diseño, la implementación y la operación de **AgroSFT**, una plataforma web de marketplace agrícola. Su propósito es servir como referencia oficial para el equipo de desarrollo, el personal de soporte técnico, los administradores del sistema y los evaluadores del proyecto, garantizando la continuidad del conocimiento técnico y la mantenibilidad del software.

### 1.2 Alcance

El manual cubre la versión 1.0.0 de AgroSFT e incluye:

- Descripción general del sistema y sus módulos funcionales.
- Arquitectura de software y decisiones técnicas.
- Estructura interna del código, repositorio y archivos de configuración.
- Modelo de base de datos (MariaDB legacy) y sus triggers.
- Controles de seguridad implementados.
- Procedimientos de instalación, configuración, despliegue y operación.
- Estrategia de pruebas y calidad.
- Solución de problemas comunes y asistencia técnica.

Quedan fuera del alcance: el manual de usuario final (vista de negocio del sistema), el manual de instalación detallado para usuarios no técnicos y los procedimientos internos del SENA.

### 1.3 Audiencia técnica

Este manual está dirigido a: desarrolladores de software (backend y frontend), administradores de base de datos, administradores del sistema, personal de soporte técnico, instructores y evaluadores del proyecto.

### 1.4 Versión documentada

Todas las referencias de código, rutas, variables y configuraciones corresponden a la **versión 1.0.0** del repositorio (confirmado en el estado actual de la rama `master`).

### 1.5 Convenciones usadas en el documento

- `Código`, `rutas`, `nombres de archivos`, `variables` y `comandos` se muestran en fuente monoespaciada.
- Los placeholders entre corchetes (`[Campo]`) deben completarse con datos institucionales (nombres, documentos, fechas).
- Las advertencias de riesgo se resaltan con la notación `> [!danger]` / `> [!warning]`.
- Los diagramas usan sintaxis Mermaid.

### 1.6 Relación con otros manuales

- **Manual de usuario** (documento aparte): describe el uso funcional del sistema desde la perspectiva del usuario final.
- **Manual de instalación** (documento aparte): detalla el paso a paso de instalación; el capítulo 15 de este manual lo resume a nivel técnico.

---

## 2. Descripción General del Sistema

### 2.1 Objetivo de la solución

AgroSFT es una plataforma digital que **conecta directamente a productores agrícolas con compradores**, eliminando la dependencia de intermediarios en la cadena de suministro. Ofrece herramientas de gestión agrícola: publicación de productos, gestión de inventario, solicitudes de compra, carrito de compras, calificaciones de transacciones y facturación.

### 2.2 Contexto y problemática

La cadena de suministro agrícola presenta tres problemas principales que motivan el proyecto:

1. Alta dependencia de intermediarios, que reducen el margen del productor.
2. Visibilidad limitada de los productos ofertados.
3. Ausencia de herramientas tecnológicas para gestionar oferta y demanda.

AgroSFT responde con un canal de **comercio justo** para productos frescos y locales, donde la negociación se realiza directamente entre las partes (la plataforma no integra pagos, por diseño).

### 2.3 Módulos del sistema

| # | Módulo | App Django | Descripción | Estado |
|---|--------|------------|-------------|--------|
| 1 | Gestión de usuarios | `apps.usuarios` | Registro, login/logout, perfil, cambio de contraseña, recuperación de contraseña (Brevo), Google OAuth, términos y condiciones | ✅ Implementado |
| 2 | Gestión de productos e inventario | `apps.inventario` | CRUD de productos, catálogo unificado, stock, marketplace con filtros y paginación AJAX | ✅ Implementado |
| 3 | Ventas y solicitudes | `apps.ventas` | Carrito de compras (sesión), solicitudes de compra con estados, movimientos, calificaciones | ✅ Implementado |
| 4 | Clientes | `apps.clientes` | Historial de compradores y actividad de usuarios | ✅ Implementado |
| 5 | Facturación | `apps.facturacion` | Generación de facturas, historial y exportación PDF (xhtml2pdf) | ✅ Implementado |
| 6 | Administración | `apps.usuarios` (controladores admin) | Gestión de usuarios, moderación de productos, categorías, estadísticas, reportes CSV y auditoría | ✅ Implementado |
| 7 | Frontend interactivo | `frontend/` (Vue 3 + Vite) | Marketplace, carrito, inventario y calificaciones como componentes SPA parciales | ✅ Implementado |

### 2.4 Actores del sistema

| Actor | Descripción | Permisos principales |
|-------|-------------|----------------------|
| **Invitado** | Visitante sin sesión | Ver marketplace, registrarse, iniciar sesión |
| **Agricultor / Productor** | Usuario autenticado que publica productos | CRUD de productos propios, gestionar solicitudes recibidas, vender, calificar |
| **Comprador** | Usuario autenticado que adquiere productos | Carrito, solicitudes de compra, compras, calificar transacciones |
| **Administrador** | Usuario `is_staff` / `is_superuser` | Administración de usuarios, moderación, categorías, reportes, auditoría, Django Admin |

### 2.5 Límites del sistema

- La plataforma **no maneja pagos** (decisión explícita de la ficha del proyecto).
- La mensajería, las notificaciones en tiempo real, las fotos de productos y la geolocalización **no están implementadas** (ver brechas en el capítulo 18).
- El esquema de base de datos es **legacy y externo a Django**: los modelos son de solo lectura (`managed = False`).

### 2.6 Flujo principal del usuario

```mermaid
graph TB
    A[Registro/Login] --> B[Marketplace]
    B --> C[Agregar al Carrito]
    C --> D[Checkout - Solicitud de Compra]
    D --> E[Vendedor recibe Solicitud]
    E --> F{Decisión}
    F -->|Aceptar| G[Cambiar tipo a Venta]
    F -->|Rechazar| H[Marcar como Rechazada]
    G --> I[Marcar como Vendida]
    I --> J[Calificar Transacción]
    B --> K[Mi Inventario]
    K --> L[Crear/Editar/Eliminar Productos]
    L --> M[Admin aprueba/rechaza] 