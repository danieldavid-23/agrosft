-- =============================================================
-- AGROSFT — Agregar columna `imagen` a la tabla `tblproducto`
-- =============================================================
-- Contexto:
--   La columna `imagen` (VARCHAR(255) NULL) ya fue aplicada en MariaDB
--   (verificado 2026-08-20 via information_schema, posicion 7 despues de
--   `descripcion`). Este script es de REFERENCIA/REPRODUCIBILIDAD y es
--   IDEMPOTENTE: si la columna ya existe, no hace nada.
--
--   NOTA: El proyecto NO usa migraciones Django (MIGRATION_MODULES = None
--   y modelos con managed = False). El schema se gestiona externamente.
--
--   Ver docs/DECISIONS.md ADR-012.
-- =============================================================

SET @existe := (
    SELECT COUNT(*) FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE()
      AND TABLE_NAME   = 'tblproducto'
      AND COLUMN_NAME  = 'imagen'
);

SET @sql := IF(
    @existe = 0,
    'ALTER TABLE `tblproducto`
     ADD COLUMN `imagen` VARCHAR(255) NULL DEFAULT NULL AFTER `descripcion`',
    'SELECT ''La columna `imagen` ya existe en tblproducto; no se ejecuta ALTER.'''
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;