  -- ============================================================================
  -- AgroSFT — Unidad de Medida para Productos
  -- ============================================================================
  -- Este script se ejecuta DIRECTAMENTE en MariaDB (la app `inventario` usa
  -- `managed = False` y `MIGRATION_MODULES = None`, por lo que Django NO gestiona
  -- este schema; se gestiona externamente, como el resto de tablas de inventario).
  --
  -- Ejecutar con:
  --   mysql -u root -p agrosft < scripts/crear_unidad_medida.sql
  -- ============================================================================

  -- ----------------------------------------------------------------------------
  -- 1. Crear la tabla de unidades de medida
  -- ----------------------------------------------------------------------------
  CREATE TABLE IF NOT EXISTS `tblunidad_medida` (
    `id_unidad` INT(11) NOT NULL AUTO_INCREMENT,
    `nombre` VARCHAR(50) NOT NULL,
    `abreviatura` VARCHAR(10) NOT NULL,
    `activo` TINYINT(1) NOT NULL DEFAULT 1,
    `created_at` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    PRIMARY KEY (`id_unidad`),
    UNIQUE KEY `uq_unidad_nombre` (`nombre`),
    UNIQUE KEY `uq_unidad_abreviatura` (`abreviatura`)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

  -- ----------------------------------------------------------------------------
  -- 2. Datos iniciales obligatorios
  -- ----------------------------------------------------------------------------
  INSERT INTO `tblunidad_medida` (`id_unidad`, `nombre`, `abreviatura`, `activo`) VALUES
    (1, 'Unidades', 'u', 1),
    (2, 'Kilogramos', 'kg', 1),
    (3, 'Libras', 'lb', 1),
    (4, 'Litros', 'L', 1),
    (5, 'Gramos', 'g', 1)
  ON DUPLICATE KEY UPDATE `nombre` = VALUES(`nombre`);

  -- ----------------------------------------------------------------------------
  -- 3. Añadir columna FK en tblproducto (nullable, default = 1 = "Unidades")
  -- ----------------------------------------------------------------------------
  ALTER TABLE `tblproducto`
    ADD COLUMN `tblunidad_medida_id_unidad` INT(11) NULL DEFAULT 1
    AFTER `tblcategoria_idt_categoria`;

  ALTER TABLE `tblproducto`
    ADD CONSTRAINT `fk_tblproductos_tblunidad_medida`
    FOREIGN KEY (`tblunidad_medida_id_unidad`)
    REFERENCES `tblunidad_medida` (`id_unidad`)
    ON DELETE NO ACTION ON UPDATE NO ACTION;