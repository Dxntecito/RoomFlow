-- PAIS
INSERT INTO PAIS (nombre, estado) VALUES 
('Perú', 1),
('Chile', 1),
('México', 1);

-- TIPO_CLIENTE
INSERT INTO TIPO_CLIENTE (tipo_cliente_id, descripcion, estado) VALUES 
('N', 'Natural', 1),
('J', 'Jurídico', 1),
('V', 'VIP', 1);

-- TIPO_DOCUMENTO
INSERT INTO TIPO_DOCUMENTO (nombre_tipo_doc, estado) VALUES 
('DNI', 1),
('RUC', 1),
('Pasaporte', 1);

-- TIPO_EMPRESA
INSERT INTO TIPO_EMPRESA (nombre_tipo, estado) VALUES 
('Individual', 1),
('Sociedad Anónima', 1),
('EIRL', 1);

-- TIPO_EMPLEADO
INSERT INTO TIPO_EMPLEADO (nombre_tipo) VALUES 
('Recepcionista'),
('Administrador'),
('Limpieza');

-- ROL
INSERT INTO ROL (nombre_rol, descripcion, estado) VALUES 
('Administrador', 'Acceso total al sistema', 1),
('Empleado', 'Acceso limitado', 1),
('Cliente', 'Solo reservas y eventos', 1);

-- TIPO_EVENTO
INSERT INTO TIPO_EVENTO (nombre_tipo_evento, estado) VALUES 
('Boda', 1),
('Conferencia', 1),
('Cumpleaños', 1);

-- TIPO_PROMOCION
INSERT INTO TIPO_PROMOCION (nombre, estado) VALUES 
('Descuento', 1),
('2x1', 1),
('Temporada Alta', 1);

-- TIPO_INCIDENCIA
INSERT INTO TIPO_INCIDENCIA (nombre_tipo_incidencia, estado) VALUES 
('Reclamo', 1),
('Sugerencia', 1),
('Mantenimiento', 1);

-- METODO_PAGO
INSERT INTO METODO_PAGO (nombre, estado) VALUES 
('Efectivo', 1),
('Tarjeta', 1),
('Transferencia', 1);

-- PISO
INSERT INTO PISO (numero, estado) VALUES 
('1', 1),
('2', 1),
('3', 1);

------------------
-- CATEGORIA
INSERT INTO CATEGORIA (nombre_categoria, precio_categoria, estado) VALUES 
('Económica', 120.00, 1),
('Ejecutiva', 220.00, 1),
('Suite', 350.00, 1);

-- AMENIDAD
INSERT INTO AMENIDAD (nombre_amenidad, precio, estado) VALUES 
('Inka Cola', 5.00, 1),
('Coca Cola', 15.00, 1),
('Keke de vainilla', 10.00, 1);

-- EMPLEADO
INSERT INTO EMPLEADO (cod_empleado, dni, ape_paterno, ape_materno, nombres, sexo, movil, tipo_empleado_id, estado) VALUES 
(1001, '45678912', 'Pérez', 'Gómez', 'Juan', 'M', '987654321', 1, 1),
(1002, '87654321', 'López', 'Ruiz', 'María', 'F', '987111222', 2, 1),
(1003, '56781234', 'Vega', 'Soto', 'Carlos', 'M', '987333444', 3, 1);

-- USUARIO
INSERT INTO USUARIO (usuario, contrasena, email, estado, fecha_creacion, id_rol) VALUES 
('admin', SHA2('admin123', 256), 'admin@hotel.com', 1, CURDATE(), 1),
('empleado1', SHA2('emp123', 256), 'empleado1@hotel.com', 1, CURDATE(), 2),
('cliente1', SHA2('cli123', 256), 'cliente1@hotel.com', 1, CURDATE(), 3);
---------------

INSERT INTO CLIENTE (direccion, telefono, f_registro, num_doc, id_tipo_cliente, id_pais, id_tipoemp, ape_paterno, ape_materno, nombres, razon_social) VALUES 
('Av. Arequipa 123', '987654321', '2025-10-01', '87654321', 'N', 1, 1, 'Sánchez', 'Torres', 'Luis', NULL),
('Jr. Lima 555', '912345678', '2025-09-15', '20456789012', 'J', 1, 2, NULL, NULL, NULL, 'Hotel Amazonia SAC'),
('Calle Sol 45', '934567890', '2025-09-20', '99887766', 'V', 2, 1, 'Ramos', 'García', 'Claudia', NULL);

-- COMPROBANTE
INSERT INTO COMPROBANTE (comprobante_id, tipo_comprobante, numero_comprobante, fecha_comprobante, hora_comprobante, monto_total) VALUES 
(1, 'B', 'B001-0001', '2025-10-10', '10:30:00', 250.00),
(2, 'F', 'F001-0002', '2025-10-11', '11:45:00', 400.00),
(3, 'B', 'B001-0003', '2025-10-12', '09:15:00', 180.00);

-- DETALLE_COMPROBANTE
INSERT INTO DETALLE_COMPROBANTE (comprobante_id, cantidad, precio_unitario, subtotal) VALUES 
(1, 1, 250.00, 250.00),
(2, 2, 200.00, 400.00),
(3, 1, 180.00, 180.00);
---------------------
INSERT INTO HABITACION (numero, estado, categoria_id, id_categoria, detalle_comprobante_id, piso_id) VALUES 
('101', 1, 1, 1, 1, 1),
('202', 1, 2, 2, 2, 2),
('303', 1, 3, 3, 3, 3);
-----------------
INSERT INTO RESERVA (fecha_registro, fecha_ingreso, fecha_salida, tipo_transaccion, monto_total, motivo, promocion_id, cliente_id, empleado_id2) VALUES 
('2025-10-05', '2025-10-10', '2025-10-12', 'Online', 350.00, 'Vacaciones familiares', 1, 1, 1),
('2025-10-06', '2025-10-15', '2025-10-18', 'Presencial', 450.00, 'Viaje de negocios', 2, 2, 2),
('2025-10-07', '2025-10-20', '2025-10-22', 'Online', 600.00, 'Evento especial', 3, 3, 3);
-----------------
INSERT INTO EVENTO (nombre_evento, fecha, hora_inicio, hora_fin, numero_horas, precio_final, estado, tipo_evento_id, tipo_reserva_id, detalle_comprobante_id) VALUES 
('Boda Martínez', '2025-10-15', '16:00:00', '22:00:00', 6, 1200.00, 1, 1, 1, 1),
('Conferencia Tech 2025', '2025-10-20', '09:00:00', '13:00:00', 4, 800.00, 1, 2, 2, 2),
('Cumpleaños Ana', '2025-10-25', '18:00:00', '23:00:00', 5, 1000.00, 1, 3, 3, 3);
-----------------
INSERT INTO PROMOCION (porcentaje, descripcion, estado, fecha_inicio, fecha_fin, tipo_promocion_id) VALUES 
(10, 'Descuento de temporada', 1, '2025-10-01', '2025-10-31', 1),
(20, 'Promoción 2x1', 1, '2025-09-01', '2025-12-31', 2),
(15, 'Oferta especial', 1, '2025-10-15', '2025-11-15', 3);
-----------------
INSERT INTO TRANSACCION (comprobante_id, metodo_pago_id, fecha_pago, monto, estado, id_reserva) VALUES 
(1, 1, '2025-10-10', 250, 1, 1),
(2, 2, '2025-10-11', 400, 1, 2),
(3, 3, '2025-10-12', 180, 1, 3);
-----------------
INSERT INTO TURNO (nombre_turno, hora_inicio, hora_fin) VALUES 
('Mañana', '07:00:00', '15:00:00'),
('Tarde', '15:00:00', '23:00:00'),
('Noche', '23:00:00', '07:00:00');

INSERT INTO DETALLE_TURNO (empleado_id, turno_id, fecha) VALUES 
(1, 1, '2025-10-01'),
(2, 2, '2025-10-01'),
(3, 3, '2025-10-01');
