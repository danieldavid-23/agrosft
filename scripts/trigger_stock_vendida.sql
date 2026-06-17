-- ============================================================
-- AgroSFT: Nuevo trigger trg_descontar_stock_vendida
-- ============================================================
-- PROPOSITO:
--   Cuando un movimiento cambia su tipo a 'vendida' (el vendedor
--   confirma que la venta fue completada), este trigger descuenta
--   automaticamente el stock de cada producto afectado.
--
--   Esto permite que las solicitudes de compra NO afecten el stock
--   hasta que la venta este realmente confirmada.
--
-- FLUJO:
--   1. Comprador crea solicitud (tipo='compra') → stock intacto
--   2. Vendedor acepta (tipo='venta')           → stock intacto
--   3. Vendedor marca vendido (tipo='vendida')  → stock se descuenta
--
-- EJECUCION:
--   mysql -u root -p nombre_base_datos < scripts/trigger_stock_vendida.sql
--
-- FECHA: 2026-06-17
-- ============================================================

DROP TRIGGER IF EXISTS trg_descontar_stock_vendida;

DELIMITER $$
CREATE TRIGGER trg_descontar_stock_vendida
AFTER UPDATE ON movimiento
FOR EACH ROW
BEGIN
    DECLARE v_tipo_nuevo VARCHAR(45);
    DECLARE v_tipo_viejo VARCHAR(45);

    -- Obtener tipo nuevo y viejo
    SELECT tipo_movimiento INTO v_tipo_nuevo
    FROM tipo_movimiento WHERE id_tipo_movimiento = NEW.tipo_movimiento_id_tipo_movimiento;

    SELECT tipo_movimiento INTO v_tipo_viejo
    FROM tipo_movimiento WHERE id_tipo_movimiento = OLD.tipo_movimiento_id_tipo_movimiento;

    -- Solo descontar stock cuando el tipo cambia A 'vendida' desde otro estado
    IF v_tipo_nuevo = 'vendida' AND v_tipo_viejo != 'vendida' THEN
        UPDATE tblproductos_has_tblusuarios pu
        INNER JOIN tblproductos_has_tblusuarios_has_movimiento pum
            ON pu.id_pd_us = pum.tblproductos_has_tblusuarios_id_pd_us
        SET pu.cantidad = pu.cantidad - ABS(pum.cantidad)
        WHERE pum.movimiento_id_movimiento = NEW.id_movimiento
          AND pum.cantidad != 0;
    END IF;
END$$
DELIMITER ;
