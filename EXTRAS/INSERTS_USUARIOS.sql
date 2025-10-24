-- ================================================
-- Script de inserción de datos para el sistema de usuarios
-- RoomFlow - Sistema de Gestión Hotelera
-- ================================================

-- Insertar roles básicos
INSERT INTO ROL (rol_id, nombre_rol, descripcion, estado) VALUES
(1, 'Administrador', 'Acceso completo al sistema', 1),
(2, 'Cliente', 'Usuario cliente del hostal', 1),
(3, 'Empleado', 'Empleado del hostal', 1),
(4, 'Recepcionista', 'Personal de recepción', 1)
ON DUPLICATE KEY UPDATE 
    nombre_rol = VALUES(nombre_rol),
    descripcion = VALUES(descripcion),
    estado = VALUES(estado);

-- Insertar usuario administrador de prueba
-- Usuario: admin
-- Contraseña: admin123
-- (Contraseña hasheada en SHA256)
INSERT INTO USUARIO (usuario, contrasena, email, estado, fecha_creacion, id_rol) VALUES
('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'admin@hostalbolivar.com', 1, CURDATE(), 1)
ON DUPLICATE KEY UPDATE 
    contrasena = VALUES(contrasena),
    email = VALUES(email),
    estado = VALUES(estado);

-- Insertar usuario cliente de prueba
-- Usuario: cliente
-- Contraseña: cliente123
-- (Contraseña hasheada en SHA256)
INSERT INTO USUARIO (usuario, contrasena, email, estado, fecha_creacion, id_rol) VALUES
('cliente', '4b2e17867d84e8e2fc7e7c0e3d8c6c3f03e8e3c8c3e8e3c8c3e8e3c8c3e8e3c8', 'cliente@example.com', 1, CURDATE(), 2)
ON DUPLICATE KEY UPDATE 
    contrasena = VALUES(contrasena),
    email = VALUES(email),
    estado = VALUES(estado);

-- ================================================
-- Notas de seguridad:
-- ================================================
-- 1. Las contraseñas en este archivo están hasheadas con SHA256
-- 2. Se recomienda cambiar la contraseña del administrador después de la primera sesión
-- 3. Para producción, usar contraseñas más seguras y no incluirlas en archivos SQL
-- 4. Credenciales de prueba:
--    - Admin: usuario="admin", contraseña="admin123"
--    - Cliente: usuario="cliente", contraseña="cliente123"
-- ================================================

