# Configuración y Entorno

> Guía completa de instalación, variables de entorno y ejecución del proyecto.

---

## Requisitos Previos

| Herramienta | Versión | Propósito |
|---|---|---|
| Python | 3.10+ | Runtime backend |
| MariaDB | 10.4+ | Base de datos |
| Node.js | 18+ | Build de frontend (Vite) |
| npm | 9+ | Gestor de paquetes JS |
| pip | 23+ | Gestor de paquetes Python |

---

## Instalación Paso a Paso

### 1. Clonar y crear entorno virtual

```bash
git clone <repo-url> agrosft
cd agrosft
python -m venv venv
```

### 2. Activar entorno virtual

```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias Python

```bash
pip install -r requirements.txt
```

**Dependencias principales** (`requirements.txt`):
- `django==6.0.2` — Framework web
- `mysqlclient==2.2.4` — Driver MariaDB
- `pillow==10.2.0` — Procesamiento de imágenes
- `python-dotenv==1.0.1` — Variables de entorno
- `social-auth-app-django` — Google OAuth2

### 4. Instalar dependencias Node.js

```bash
npm install
```

**Dependencias** (`package.json`):
- `vue@^3.5` — Framework frontend
- `vite@^6` — Bundler
- `@vitejs/plugin-vue@^5` — Plugin Vue para Vite

### 5. Configurar base de datos

1. Crear base de datos `agrosft` en MariaDB
2. Importar schema SQL existente (tablas, triggers, datos iniciales)
3. Configurar credenciales en `.env`

### 6. Compilar frontend

```bash
npm run build    # Una vez
npm run dev      # Watch mode para desarrollo
```

### 7. Ejecutar servidor

```bash
python manage.py runserver
```

Acceder en: `http://localhost:8000`

---

## Variables de Entorno (`.env`)

```env
# Django Core
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de Datos
DB_NAME=agrosft
DB_USER=root
DB_PASSWORD=tu-password-mysql
DB_HOST=127.0.0.1
DB_PORT=3306

# Seguridad (solo producción)
SECURE_SSL_REDIRECT=False

# Google OAuth2 (opcional)
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

> [!warning] SECRET_KEY
> Si no se define, Django usa un default inseguro y muestra un warning. **Nunca usar en producción.**

---

## Configuración Django (`config/settings.py`)

### Apps Instaladas

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.usuarios',
    'apps.inventario',
    'apps.clientes',
    'apps.ventas',
    'social_django',
]
```

### Migraciones Deshabilitadas

```python
MIGRATION_MODULES = {
    'usuarios': None,
    'inventario': None,
    'clientes': None,
    'ventas': None,
}
```

> [!danger] NUNCA ejecutar `makemigrations`
> Los modelos son `managed = False`. Django no debe generar ni aplicar migraciones para las apps del proyecto.

### Sesión y Caché

```python
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
SESSION_COOKIE_AGE = 1800  # 30 minutos
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
```

### URLs de Autenticación

```python
LOGIN_URL = 'usuarios:login'
LOGIN_REDIRECT_URL = 'inventario:marketplace'
LOGOUT_REDIRECT_URL = 'usuarios:login'
```

---

## Frontend Build

### Desarrollo
```bash
npm run dev  # vite build --watch (recompila en cada cambio)
```

### Producción
```bash
npm run build  # vite build → static/dist/
```

### Estructura de Output
```
static/dist/
├── marketplace.js
├── carrito.js
├── inventario.js
├── solicitudes.js
├── calificaciones.js
├── chunks/
│   └── vendor-[hash].js
└── assets/
    └── style-[hash].css
```

---

## Base de Datos — Inicialización

### Tablas requeridas
1. `tblusuarios` — Usuarios del sistema
2. `tblcategoria` — Categorías de productos
3. `estado` — Estados de publicación
4. `tipo_movimiento` — Tipos de transacción
5. `tblproducto` — Catálogo maestro
6. `tblproductos_has_tblusuarios` — Publicaciones
7. `movimiento` — Transacciones
8. `tblproductos_has_tblusuarios_has_movimiento` — Detalles
9. `calificacion` — Referencia (opcional)
10. `user_profiles` — Perfiles (opcional)

### Datos iniciales requeridos

```sql
-- Categorías
INSERT INTO tblcategoria (categoria, activo) VALUES
('Frutas', 1), ('Verduras', 1), ('Tubérculos', 1),
('Granos y Cereales', 1), ('Insumos Agrícolas', 1);

-- Estados
INSERT INTO estado (estado) VALUES
('Pendiente'), ('Aprobado'), ('Rechazado');

-- Tipos de movimiento
INSERT INTO tipo_movimiento (tipo_movimiento) VALUES
('compra'), ('venta'), ('rechazada'), ('vendida');
```

---

## Logs

Configuración en `settings.py`:
- **Consola**: StreamHandler (verbose format)
- **Archivo**: `agrosft.log` en la raíz del proyecto
- **Nivel root**: INFO
- **Nivel django**: WARNING

---

## Comandos Útiles

```bash
# Servidor de desarrollo
python manage.py runserver

# Crear superusuario
python manage.py createsuperuser

# Shell interactivo
python manage.py shell

# Verificar configuración
python manage.py check

# Colectar archivos estáticos (producción)
python manage.py collectstatic
```

> [!note] Scripts de mantenimiento
> En `scripts/` existen scripts de validación:
> - `validate_schema.py` / `validate_schema.bat` — Valida schema de BD
> - `asegurar_tipos_movimiento.py` — Crea tipos de movimiento si faltan
> - `verify_cantidad_change.py` — Verifica cambios de cantidad

---

## Enlaces Relacionados

- [[00-INDEX]] — Volver al índice
- [[02-ARQUITECTURA]] — Arquitectura del sistema
- [[03-BASE-DATOS]] — Esquema de base de datos
- [[11-CONVENCIONES]] — Estándares de desarrollo
