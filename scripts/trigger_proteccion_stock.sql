-- ============================================================
-- AgroSFT: Trigger consolidado con proteccion contra stock negativo
-- ============================================================
-- PROPOSITO:
--   Reemplaza trg_actualizar_stock_oferta con las siguientes mejoras:
--   1. Ignora movimientos tipo 'compra' (solicitudes pendientes)
--   2. Valida que el stock no quede negativo antes de actualizar
--   3. Emite SIGNAL error si stock seria insuficiente
--   4. Mantiene actualizacion de calificacion_promedio
--
-- PRECAUCION:
--   Ejecutar corregir_stock_negativo.sql ANTES de este script.
--   Este trigger reemplaza al de trigger_modificar_stock.sql
--   (incluye la misma logica + proteccion adicional).
--
-- EJECUCION:
--   C:\xampp\mysql\bin\mysql.exe -u root -p nombre_bd < scripts/trigger_proteccion_stock.sql
--
-- FECHA: 2026-06-17
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

    -- Solo actualizar stock si NO es una solicitud de compra
    IF v_tipo != 'compra' THEN

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
