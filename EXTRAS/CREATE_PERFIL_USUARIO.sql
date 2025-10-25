-- ================================================
-- Script para crear tabla PERFIL_USUARIO
-- RoomFlow - Sistema de Gestión Hotelera
-- ================================================

-- Crear tabla PERFIL_USUARIO
CREATE TABLE IF NOT EXISTS PERFIL_USUARIO (
    perfil_id INT(10) NOT NULL AUTO_INCREMENT,
    usuario_id INT(10) NOT NULL,
    nombres VARCHAR(50),
    apellido_paterno VARCHAR(50),
    apellido_materno VARCHAR(50),
    tipo_documento_id INT(10),
    num_documento VARCHAR(20),
    sexo CHAR(1),
    telefono VARCHAR(9),
    PRIMARY KEY (perfil_id),
    UNIQUE KEY unique_usuario (usuario_id),
    FOREIGN KEY (usuario_id) REFERENCES USUARIO(usuario_id) ON DELETE CASCADE,
    FOREIGN KEY (tipo_documento_id) REFERENCES TIPO_DOCUMENTO(tipo_doc_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insertar tipos de documento si no existen
INSERT INTO TIPO_DOCUMENTO (nombre_tipo_doc, estado) VALUES
('DNI', 1),
('Pasaporte', 1),
('Carnet de Extranjería', 1),
('RUC', 1)
ON DUPLICATE KEY UPDATE nombre_tipo_doc = VALUES(nombre_tipo_doc);

-- ================================================
-- Fin del script
-- ================================================

