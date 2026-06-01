-- =============================================================
-- SISTEMA DE FARMACIA GENESIS
-- Base de Datos Corregida y Completa
-- MySQL Workbench Forward Engineering
-- =============================================================

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema farmacia_genesis
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `farmacia_genesis`;
CREATE SCHEMA IF NOT EXISTS `farmacia_genesis` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `farmacia_genesis`;

-- =============================================================
-- MÓDULO: PACIENTES
-- =============================================================

-- -----------------------------------------------------
-- Table `pacientes`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `pacientes` (
  `id_paciente`      INT NOT NULL AUTO_INCREMENT,
  `nombre_completo`  VARCHAR(100) NOT NULL,
  `edad`             INT NOT NULL,
  `genero`           ENUM('Masculino', 'Femenino', 'Otro') NOT NULL,
  `fecha_nacimiento` DATE NULL,
  `fecha_registro`   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_paciente`)
) ENGINE = InnoDB COMMENT = 'Datos generales de los pacientes';

-- -----------------------------------------------------
-- Table `correos`  (correos de pacientes)
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `correos` (
  `id_correo`  INT NOT NULL AUTO_INCREMENT,
  `correo`     VARCHAR(100) NOT NULL,
  `id_paciente` INT NOT NULL,
  PRIMARY KEY (`id_correo`),
  INDEX `correo_paciente_idx` (`id_paciente` ASC),
  CONSTRAINT `fk_correo_paciente`
    FOREIGN KEY (`id_paciente`)
    REFERENCES `pacientes` (`id_paciente`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT = 'Correos electrónicos de los pacientes';

-- -----------------------------------------------------
-- Table `telefonos_pacientes`  ← CORREGIDO (antes era "telefonos" duplicada)
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telefonos_pacientes` (
  `id_telefono` INT NOT NULL AUTO_INCREMENT,
  `telefono`    VARCHAR(20) NOT NULL,          -- ← CORREGIDO: VARCHAR en lugar de FLOAT
  `id_paciente` INT NOT NULL,
  PRIMARY KEY (`id_telefono`),
  INDEX `telefono_paciente_idx` (`id_paciente` ASC),
  CONSTRAINT `fk_telefono_paciente`
    FOREIGN KEY (`id_paciente`)
    REFERENCES `pacientes` (`id_paciente`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT = 'Teléfonos de los pacientes';

-- -----------------------------------------------------
-- Table `direcciones`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `direcciones` (
  `id_direccion`  INT NOT NULL AUTO_INCREMENT,
  `departamento`  VARCHAR(60) NOT NULL,
  `municipio`     VARCHAR(60) NOT NULL,
  `numero_casa`   VARCHAR(20) NULL,
  `calle`         VARCHAR(60) NULL,
  `zona`          VARCHAR(20) NULL,
  `colonia`       VARCHAR(60) NULL,
  `referencia`    VARCHAR(100) NOT NULL,
  `id_paciente`   INT NOT NULL,
  PRIMARY KEY (`id_direccion`),
  INDEX `direccion_paciente_idx` (`id_paciente` ASC),
  CONSTRAINT `fk_direccion_paciente`
    FOREIGN KEY (`id_paciente`)
    REFERENCES `pacientes` (`id_paciente`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT = 'Direcciones de los pacientes';

-- -----------------------------------------------------
-- Table `historiales_medicos`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `historiales_medicos` (
  `id_historial`  INT NOT NULL AUTO_INCREMENT,
  `enfermedad`    VARCHAR(150) NOT NULL,
  `alergia`       VARCHAR(150) NOT NULL,
  `observacion`   VARCHAR(255) NOT NULL,
  `id_paciente`   INT NOT NULL,
  `fecha_registro` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_historial`),
  INDEX `historial_paciente_idx` (`id_paciente` ASC),
  CONSTRAINT `fk_historial_paciente`
    FOREIGN KEY (`id_paciente`)
    REFERENCES `pacientes` (`id_paciente`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT = 'Historial médico de los pacientes';

-- =============================================================
-- MÓDULO: MÉDICOS Y CLÍNICA
-- =============================================================

-- -----------------------------------------------------
-- Table `medicos`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `medicos` (
  `id_medico`    INT NOT NULL AUTO_INCREMENT,
  `nombre`       VARCHAR(100) NOT NULL,
  `especialidad` VARCHAR(80) NOT NULL,
  `telefono`     VARCHAR(20) NOT NULL,           -- ← CORREGIDO: VARCHAR en lugar de FLOAT
  PRIMARY KEY (`id_medico`)
) ENGINE = InnoDB COMMENT = 'Médicos de la clínica';

-- -----------------------------------------------------
-- Table `citas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `citas` (
  `id_cita`    INT NOT NULL AUTO_INCREMENT,
  `fecha`      DATETIME NOT NULL,
  `motivo`     VARCHAR(150) NULL,
  `id_paciente` INT NOT NULL,
  `id_medico`  INT NOT NULL,
  PRIMARY KEY (`id_cita`),
  INDEX `cita_medico_idx`   (`id_medico` ASC),
  INDEX `cita_paciente_idx` (`id_paciente` ASC),
  CONSTRAINT `fk_cita_medico`
    FOREIGN KEY (`id_medico`)
    REFERENCES `medicos` (`id_medico`)
    ON DELETE NO ACTION ON UPDATE CASCADE,
  CONSTRAINT `fk_cita_paciente`
    FOREIGN KEY (`id_paciente`)
    REFERENCES `pacientes` (`id_paciente`)
    ON DELETE NO ACTION ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT = 'Citas médicas agendadas';

-- -----------------------------------------------------
-- Table `estados_citas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `estados_citas` (
  `id_estado`   INT NOT NULL AUTO_INCREMENT,
  `nombre`      ENUM('Pendiente','Confirmada','Completada','Cancelada') NOT NULL DEFAULT 'Pendiente',
  `descripcion` VARCHAR(100) NULL,
  `fecha_cambio` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `id_cita`     INT NOT NULL,
  PRIMARY KEY (`id_estado`),
  INDEX `cita_estado_idx` (`id_cita` ASC),
  CONSTRAINT `fk_estado_cita`
    FOREIGN KEY (`id_cita`)
    REFERENCES `citas` (`id_cita`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT = 'Estados de las citas médicas';

-- -----------------------------------------------------
-- Table `consultas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `consultas` (
  `id_consulta`  INT NOT NULL AUTO_INCREMENT,
  `fecha`        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `tratamiento`  VARCHAR(255) NOT NULL,
  `diagnostico`  VARCHAR(255) NOT NULL,
  `id_paciente`  INT NOT NULL,
  `id_medico`    INT NOT NULL,
  PRIMARY KEY (`id_consulta`),
  INDEX `consulta_medico_idx`   (`id_medico` ASC),
  INDEX `consulta_paciente_idx` (`id_paciente` ASC),
  CONSTRAINT `fk_consulta_medico`
    FOREIGN KEY (`id_medico`)
    REFERENCES `medicos` (`id_medico`)
    ON DELETE NO ACTION ON UPDATE CASCADE,
  CONSTRAINT `fk_consulta_paciente`
    FOREIGN KEY (`id_paciente`)
    REFERENCES `pacientes` (`id_paciente`)
    ON DELETE NO ACTION ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT = 'Consultas médicas realizadas';

-- -----------------------------------------------------
-- Table `recetas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `recetas` (
  `id_receta`   INT NOT NULL AUTO_INCREMENT,
  `fecha`       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `id_consulta` INT NOT NULL,
  PRIMARY KEY (`id_receta`),
  INDEX `receta_consulta_idx` (`id_consulta` ASC),
  CONSTRAINT `fk_receta_consulta`
    FOREIGN KEY (`id_consulta`)
    REFERENCES `consultas` (`id_consulta`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT = 'Recetas médicas generadas en consulta';

-- -----------------------------------------------------
-- Table `detalles_recetas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `detalles_recetas` (
  `id_detalle`    INT NOT NULL AUTO_INCREMENT,
  `cantidad`      INT NOT NULL,                -- ← CORREGIDO: INT en lugar de FLOAT
  `dosis`         VARCHAR(100) NOT NULL,
  `instrucciones` VARCHAR(255) NULL,
  `id_receta`     INT NOT NULL,
  `id_medicamento` INT NOT NULL,
  PRIMARY KEY (`id_detalle`),
  INDEX `detalle_receta_idx`       (`id_receta` ASC),
  INDEX `detalle_med_receta_idx`   (`id_medicamento` ASC),
  CONSTRAINT `fk_detalle_receta`
    FOREIGN KEY (`id_receta`)
    REFERENCES `recetas` (`id_receta`)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_detalle_med_receta`
    FOREIGN KEY (`id_medicamento`)
    REFERENCES `medicamentos` (`id_medicamento`)
    ON DELETE NO ACTION ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT = 'Medicamentos dentro de cada receta';

-- =============================================================
-- MÓDULO: MEDICAMENTOS E INVENTARIO
-- =============================================================

-- -----------------------------------------------------
-- Table `medicamentos`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `medicamentos` (
  `id_medicamento` INT NOT NULL AUTO_INCREMENT,
  `nombre`         VARCHAR(100) NOT NULL,
  `precio`         DECIMAL(10,2) NOT NULL,     -- ← CORREGIDO: DECIMAL en lugar de FLOAT
  `stock`          INT NOT NULL DEFAULT 0,     -- ← CORREGIDO: INT en lugar de FLOAT
  `descripcion`    VARCHAR(255) NULL,
  `unidad_medida`  VARCHAR(30) NULL,           -- ej: "tabletas", "ml", "frascos"
  PRIMARY KEY (`id_medicamento`)
) ENGINE = InnoDB COMMENT = 'Catálogo de medicamentos';

-- -----------------------------------------------------
-- Table `tipos_medicamentos`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `tipos_medicamentos` (
  `id_tipo`        INT NOT NULL AUTO_INCREMENT,
  `nombre`         VARCHAR(60) NOT NULL,
  `descripcion`    VARCHAR(150) NOT NULL,
  `id_medicamento` INT NOT NULL,
  PRIMARY KEY (`id_tipo`),
  INDEX `tipo_medicamento_idx` (`id_medicamento` ASC),
  CONSTRAINT `fk_tipo_medicamento`
    FOREIGN KEY (`id_medicamento`)
    REFERENCES `medicamentos` (`id_medicamento`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT = 'Clasificación/tipo de cada medicamento';

-- -----------------------------------------------------
-- Table `movimientos_inventarios`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `movimientos_inventarios` (
  `id_movimiento`  INT NOT NULL AUTO_INCREMENT,
  `tipo_movimiento` ENUM('Entrada','Salida') NOT NULL,  -- ← CORREGIDO: ENUM claro
  `cantidad`       INT NOT NULL,
  `stock_anterior` INT NOT NULL,
  `stock_nuevo`    INT NOT NULL,
  `fecha`          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `motivo`         VARCHAR(150) NULL,
  `id_medicamento` INT NOT NULL,
  PRIMARY KEY (`id_movimiento`),
  INDEX `movimiento_medicamento_idx` (`id_medicamento` ASC),
  CONSTRAINT `fk_movimiento_medicamento`
    FOREIGN KEY (`id_medicamento`)
    REFERENCES `medicamentos` (`id_medicamento`)
    ON DELETE NO ACTION ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT = 'Registro de todos los movimientos de stock';

-- -----------------------------------------------------
-- Table `lotes_medicamentos`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `lotes_medicamentos` (
  `id_lote`          INT NOT NULL AUTO_INCREMENT,
  `numero_lote`      VARCHAR(50) NULL,
  `fecha_vencimiento` DATE NOT NULL,
  `cantidad`         INT NOT NULL,
  `id_medicamento`   INT NOT NULL,
  `id_movimiento`    INT NOT NULL,
  PRIMARY KEY (`id_lote`),
  INDEX `lote_medicamento_idx`  (`id_medicamento` ASC),
  INDEX `lote_movimiento_idx`   (`id_movimiento` ASC),
  CONSTRAINT `fk_lote_medicamento`
    FOREIGN KEY (`id_medicamento`)
    REFERENCES `medicamentos` (`id_medicamento`)
    ON DELETE NO ACTION ON UPDATE CASCADE,
  CONSTRAINT `fk_lote_movimiento`
    FOREIGN KEY (`id_movimiento`)
    REFERENCES `movimientos_inventarios` (`id_movimiento`)
    ON DELETE NO ACTION ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT = 'Lotes de medicamentos con fecha de vencimiento';

-- =============================================================
-- MÓDULO: VENTAS Y PAGOS
-- =============================================================

-- -----------------------------------------------------
-- Table `ventas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ventas` (
  `id_venta`   INT NOT NULL AUTO_INCREMENT,
  `fecha`      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `total`      DECIMAL(10,2) NOT NULL,         -- ← CORREGIDO: DECIMAL
  `id_paciente` INT NOT NULL,
  PRIMARY KEY (`id_venta`),
  INDEX `venta_paciente_idx` (`id_paciente` ASC),
  CONSTRAINT `fk_venta_paciente`
    FOREIGN KEY (`id_paciente`)
    REFERENCES `pacientes` (`id_paciente`)
    ON DELETE NO ACTION ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT = 'Ventas realizadas a pacientes';

-- -----------------------------------------------------
-- Table `detalles_ventas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `detalles_ventas` (
  `id_detalle`     INT NOT NULL AUTO_INCREMENT,
  `cantidad`       INT NOT NULL,               -- ← CORREGIDO: INT
  `precio_unitario` DECIMAL(10,2) NOT NULL,   -- ← CORREGIDO: DECIMAL + nombre más claro
  `subtotal`       DECIMAL(10,2) NOT NULL,
  `id_medicamento` INT NOT NULL,
  `id_venta`       INT NOT NULL,
  PRIMARY KEY (`id_detalle`),
  INDEX `detalle_medicamento_venta_idx` (`id_medicamento` ASC),
  INDEX `detalle_venta_idx`             (`id_venta` ASC),
  CONSTRAINT `fk_detalle_medicamento_venta`
    FOREIGN KEY (`id_medicamento`)
    REFERENCES `medicamentos` (`id_medicamento`)
    ON DELETE NO ACTION ON UPDATE CASCADE,
  CONSTRAINT `fk_detalle_venta`
    FOREIGN KEY (`id_venta`)
    REFERENCES `ventas` (`id_venta`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT = 'Detalle de medicamentos por venta';

-- -----------------------------------------------------
-- Table `pagos`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `pagos` (
  `id_pago`  INT NOT NULL AUTO_INCREMENT,
  `monto`    DECIMAL(10,2) NOT NULL,           -- ← CORREGIDO: DECIMAL
  `fecha`    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `id_venta` INT NOT NULL,
  PRIMARY KEY (`id_pago`),
  INDEX `pagos_venta_idx` (`id_venta` ASC),
  CONSTRAINT `fk_pago_venta`
    FOREIGN KEY (`id_venta`)
    REFERENCES `ventas` (`id_venta`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT = 'Pagos realizados por ventas';

-- -----------------------------------------------------
-- Table `metodos_pagos`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `metodos_pagos` (
  `id_metodo` INT NOT NULL AUTO_INCREMENT,
  `tipo`      ENUM('Efectivo','Tarjeta de Crédito','Tarjeta de Débito','Transferencia','Otro') NOT NULL,
  `id_pago`   INT NOT NULL,
  PRIMARY KEY (`id_metodo`),
  INDEX `metodo_pago_idx` (`id_pago` ASC),
  CONSTRAINT `fk_metodo_pago`
    FOREIGN KEY (`id_pago`)
    REFERENCES `pagos` (`id_pago`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT = 'Método de pago utilizado en cada pago';

-- =============================================================
-- MÓDULO: PROVEEDORES Y COMPRAS
-- =============================================================

-- -----------------------------------------------------
-- Table `proveedores`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `proveedores` (
  `id_proveedor` INT NOT NULL AUTO_INCREMENT,
  `nombre`       VARCHAR(100) NOT NULL,
  `direccion`    VARCHAR(150) NOT NULL,
  `correo`       VARCHAR(100) NOT NULL,
  PRIMARY KEY (`id_proveedor`)
) ENGINE = InnoDB COMMENT = 'Proveedores de medicamentos';

-- -----------------------------------------------------
-- Table `telefonos_proveedores`  ← CORREGIDO (antes era "telefonos" duplicada)
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `telefonos_proveedores` (
  `id_telefono`  INT NOT NULL AUTO_INCREMENT,
  `telefono`     VARCHAR(20) NOT NULL,          -- ← CORREGIDO: VARCHAR
  `id_proveedor` INT NOT NULL,
  PRIMARY KEY (`id_telefono`),
  INDEX `telefono_proveedor_idx` (`id_proveedor` ASC),
  CONSTRAINT `fk_telefono_proveedor`
    FOREIGN KEY (`id_proveedor`)
    REFERENCES `proveedores` (`id_proveedor`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT = 'Teléfonos de los proveedores';

-- -----------------------------------------------------
-- Table `compras`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `compras` (
  `id_compra`    INT NOT NULL AUTO_INCREMENT,
  `fecha`        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `total`        DECIMAL(10,2) NOT NULL,        -- ← CORREGIDO: DECIMAL
  `id_proveedor` INT NOT NULL,
  PRIMARY KEY (`id_compra`),
  INDEX `compra_proveedor_idx` (`id_proveedor` ASC),
  CONSTRAINT `fk_compra_proveedor`
    FOREIGN KEY (`id_proveedor`)
    REFERENCES `proveedores` (`id_proveedor`)
    ON DELETE NO ACTION ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT = 'Órdenes de compra a proveedores';

-- -----------------------------------------------------
-- Table `detalles_compras`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `detalles_compras` (
  `id_detalle`    INT NOT NULL AUTO_INCREMENT,
  `cantidad`      INT NOT NULL,                -- ← CORREGIDO: INT
  `precio_compra` DECIMAL(10,2) NOT NULL,     -- ← CORREGIDO: DECIMAL
  `subtotal`      DECIMAL(10,2) NOT NULL,
  `id_compra`     INT NOT NULL,
  `id_medicamento` INT NOT NULL,
  PRIMARY KEY (`id_detalle`),
  INDEX `detalle_medicamento_compra_idx` (`id_medicamento` ASC),
  INDEX `detalle_compra_idx`             (`id_compra` ASC),
  CONSTRAINT `fk_detalle_medicamento_compra`
    FOREIGN KEY (`id_medicamento`)
    REFERENCES `medicamentos` (`id_medicamento`)
    ON DELETE NO ACTION ON UPDATE CASCADE,
  CONSTRAINT `fk_detalle_compra`
    FOREIGN KEY (`id_compra`)
    REFERENCES `compras` (`id_compra`)
    ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT = 'Detalle de medicamentos por compra';

-- =============================================================
-- MÓDULO: USUARIOS Y AUTENTICACIÓN  ← NUEVO
-- =============================================================

-- -----------------------------------------------------
-- Table `usuarios`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `usuarios` (
  `id_usuario`      INT NOT NULL AUTO_INCREMENT,
  `nombre_usuario`  VARCHAR(60) NOT NULL UNIQUE,
  `password_hash`   VARCHAR(255) NOT NULL,
  `rol`             ENUM('admin','medico') NOT NULL DEFAULT 'medico',
  `nombre_completo` VARCHAR(100) NOT NULL,
  `activo`          TINYINT(1) NOT NULL DEFAULT 1,
  `id_medico`       INT NULL,              -- Si rol=medico, vincula al médico en el sistema
  `fecha_creacion`  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `ultimo_acceso`   DATETIME NULL,
  PRIMARY KEY (`id_usuario`),
  INDEX `usuario_medico_idx` (`id_medico` ASC),
  CONSTRAINT `fk_usuario_medico`
    FOREIGN KEY (`id_medico`)
    REFERENCES `medicos` (`id_medico`)
    ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE = InnoDB COMMENT = 'Usuarios del sistema con roles admin y medico';

-- =============================================================
-- DATOS INICIALES
-- =============================================================

-- Usuario administrador por defecto (password: Admin1234)
-- Hash bcrypt generado externamente — cambiar en primera ejecución
INSERT INTO `usuarios` (`nombre_usuario`, `password_hash`, `rol`, `nombre_completo`, `activo`)
VALUES ('admin', '$2b$12$placeholder_hash_to_be_set_on_first_run', 'admin', 'Administrador del Sistema', 1);

-- =============================================================
-- RESTAURAR CONFIGURACIÓN
-- =============================================================
SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
