-- ============================================================
-- AgroSFT: Correccion de stock negativo por trigger viejo
-- ============================================================
-- PROPOSITO:
--   El trigger original trg_actualizar_stock_oferta descontaba
--   stock en CUALQUIER insercion, incluyendo solicitudes de
--   compra (tipo='compra') que NO debian afectar el stock.
--
--   Este script revierte esos descuentos incorrectos devolviendo
--   las cantidades negativas al stock de cada ProductoUsuario.
--
-- PRECAUCION:
--   Ejecutar ANTES de instalar los triggers nuevos.
--   Solo afecta productos donde movimientos 'compra' generaron
--   stock negativo. Los demas no se tocan.
--
-- EJECUCION:
--   C:\xampp\mysql\bin\mysql.exe -u root -p nombre_bd < scripts/corregir_stock_negativo.sql
--
-- FECHA: 2026-06-17
-- ============================================================

-- ============================================================
-- PASO 1: Ver productos afectados (solo informativo)
-- ============================================================
SELECT '=== PRODUCTOS CON STOCK AFECTADO POR SOLICITUDES DE COMPRA ===' AS '';

SELECT 
    pu.id_pd_us,
    p.nombre AS producto,
    u.nombres AS vendedor,
    pu.cantidad AS stock_actual,
    SUM(pum.cantidad) AS descuento_incorrecto,
    pu.cantidad - SUM(pum.cantidad) AS stock_corregido
FROM tblproductos_has_tblusuarios pu
JOIN tblproducto p ON pu.tblproductos_id_productos = p.id_productos
JOIN tblusuarios u ON pu.tblusuarios_id_users = u.id_users
JOIN tblproductos_has_tblusuarios_has_movimiento pum
  ON pu.id_pd_us = pum.tblproductos_has_tblusuarios_id_pd_us
JOIN movimiento m ON pum.movimiento_id_movimiento = m.id_movimiento
JOIN tipo_movimiento tm ON m.tipo_movimiento_id_tipo_movimiento = tm.id_tipo_movimiento
WHERE tm.tipo_movimiento = 'compra'
GROUP BY pu.id_pd_us, p.nombre, u.nombres, pu.cantidad
HAVING SUM(pum.cantidad) < 0;

-- ============================================================
-- PASO 2: Revertir descuentos incorrectos
-- ============================================================
SELECT '=== CORRIGIENDO STOCK ===' AS '';

UPDATE tblproductos_has_tblusuarios pu
JOIN (
    SELECT 
        pum.tblproductos_has_tblusuarios_id_pd_us AS id_pd_us,
        SUM(pum.cantidad) AS total_descontado
    FROM tblproductos_has_tblusuarios_has_movimiento pum
    JOIN movimiento m ON pum.movimiento_id_movimiento = m.id_movimiento
    JOIN tipo_movimiento tm ON m.tipo_movimiento_id_tipo_movimiento = tm.id_tipo_movimiento
    WHERE tm.tipo_movimiento = 'compra'
    GROUP BY pum.tblproductos_has_tblusuarios_id_pd_us
    HAVING SUM(pum.cantidad) < 0
) AS correccion ON pu.id_pd_us = correccion.id_pd_us
SET pu.cantidad = pu.cantidad - correccion.total_descontado;

-- total_descontado es negativo, asi que restar un negativo = sumar (devolver stock)

-- ============================================================
-- PASO 3: Verificar resultado
-- ============================================================
SELECT '=== VERIFICACION POST-CORRECCION ===' AS '';

SELECT 
    pu.id_pd_us,
    p.nombre AS producto,
    pu.cantidad AS stock_corregido
FROM tblproductos_has_tblusuarios pu
JOIN tblproducto p ON pu.tblproductos_id_productos = p.id_productos
WHERE pu.cantidad < 0;

SELECT '=== Si no aparecen filas arriba, no hay stock negativo restante ===' AS '';
