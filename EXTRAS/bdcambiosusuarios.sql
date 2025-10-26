ALTER TABLE INCIDENCIA 
ADD COLUMN numero_comprobante VARCHAR(20) NULL;

ALTER TABLE INCIDENCIA 
MODIFY COLUMN estado TINYINT(2) NOT NULL DEFAULT 3;

ALTER TABLE INCIDENCIA 
ADD COLUMN respuesta TEXT NULL;

-- Primero verifica los datos actuales
SELECT * FROM TIPO_INCIDENCIA;

-- Luego inserta los tipos que necesitas (si no existen)
INSERT INTO TIPO_INCIDENCIA (nombre, estado) VALUES 
('Reserva', 1),
('RoomService', 1),
('Evento', 1);

-- Agregar columna usuario_id a la tabla CLIENTE
ALTER TABLE CLIENTE 
ADD COLUMN usuario_id INT NULL;

-- Crear índice para mejorar rendimiento
CREATE INDEX idx_cliente_usuario_id ON CLIENTE(usuario_id);

-- Agregar clave foránea (opcional, para integridad referencial)
ALTER TABLE CLIENTE 
ADD CONSTRAINT fk_cliente_usuario 
FOREIGN KEY (usuario_id) REFERENCES USUARIO(usuario_id) 
ON DELETE SET NULL ON UPDATE CASCADE;