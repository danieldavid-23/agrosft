# 🌾 AgroSFT — Sistema de Información y Comercio Agrícola

[![Django](https://img.shields.io/badge/Django-6.0.2-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.5-4FC08D?style=for-the-badge&logo=vuedotjs&logoColor=white)](https://vuejs.org/)
[![Vite](https://img.shields.io/badge/Vite-6.4-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.1.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![MariaDB](https://img.shields.io/badge/MariaDB-10.4-003545?style=for-the-badge&logo=mariadb&logoColor=white)](https://mariadb.org/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)

> **AgroSFT** es una plataforma web integral diseñada en el marco de la formación profesional integral del **SENA**, enfocada en conectar de manera directa y justa a **productores campesinos** con **compradores y consumidores**, disminuyendo la intermediación comercial y modernizando la gestión del campo colombiano.

---

## 📖 Documentación Completa del Proyecto

Para consultar los manuales técnicos, arquitectura, base de datos y detalles de cada módulo:

- 📄 **[Documentación General Completa (DOCUMENTACION_GENERAL.md)](./DOCUMENTACION_GENERAL.md)** — Manual maestro con arquitectura, 9 capas de seguridad, modelos de datos, endpoints y guía completa de despliegue.
- 📁 **[Base de Conocimiento SDD (docs/)](./docs/00-INDEX.md)** — Documentación modular en formato Obsidian (Requisitos, Arquitectura, Decisiones ADR, Casos de Uso y Módulos).

---

## ✨ Funcionalidades Principales

### 🛒 1. Marketplace Agrícola Interactivo
- Catálogo público con **filtros reactivos en tiempo real** por categoría (Frutas, Hortalizas, Tubérculos, etc.) y buscador instantáneo construido con **Vue 3**.
- Ficha detallada con procedencia del productor, existencias actuales y valoraciones por estrellas.

### 📦 2. Gestión de Inventario y Cosechas
- Panel para productores campesinos con control de stock, fijación de precios unitarios y carga segura de imágenes de cosechas.
- **Flujo de moderación:** Las publicaciones pasan por un proceso de revisión y aprobación administrativa antes de ser visibles en el catálogo general.

### 🛍️ 3. Carrito de Compras y Venta Directa
- **Carrito con persistencia en sesión:** Ajuste dinámico de cantidades, cálculo automático de subtotales y emisión de solicitudes de compra.
- **Venta directa de mostrador:** Permite a los campesinos registrar ventas físicas en plaza o finca, deduciendo inventario y formalizando la entrega.

### 🧾 4. Facturación Electrónica y Descarga PDF
- Comprobantes de venta estructurados con desglose de impuestos (0% IVA Exento Agrícola - Ley 1607).
- Nombres de productos limpios y cantidades exactas sin decimales artificiales (`1` en lugar de `1,00`).
- **Descarga en PDF oficial** maquetado profesionalmente mediante `xhtml2pdf`.
- Historial completo de facturas para compradores y productores.

### 🛡️ 5. Seguridad en Profundidad (9 Capas)
- Cifrado de contraseñas con PBKDF2/Argon2 y autenticación social mediante **Google OAuth2**.
- Protección contra vulnerabilidades OWASP: Anti-CSRF, XSS auto-escaping, anti-clickjacking (`X-Frame-Options`), validación de archivos con Pillow y prevención de IDOR.
- Registro inmutable de auditoría forense (`admin_audit_logs`) con dirección IP y marcas de tiempo.

### 🔔 6. Notificaciones Flotantes (Toast Premium)
- Sistema moderno de alertas con efecto *glassmorphism*, insignias circulares por tipo de evento y barra de progreso temporizada con autocierre.

---

## 🏗️ Estructura del Repositorio

```
agrosft/
├── config/                  → Configuración global de Django (settings.py, urls.py, wsgi.py)
├── core/                    → Middlewares, context processors y templatetags compartidos
├── apps/
│   ├── usuarios/            → Autenticación, perfiles, moderación y auditoría
│   ├── inventario/          → Productos, categorías, lotes y marketplace
│   ├── ventas/              → Carrito en sesión, solicitudes, ventas y calificaciones
│   ├── clientes/            → Directorio y métricas de compradores frecuentes
│   └── facturacion/         → Emisión de facturas y exportación PDF oficial
├── frontend/                → Código fuente Vue 3 y estilos Vite
│   ├── src/layout/          → Navbar reactivo y sistema de alertas Toast
│   ├── src/marketplace/     → Componentes SPA del marketplace
│   ├── src/inventario/      → Componentes reactivos del inventario
│   └── src/carrito/         → Carrito interactivo
├── static/dist/             → Bundles compilados listos para producción (JS/CSS)
├── templates/               → Plantillas HTML base y páginas administrativas
├── docs/                    → Base de conocimiento técnico en Markdown / Obsidian
├── DOCUMENTACION_GENERAL.md → Documento maestro técnico y funcional
├── requirements.txt         → Dependencias de Python
└── package.json             → Dependencias y scripts de Vite
```

---

## 🚀 Guía de Instalación Rápida

### 1. Prerrequisitos
- **Python 3.10+** (probado en Python 3.14)
- **Node.js 18+** y `npm`
- **MariaDB 10.4+** o MySQL 8.0+

### 2. Clonar y Configurar Entorno Virtual
```bash
# Clonar el proyecto
git clone https://github.com/danieldavid-23/agrosft.git
cd agrosft

# Crear y activar entorno virtual
python -m venv env

# En Windows:
.\env\Scripts\activate

# En Linux / Mac:
source env/bin/activate
```

### 3. Instalar Dependencias
```bash
# Dependencias Backend
pip install -r requirements.txt

# Dependencias Frontend
npm install
```

### 4. Configurar Variables de Entorno
Crear un archivo `.env` en la raíz del proyecto:
```ini
DEBUG=True
SECRET_KEY=clave_secreta_agrosft_desarrollo_2026

DB_NAME=agrosft
DB_USER=root
DB_PASSWORD=tu_contraseña
DB_HOST=127.0.0.1
DB_PORT=3306

GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

### 5. Compilar Activos Frontend
```bash
npm run build
```

### 6. Migraciones y Superusuario
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 7. Ejecutar el Servidor
```bash
python manage.py runserver
```
Accede desde tu navegador a: **`http://127.0.0.1:8000/`**

---

## 🤝 Créditos y Proyecto Formativo
Desarrollado como proyecto de software para el sector agropecuario bajo la metodología de formación por proyectos del **SENA (Servicio Nacional de Aprendizaje)**.