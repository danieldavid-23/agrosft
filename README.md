# AgroSFT

Proyecto de gestión agrícola del SENA: plataforma web para conectar agricultores y compradores (catálogo, ventas, compras, facturación y calificaciones).

## Stack

| Capa | Tecnología |
|---|---|
| Backend | Django 5.0.14 (Python) |
| Base de datos | MariaDB 10.4 (schema legacy; la app `facturacion` usa migraciones Django) |
| Frontend | Vue.js 3.5 (SPA parcial) + Vite 6 + Bootstrap 5.1.3 + Font Awesome 6.4 |
| PDF | xhtml2pdf |
| OAuth | social-auth-app-django (Google, configurado) |

## Módulos (apps Django)

- `apps/usuarios` — Autenticación, registro, perfil, panel admin, OAuth
- `apps/inventario` — Catálogo de productos, marketplace, aprobación admin
- `apps/ventas` — Carrito, solicitudes, ventas, compras, calificaciones
- `apps/clientes` — Historial de compradores
- `apps/facturacion` — Facturas, historial y PDF
- `core` — Clases base, middleware y utilidades compartidas
- `frontend/src/` — Componentes Vue 3 (nav, footer, marketplace, carrito, inventario, calificaciones)

## Estructura del Proyecto

```
agrosft/
├── config/       → Settings, URLs raíz, WSGI/ASGI
├── core/         → Clases base, middleware, utilidades
├── apps/         → Aplicaciones Django (usuarios, inventario, ventas, clientes, facturacion)
├── frontend/src/ → Componentes Vue 3 + layout
├── templates/    → Plantillas HTML
├── static/dist/  → Assets compilados por Vite
├── media/        → Archivos subidos por usuarios
├── scripts/      → Scripts de mantenimiento y validación
└── docs/         → Documentación SDD completa
```

## Instalación

```bash
# 1. Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate          # Windows (Linux/macOS: source venv/bin/activate)

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno (datos de MariaDB, EMAIL, SECRET_KEY)

# 4. Preparar la base de datos
#    - El schema principal es legacy (gestionado externamente en MariaDB).
#    - Solo la app de facturación usa migraciones Django:
python manage.py migrate facturacion

# 5. Compilar los assets del frontend (Vite)
#    Requiere Node.js. Salida en static/dist.
cd frontend
npm install
npm run build
cd ..

# 6. Ejecutar el servidor de desarrollo
python manage.py runserver
```

> **Importante**: los modelos de `usuarios`, `inventario`, `ventas` y `clientes` usan `managed = False` (el schema se gestiona fuera de Django). `facturacion` es la única app con migraciones activas. Ver `docs/PROJECT_CONTEXT.md` y `docs/DECISIONS.md`.

## Documentación

La documentación completa (metodología SDD) vive en `docs/`: arquitectura, base de datos, API, ADRs, roadmap y changelog. Empieza en `docs/00-INDEX.md`.