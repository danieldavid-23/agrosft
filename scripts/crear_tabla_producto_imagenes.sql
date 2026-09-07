-- =============================================================
-- AGROSFT — Crear tabla `tblproducto_imagenes` para carrusel
-- =============================================================
-- Contexto:
--   Permite almacenar múltiples imágenes por producto para ser
--   desplegadas en un carrusel interactivo en el marketplace e inventario.
--   La tabla principal `tblproducto` mantiene la columna `imagen`
--   para la imagen principal de portada (compatibilidad hacia atrás).
--
--   NOTA: El proyecto NO usa migraciones Django (MIGRATION_MODULES = None
--   y modelos con managed = False). El schema se gestiona externamente.
--
--   Ver docs/DECISIONS.md ADR-014.
-- =============================================================

CREATE TABLE IF NOT EXISTS `tblproducto_imagenes` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `id_producto` INT NOT NULL,
    `imagen` VARCHAR(255) NOT NULL,
    `orden` INT NOT NULL DEFAULT 0,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX `idx_producto_imagenes_producto` (`id_producto`),
    CONSTRAINT `fk_producto_imagenes_producto`
        FOREIGN KEY (`id_producto`)
        REFERENCES `tblproducto` (`id_productos`)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
