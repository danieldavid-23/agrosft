-- ============================================================
-- AgroSFT: Modificacion del trigger trg_actualizar_stock_oferta
-- ============================================================
-- PROPOSITO:
--   El trigger original descontaba stock en CUALQUIER insercion
--   en tblproductos_has_tblusuarios_has_movimiento, incluyendo
--   las solicitudes de compra (tipo='compra').
--
--   Con el nuevo flujo, el stock SOLO debe descontarse cuando
--   la venta se marca como "vendida", no al crear la solicitud.
--
--   Este trigger modificado OMITE la actualizacion de stock
--   cuando el movimiento es de tipo 'compra' (solicitud pendiente).
--
-- EJECUCION:
--   mysql -u root -p nombre_base_datos < scripts/trigger_modificar_stock.sql
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

    -- Obtener el tipo de movimiento asociado
    SELECT tm.tipo_movimiento INTO v_tipo
    FROM movimiento m
    JOIN tipo_movimiento tm ON m.tipo_movimiento_id_tipo_movimiento = tm.id_tipo_movimiento
    WHERE m.id_movimiento = NEW.movimiento_id_movimiento;

    -- Solo actualizar stock si NO es una solicitud de compra
    -- Las solicitudes de compra (tipo='compra') no deben afectar stock
    -- hasta que el vendedor marque la venta como 'vendida'
    IF v_tipo != 'compra' THEN
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
