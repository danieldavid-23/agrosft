-- ============================================================
-- AgroSFT: Insertar tipo de movimiento 'reabastecimiento'
-- ============================================================
-- PROPOSITO:
--   Garantiza la existencia del tipo de movimiento 'reabastecimiento'
--   en la tabla tipo_movimiento (idempotente).
--
-- EJECUCION:
--   mysql -u root -p nombre_base_datos < scripts/insertar_tipo_reabastecimiento.sql
--
-- FECHA: 2026-09-09
-- ============================================================

INSERT INTO tipo_movimiento (tipo_movimiento)
SELECT 'reabastecimiento'
WHERE NOT EXISTS (
    SELECT 1 FROM tipo_movimiento WHERE tipo_movimiento = 'reabastecimiento'
);