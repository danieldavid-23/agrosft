# Módulo de Facturación y Comprobantes

> Generación contable, emisión de comprobantes oficiales y descarga de facturas en PDF.

**App**: `apps.facturacion` | **Namespace**: `facturacion` | **URL prefix**: `/facturacion/`

---

## 1. Propósito del Módulo
El módulo de facturación es el componente encargado de formalizar las transacciones comerciales originadas en el sistema (tanto compras a través del marketplace como ventas directas de mostrador). Garantiza la inmutabilidad de los precios y cantidades pactadas al momento de la venta, desglosa el marco tributario agropecuario (IVA 0% Régimen Agrícola) y emite comprobantes digitales en PDF.

---

## 2. Estructura de Archivos

```
apps/facturacion/
├── admin.py                    → Configuración del panel de administración Django
├── apps.py                     → Configuración de la App Facturación
├── controllers/
│   ├── __init__.py
│   └── factura_controller.py   → Controladores web: detalle, historial, generación PDF
├── models.py                   → Modelos Factura e ItemFactura
├── services/
│   └── factura_service.py      → Lógica transaccional de creación y cancelación
├── templates/facturacion/
│   ├── detalle_factura.html    → Vista web comercial moderna con diseño institucional
│   ├── factura_pdf.html        → Plantilla optimizada para motor de PDF xhtml2pdf
│   └── historial_facturas.html → Listado con badges de estado y descarga directa
└── urls.py                     → Definición de rutas y endpoints del módulo
```

---

## 3. Modelos de Datos

### 3.1 Modelo: `Factura`
Representa el encabezado contable del comprobante de venta.

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id_factura` | AutoField | PK | Identificador único de la factura. |
| `usuario` | ForeignKey | `settings.AUTH_USER_MODEL`, CASCADE | Comprador o receptor de la factura. |
| `movimiento` | ForeignKey | `ventas.Movimiento`, SET_NULL, Null=True | Movimiento de inventario/transacción asociado. |
| `total` | DecimalField | `max_digits=12, decimal_places=2` | Monto total liquidado de la factura. |
| `metodo_pago_nombre` | CharField | `max_length=60, blank=True` | Método utilizado (Contado, Transferencia, Directo). |
| `estado` | CharField | `choices=[('emitida', 'Emitida'), ('cancelada', 'Cancelada')]` | Estado actual del comprobante. |
| `payer_email` | EmailField | `max_length=255, blank=True` | Correo de facturación del cliente. |
| `creada_en` | DateTimeField | `auto_now_add=True` | Fecha y hora exacta de emisión. |
| `pdf_generado` | BooleanField | `default=False` | Bandera que indica si ya se descargó el PDF. |

### 3.2 Modelo: `ItemFactura`
Líneas de detalle de los productos incluidos en la factura.

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id_item` | AutoField | PK | Identificador del renglón. |
| `factura` | ForeignKey | `Factura`, CASCADE, `related_name='items'` | Factura a la que pertenece el ítem. |
| `producto` | ForeignKey | `inventario.Producto`, SET_NULL, Null=True | Producto maestro vendido. |
| `descripcion` | CharField | `max_length=255` | Nombre limpio del producto (sin datos de usuario). |
| `cantidad` | DecimalField | `max_digits=10, decimal_places=2` | Cantidad vendida (unidades o kilogramos). |
| `precio_unitario` | DecimalField | `max_digits=12, decimal_places=2` | Precio por unidad al momento de la venta. |
| `subtotal` | DecimalField | `max_digits=12, decimal_places=2` | `cantidad * precio_unitario`. |

#### Propiedades del Modelo:
- **`nombre_producto_limpio`**: Retorna el nombre puro del producto, aislando cualquier sufijo de usuario o vendedor anterior.
- **`cantidad_formateada`**: Retorna la cantidad como entero si no contiene decimales (ej. `1` en lugar de `1,00`), o con formato de coma si tiene decimales reales (ej. `2,5`).

---

## 4. Servicios de Negocio (`FacturaService`)

La clase `FacturaService` encapsula las transacciones atómicas de facturación:

- **`crear_factura_desde_carrito(usuario, carrito)`**:
  1. Crea un `Movimiento` tipo `'compra'`.
  2. Itera los ítems del carrito registrando `ProductoUsuarioMovimiento` con cantidad negativa (descuento de stock).
  3. Crea la `Factura` en estado `emitida`.
  4. Crea los registros `ItemFactura` con los nombres limpios y montos calculados.
  5. Ejecuta todo el proceso bajo `@transaction.atomic`.
- **`obtener_o_crear_factura_desde_movimiento(usuario, movimiento)`**:
  - Recupera la factura existente para un movimiento o la genera automáticamente a partir de los detalles registrados en `ProductoUsuarioMovimiento`.
- **`cancelar_factura(factura)`**:
  - Actualiza el estado a `'cancelada'` y limpia la relación con el movimiento si corresponde.
- **`historial_usuario(usuario)`**:
  - Consulta ordenada de facturas correspondientes al usuario autenticado.

---

## 5. Controladores y Vistas (`factura_controller.py`)

| Vista | Método | Decoradores | Descripción |
|---|---|---|---|
| `detalle_factura` | GET | `@login_required` | Renderiza `detalle_factura.html` con select_related optimizado. |
| `historial_facturas` | GET | `@login_required` | Renderiza `historial_facturas.html` con todas las facturas del usuario. |
| `generar_pdf_factura`| GET | `@login_required` | Renderiza `factura_pdf.html` y compila el PDF mediante `xhtml2pdf`. Soporta parámetro `?descargar=1` para forzar descarga. |
| `generar_factura_pedido` | GET | `@login_required`| Genera el PDF a partir del identificador de un movimiento. |

---

## 6. Generación de PDF con `xhtml2pdf`

La generación de PDF se basa en la plantilla [`factura_pdf.html`](file:///c:/Users/daniel/Downloads/agrosft%20GIT%20HUB%20--CONECCION/apps/facturacion/templates/facturacion/factura_pdf.html):
- **Codificación:** Utiliza `encoding='utf-8'` y meta tag `Content-Type` compatible con caracteres en español.
- **Tipografía Segura:** Emplea familias compatibles con ReportLab Type-1 (Helvetica/Arial) sustituyendo glifos no imprimibles.
- **Diseño Corporativo:**
  - Encabezado con marca AgroSFT y numeración correlativa `FAC-00000X`.
  - Cuadrícula de datos de cliente y forma de pago.
  - Tabla de productos con cabecera verde institucional `#15803d` y filas alternadas.
  - Sección de totales destacada y pie de página legal con valor probatorio.
