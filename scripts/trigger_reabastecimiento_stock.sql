-- ============================================================
-- AgroSFT: Trigger consolidado con soporte para 'reabastecimiento'
-- ============================================================
-- PROPOSITO:
--   Reemplaza trg_actualizar_stock_oferta con la siguiente logica:
--   1. SUMA stock cuando el tipo de movimiento es de entrada
--      ('venta' = abastecimiento, 'reabastecimiento').
--   2. Ignora movimientos tipo 'compra' (solicitudes pendientes).
--   3. Valida que el stock no quede negativo antes de descontar.
--   4. Emite SIGNAL error si stock seria insuficiente.
--   5. Mantiene actualizacion de calificacion_promedio.
--
-- PRECAUCION:
--   La cantidad en tblproductos_has_tblusuarios_has_movimiento es:
--     - Positiva = entrada/abastecimiento (se SUMA)
--     - Negativa = salida/venta (se RESTA)
--
-- EJECUCION:
--   mysql -u root -p nombre_base_datos < scripts/trigger_reabastecimiento_stock.sql
--
-- FECHA: 2026-09-09
-- ============================================================

DROP TRIGGER IF EXISTS trg_actualizar_stock_oferta;

DELIMITER $$
CREATE TRIGGER trg_actualizar_stock_oferta
AFTER INSERT ON tblproductos_has_tblusuarios_has_movimiento
FOR EACH ROW
BEGIN
    DECLARE v_tipo VARCHAR(45);
    DECLARE v_stock_actual DECIMAL(10,2);

    -- Obtener el tipo de movimiento asociado
    SELECT tm.tipo_movimiento INTO v_tipo
    FROM movimiento m
    JOIN tipo_movimiento tm ON m.tipo_movimiento_id_tipo_movimiento = tm.id_tipo_movimiento
    WHERE m.id_movimiento = NEW.movimiento_id_movimiento;

    -- Solo actualizar stock para tipos que afectan el inventario
    -- ('venta' legacy = abastecimiento y 'reabastecimiento' suman stock).
    IF v_tipo IN ('venta', 'reabastecimiento') THEN

        -- Proteccion: validar que no quede stock negativo (solo para salidas)
        IF NEW.cantidad < 0 THEN
            SELECT cantidad INTO v_stock_actual
            FROM tblproductos_has_tblusuarios
            WHERE id_pd_us = NEW.tblproductos_has_tblusuarios_id_pd_us;

            IF v_stock_actual + NEW.cantidad < 0 THEN
                SIGNAL SQLSTATE '45000'
                SET MESSAGE_TEXT = 'Stock insuficiente: la cantidad solicitada excede el stock disponible';
            END IF;
        END IF;

        -- Actualizar stock
        UPDATE tblproductos_has_tblusuarios
        SET cantidad = cantidad + NEW.cantidad
        WHERE id_pd_us = NEW.tblproductos_has_tblusuarios_id_pd_us;
    END IF;

    -- Actualizar calificacion promedio (se mantiene sin cambios)
    IF NEW.calificacion IS NOT NULL THEN
        UPDATE tblproductos_has_tblusuarios pu
        SET pu.calificacion_promedio = (
            SELECT AVG(pum.calificacion)
            FROM tblproductos_has_tblusuarios_has_movimiento pum
            WHERE pum.tblproductos_has_tblusuarios_id_pd_us = pu.id_pd_us
              AND pum.calificacion IS NOT NULL
        )
        WHERE pu.id_pd_us = NEW.tblproductos_has_tblusuarios_id_pd_us;
    END IF;
END$$
DELIMITER ;