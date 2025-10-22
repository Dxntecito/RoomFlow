INSERT INTO PAIS (nombre, estado)
VALUES ('Perú', 1), ('Chile', 1), ('Colombia', 1);

INSERT INTO TIPO_CLIENTE (tipo_cliente_id, descripcion, estado)
VALUES ('N', 'Natural', 1), ('J', 'Jurídico', 1);

INSERT INTO TIPO_DOCUMENTO (nombre_tipo_doc, estado)
VALUES ('DNI', 1), ('RUC', 1), ('Pasaporte', 1);

INSERT INTO TIPO_EMPLEADO (nombre_tipo)
VALUES ('Recepcionista'), ('Administrador'), ('Limpieza');

INSERT INTO TIPO_INCIDENCIA (nombre, estado)
VALUES ('Queja', 1), ('Reclamo', 1), ('Sugerencia', 1);

INSERT INTO ROL (nombre_rol, descripcion, estado)
VALUES ('Admin', 'Administrador del sistema', 1),
       ('Empleado', 'Usuario operativo', 1);

INSERT INTO METODO_PAGO (nombre, estado)
VALUES ('Efectivo', 1), ('Tarjeta', 1), ('Monedero Virtual', 1);

INSERT INTO TIPO_EVENTO (nombre_tipo_evento, estado)
VALUES ('Boda', 1), ('Conferencia', 1), ('Cumpleaños', 1);

INSERT INTO TIPO_PROMOCION (nombre, estado)
VALUES ('Temporada Baja', 1), ('Fiestas Patrias', 1);

INSERT INTO CATEGORIA (nombre_categoria, precio_categoria, estado, capacidad)
VALUES ('Estándar', 150.00, 1, 2),
       ('Suite', 300.00, 1, 4);

INSERT INTO PISO (numero, estado, precio)
VALUES ('01', 1, 10.00),
       ('02', 1, 15.00);

INSERT INTO HABITACION (numero, estado, id_categoria, piso_id)
VALUES ('101', 1, 1, 1),
       ('102', 1, 1, 1),
       ('201', 1, 2, 2);

INSERT INTO EMPLEADO (cod_empleado, dni, ape_paterno, ape_materno, nombres, sexo, movil, tipo_empleado_id, estado)
VALUES (1001, '45678912', 'Torres', 'Vega', 'Lucía', 'F', '912345678', 1, 1),
       (1002, '12345678', 'Ramírez', 'Gómez', 'Carlos', 'M', '987654321', 2, 1);

INSERT INTO USUARIO (usuario, contrasena, email, estado, fecha_creacion, id_rol)
VALUES ('admin', SHA2('admin123', 256), 'admin@hotel.com', 1, CURDATE(), 1),
       ('lucia', SHA2('1234', 256), 'lucia@hotel.com', 1, CURDATE(), 2);

INSERT INTO CLIENTE (direccion, telefono, f_registro, num_doc, id_tipo_cliente, id_pais, id_tipoemp, ape_paterno, ape_materno, nombres)
VALUES ('Av. Larco 123', '999888777', CURDATE(), '44556677', 'N', 1, 1, 'Pérez', 'Rojas', 'María'),
       ('Jr. Grau 234', '988776655', CURDATE(), '10456789011', 'J', 1, 2, NULL, NULL, NULL);

INSERT INTO RESERVA (fecha_registro, hora_registro, monto_total, cliente_id, empleado_id, tipo_reserva, estado, fecha_ingreso, fecha_salida, motivo)
VALUES (CURDATE(), CURTIME(), 450.00, 1, 1, 'H', 1, '2025-10-25', '2025-10-27', 'Vacaciones familiares');

INSERT INTO RESERVA_HABITACION (reserva_id, habitacion_id)
VALUES (1, 1);

INSERT INTO SERVICIO (nombre_servicio, descripcion, precio, estado)
VALUES ('Spa', 'Masajes relajantes', 80.00, 1),
       ('Desayuno Buffet', 'Incluye desayuno variado', 50.00, 1);

INSERT INTO AMENIDAD (nombre_amenidad, precio, estado)
VALUES ('Champaña', 100.00, 1),
       ('Flores', 60.00, 1);

INSERT INTO PROMOCION (porcentaje, descripcion, estado, fecha_inicio, fecha_fin, tipo_promocion_id)
VALUES (10, 'Descuento por temporada baja', 1, '2025-01-01', '2025-03-01', 1);

INSERT INTO TRANSACCION (metodo_pago_id, fecha_pago, monto, estado, reserva_id)
VALUES (2, CURDATE(), 450.00, 1, 1);

INSERT INTO COMPROBANTE (tipo_comprobante, numero_comprobante, fecha_comprobante, hora_comprobante, monto_total, transaccion_id)
VALUES ('B', 'B001-000123', CURDATE(), CURTIME(), 450.00, 1);

INSERT INTO ROOM_SERVICE (reserva_habitacion_id, fecha_pedido, hora_pedido)
VALUES (1, CURDATE(), CURTIME());

INSERT INTO ROOM_SERVICE_AMENIDAD (room_service_id, amenidad_id, cantidad)
VALUES (1, 1, 1), (1, 2, 1);

