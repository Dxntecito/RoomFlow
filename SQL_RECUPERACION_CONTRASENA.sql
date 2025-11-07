-- =====================================================
-- TABLA PARA RECUPERACIÓN DE CONTRASEÑA
-- =====================================================

CREATE TABLE IF NOT EXISTS CODIGO_RECUPERACION (
  codigo_id INT(11) NOT NULL AUTO_INCREMENT,
  usuario_id INT(10) NOT NULL,
  codigo CHAR(6) NOT NULL,
  fecha_creacion DATETIME NOT NULL,
  fecha_expiracion DATETIME NOT NULL,
  usado TINYINT(1) DEFAULT 0,
  PRIMARY KEY (codigo_id),
  FOREIGN KEY (usuario_id) REFERENCES USUARIO(usuario_id) ON DELETE CASCADE,
  INDEX idx_codigo (codigo),
  INDEX idx_usuario_usado (usuario_id, usado),
  INDEX idx_expiracion (fecha_expiracion)
);

-- Nota: Los códigos expiran en 10 minutos por defecto
-- Se recomienda crear un job/cron para limpiar códigos antiguos periódicamente

-- Query opcional para limpiar códigos expirados (ejecutar periódicamente)
-- DELETE FROM CODIGO_RECUPERACION WHERE fecha_expiracion < NOW() OR usado = 1;

