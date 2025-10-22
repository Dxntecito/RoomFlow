-- TABLAS BÁSICAS (sin cambios lógicos)
CREATE TABLE AMENIDAD (
  amenidad_id     INT(11) NOT NULL AUTO_INCREMENT,
  nombre_amenidad VARCHAR(50) NOT NULL,
  precio          DECIMAL(8,2) NOT NULL,
  estado          TINYINT(1) NOT NULL,
  PRIMARY KEY (amenidad_id)
);

CREATE TABLE CATEGORIA (
  categoria_id     INT(10) NOT NULL AUTO_INCREMENT,
  nombre_categoria VARCHAR(50) UNIQUE,
  precio_categoria DECIMAL(10,2),
  estado           TINYINT(1) NOT NULL,
  PRIMARY KEY (categoria_id)
);

CREATE TABLE PAIS (
  pais_id INT(10) NOT NULL AUTO_INCREMENT,
  nombre  VARCHAR(50) NOT NULL,
  estado  TINYINT(1) NOT NULL,
  PRIMARY KEY (pais_id)
);

CREATE TABLE TIPO_CLIENTE (
  tipo_cliente_id CHAR(1) NOT NULL,
  descripcion     VARCHAR(50) NOT NULL,
  estado          TINYINT(1) NOT NULL,
  PRIMARY KEY (tipo_cliente_id)
);

CREATE TABLE TIPO_DOCUMENTO (
  tipo_doc_id     INT(10) NOT NULL AUTO_INCREMENT,
  nombre_tipo_doc VARCHAR(20) NOT NULL,
  estado          TINYINT(1) NOT NULL,
  PRIMARY KEY (tipo_doc_id)
);

CREATE TABLE TIPO_EVENTO (
  tipo_evento_id     INT(11) NOT NULL AUTO_INCREMENT,
  nombre_tipo_evento VARCHAR(50) NOT NULL,
  estado             TINYINT(1) NOT NULL,
  PRIMARY KEY (tipo_evento_id)
);

CREATE TABLE METODO_PAGO (
  id_metodo_pago INT(10) NOT NULL AUTO_INCREMENT,
  nombre         VARCHAR(20) NOT NULL,
  estado         TINYINT(1) NOT NULL,
  PRIMARY KEY (id_metodo_pago)
);

CREATE TABLE PISO (
  piso_id INT(10) NOT NULL AUTO_INCREMENT,
  numero  CHAR(3) NOT NULL,--------
  estado  TINYINT(1) NOT NULL,
  PRIMARY KEY (piso_id)
);

CREATE TABLE HABITACION (
  habitacion_id INT(10) NOT NULL AUTO_INCREMENT,
  numero        CHAR(3) NOT NULL,
  estado        TINYINT(1) NOT NULL,
  id_categoria  INT(10) NOT NULL,
  piso_id       INT(10) NOT NULL,
  PRIMARY KEY (habitacion_id),
  CONSTRAINT FK_HABITACION_CATEGORIA FOREIGN KEY (id_categoria) REFERENCES CATEGORIA(categoria_id),
  CONSTRAINT FK_HABITACION_PISO FOREIGN KEY (piso_id) REFERENCES PISO(piso_id)
);

CREATE TABLE TIPO_PROMOCION (
  id_tipo_promocion INT(11) NOT NULL AUTO_INCREMENT,
  nombre            VARCHAR(20) NOT NULL,
  estado            TINYINT(1) NOT NULL,
  PRIMARY KEY (id_tipo_promocion)
);

CREATE TABLE PROMOCION (
  id_promocion      INT(11) NOT NULL AUTO_INCREMENT,
  porcentaje        INT(11) NOT NULL,
  descripcion       VARCHAR(25) NOT NULL,
  estado            TINYINT(1) NOT NULL,
  fecha_inicio      DATE NOT NULL,
  fecha_fin         DATE NOT NULL,
  tipo_promocion_id INT(11) NOT NULL,
  PRIMARY KEY (id_promocion),
  CONSTRAINT FK_PROMOCION_TIPO FOREIGN KEY (tipo_promocion_id) REFERENCES TIPO_PROMOCION(id_tipo_promocion)
);

CREATE TABLE CLIENTE (
  cliente_id      INT(10) NOT NULL AUTO_INCREMENT,
  direccion       VARCHAR(255),
  telefono        CHAR(9) UNIQUE,
  f_registro      DATE NOT NULL,
  num_doc         VARCHAR(20) UNIQUE,
  id_tipo_cliente CHAR(1) NOT NULL,
  id_pais         INT(10) NOT NULL,
  id_tipoemp      INT(10),---------
  ape_paterno     VARCHAR(50),
  ape_materno     VARCHAR(50),
  nombres         VARCHAR(50),
  razon_social    VARCHAR(50) UNIQUE,
  PRIMARY KEY (cliente_id),
  CONSTRAINT FK_CLIENTE_TIPOCLI FOREIGN KEY (id_tipo_cliente) REFERENCES TIPO_CLIENTE(tipo_cliente_id),
  CONSTRAINT FK_CLIENTE_PAIS FOREIGN KEY (id_pais) REFERENCES PAIS(pais_id),
  -- id_tipoemp puede referenciar tipo de documento o tipo_empresa según negocio (dejado como nullable/USAR según contexto)
  CONSTRAINT FK_CLIENTE_TIPODOC FOREIGN KEY (id_tipoemp) REFERENCES TIPO_DOCUMENTO(tipo_doc_id)
);

CREATE TABLE EMPLEADO (
  empleado_id      INT(10) NOT NULL AUTO_INCREMENT,
  cod_empleado     INT(11) NOT NULL UNIQUE,
  dni              VARCHAR(8) NOT NULL UNIQUE,
  ape_paterno      VARCHAR(50) NOT NULL,
  ape_materno      VARCHAR(50) NOT NULL,
  nombres          VARCHAR(50) NOT NULL,
  sexo             CHAR(1) NOT NULL,
  movil            VARCHAR(9) NOT NULL,
  tipo_empleado_id INT(10) NOT NULL,
  estado           TINYINT(1) NOT NULL,
  PRIMARY KEY (empleado_id)
);

CREATE TABLE ROL (
  rol_id      INT(10) NOT NULL AUTO_INCREMENT,
  nombre_rol  VARCHAR(50) NOT NULL,
  descripcion VARCHAR(100) NOT NULL,
  estado      TINYINT(1) NOT NULL,
  PRIMARY KEY (rol_id)
);

CREATE TABLE USUARIO (
  usuario_id     INT(10) NOT NULL AUTO_INCREMENT,
  usuario        VARCHAR(50) NOT NULL UNIQUE,
  contrasena     CHAR(64) NOT NULL,
  email          VARCHAR(100) NOT NULL UNIQUE,
  estado         TINYINT(1) NOT NULL,
  fecha_creacion DATE NOT NULL,
  id_rol         INT(10) NOT NULL,
  PRIMARY KEY (usuario_id),
  CONSTRAINT FK_USUARIO_ROL FOREIGN KEY (id_rol) REFERENCES ROL(rol_id)
);

-- RESERVA (agregada con campos generales)
CREATE TABLE RESERVA (
  reserva_id     INT(10) NOT NULL AUTO_INCREMENT,
  fecha_registro DATE NOT NULL,
  hora_registro  TIME(4) NOT NULL,
  monto_total    DECIMAL(10,2) NOT NULL DEFAULT 0,
  promocion_id   INT(11),
  cliente_id     INT(10) NOT NULL,
  empleado_id2   INT(10),
  tipo_reserva   CHAR(1),
  estado         TINYINT(1) NOT NULL DEFAULT 1,
  fecha_ingreso         DATE,--en caso sea reserva
  fecha_salida          DATE,--en caso sea reserva
  motivo                VARCHAR(200),--en caso sea reserva
  PRIMARY KEY (reserva_id),
  CONSTRAINT FK_RESERVA_PROMO FOREIGN KEY (promocion_id) REFERENCES PROMOCION(id_promocion),
  CONSTRAINT FK_RESERVA_CLIENTE FOREIGN KEY (cliente_id) REFERENCES CLIENTE(cliente_id),
  CONSTRAINT FK_RESERVA_EMPLEADO FOREIGN KEY (empleado_id2) REFERENCES EMPLEADO(empleado_id)
);

-- RESERVA_HABITACION CON PK SURROGADA (para facilitar FKs)
CREATE TABLE RESERVA_HABITACION (
  reserva_habitacion_id INT(11) NOT NULL AUTO_INCREMENT,
  reserva_id            INT(10) NOT NULL,
  habitacion_id         INT(10) NOT NULL,
  PRIMARY KEY (reserva_habitacion_id),
  CONSTRAINT FK_RESERVAHABITACION_RESERVA FOREIGN KEY (reserva_id) REFERENCES RESERVA(reserva_id),
  CONSTRAINT FK_RESERVAHABITACION_HABITACION FOREIGN KEY (habitacion_id) REFERENCES HABITACION(habitacion_id)
);

-- ROOM_SERVICE ligado a una reserva_habitacion
CREATE TABLE ROOM_SERVICE (
  room_service_id INT(11) NOT NULL AUTO_INCREMENT,
  reserva_habitacion_id INT(11) NOT NULL,
  fecha_pedido    DATE NOT NULL,
  hora_pedido     TIME(4) NOT NULL,
  PRIMARY KEY (room_service_id),
  CONSTRAINT FK_ROOM_SERVICE_RESERVAHAB FOREIGN KEY (reserva_habitacion_id) REFERENCES RESERVA_HABITACION(reserva_habitacion_id)
);

-- ROOM_SERVICE_AMENIDAD: relaciona room_service con amenidades y opcionalmente con un detalle de comprobante
CREATE TABLE ROOM_SERVICE_AMENIDAD (
  room_service_id int(11) NOT NULL,
  amenidad_id     int(11) NOT NULL,
  cantidad        INT NOT NULL DEFAULT 1,
  detalle_id      int(10) NULL, -- referencia opcional al detalle del comprobante
  PRIMARY KEY (room_service_id, amenidad_id),
  CONSTRAINT FK_RSAMENIDAD_ROOM_SERVICE FOREIGN KEY (room_service_id) REFERENCES ROOM_SERVICE(room_service_id),
  CONSTRAINT FK_RSAMENIDAD_AMENIDAD FOREIGN KEY (amenidad_id) REFERENCES AMENIDAD(amenidad_id)
  -- detalle_id FK añadido más abajo (porque DETALLE_COMPROBANTE se define posteriormente)
);

-- EVENTO (ligado a reserva)
CREATE TABLE EVENTO (
  id_evento       INT(10) NOT NULL AUTO_INCREMENT,
  nombre_evento   VARCHAR(100) NOT NULL,
  fecha           DATE NOT NULL,
  hora_inicio     TIME(4) NOT NULL,
  hora_fin        TIME(4) NOT NULL,
  numero_horas    DECIMAL(5,2) NOT NULL,
  precio_final    DECIMAL(10,2) NOT NULL,
  tipo_evento_id  INT(11) NOT NULL,
  reserva_id      INT(10) NOT NULL,
  PRIMARY KEY (id_evento),
  CONSTRAINT FK_EVENTO_TIPO FOREIGN KEY (tipo_evento_id) REFERENCES TIPO_EVENTO(tipo_evento_id),
  CONSTRAINT FK_EVENTO_RESERVA FOREIGN KEY (reserva_id) REFERENCES RESERVA(reserva_id)
);

-- COMPROBANTE (autoincremental)
CREATE TABLE COMPROBANTE (
  comprobante_id     INT(11) NOT NULL AUTO_INCREMENT,
  tipo_comprobante   CHAR(1) NOT NULL,
  numero_comprobante VARCHAR(20) NOT NULL UNIQUE,
  fecha_comprobante  DATE NOT NULL,
  hora_comprobante   TIME NOT NULL,
  monto_total        DECIMAL(10,2) NOT NULL,
  transaccion_id INT(11) NOT NULL UNIQUE,  
  PRIMARY KEY (comprobante_id),
  CONSTRAINT FK_TRANSACCION_COMPROBANTE FOREIGN KEY (transaccion_id) REFERENCES TRANSACCION(transaccion_id)
);

-- DETALLE_COMPROBANTE: puede apuntar a reserva_habitacion, evento o habitacion directamente.
CREATE TABLE DETALLE_COMPROBANTE (
  detalle_id       INT(10) NOT NULL AUTO_INCREMENT,
  comprobante_id   INT(11) NOT NULL,
  reserva_habitacion_id INT(11) NULL, -- 1–N con reserva_habitacion
  evento_id        INT(10) NULL,      -- 1–N con evento
  habitacion_id    INT(10) NULL,      -- opcional si quieres línea directa a habitación
  cantidad         INT(10) NOT NULL,
  precio_unitario  DECIMAL(10,2) NOT NULL,
  subtotal         DECIMAL(10,2) NOT NULL,
  PRIMARY KEY (detalle_id),
  CONSTRAINT FK_DETALLE_COMP_COMPROBANTE FOREIGN KEY (comprobante_id) REFERENCES COMPROBANTE(comprobante_id),
  CONSTRAINT FK_DETALLE_COMP_RESERVAHAB FOREIGN KEY (reserva_habitacion_id) REFERENCES RESERVA_HABITACION(reserva_habitacion_id),
  CONSTRAINT FK_DETALLE_COMP_EVENTO FOREIGN KEY (evento_id) REFERENCES EVENTO(id_evento),
  CONSTRAINT FK_DETALLE_COMP_HABITACION FOREIGN KEY (habitacion_id) REFERENCES HABITACION(habitacion_id)
);

-- Ahora que DETALLE_COMPROBANTE existe, creamos FK desde ROOM_SERVICE_AMENIDAD.detalle_id hacia DETALLE_COMPROBANTE
ALTER TABLE ROOM_SERVICE_AMENIDAD
  ADD CONSTRAINT FK_RSAMENIDAD_DETALLE FOREIGN KEY (detalle_id) REFERENCES DETALLE_COMPROBANTE(detalle_id);

-- TRANSACCION: cada reserva tiene 1 transacción y cada transacción 1 comprobante (1–1)
CREATE TABLE TRANSACCION (
  transaccion_id INT(11) NOT NULL AUTO_INCREMENT,
  metodo_pago_id INT(10) NOT NULL,
  fecha_pago     DATE NOT NULL,
  monto          DECIMAL(10,2) NOT NULL,
  estado         TINYINT(1) NOT NULL,
  reserva_id     INT(10) NOT NULL UNIQUE,   -- 1 reserva = 1 transaccion
  -- 1 transaccion = 1 comprobante
  PRIMARY KEY (transaccion_id),
  CONSTRAINT FK_TRANSACCION_METODO FOREIGN KEY (metodo_pago_id) REFERENCES METODO_PAGO(id_metodo_pago),
  CONSTRAINT FK_TRANSACCION_RESERVA FOREIGN KEY (reserva_id) REFERENCES RESERVA(reserva_id)
  
);

-- NOTA_CREDITO: 1–1 con comprobante (si existe)
CREATE TABLE NOTA_CREDITO (
  nota_credito_id INT(11) NOT NULL AUTO_INCREMENT,
  comprobante_id  INT(11) NOT NULL UNIQUE, -- 1 nota_credito por comprobante (si aplica)
  fecha_emision   DATE NOT NULL,
  motivo          VARCHAR(100) NOT NULL,
  monto_credito   DECIMAL(10,2) NOT NULL,
  estado          TINYINT(1) NOT NULL,
  PRIMARY KEY (nota_credito_id),
  CONSTRAINT FK_NOTA_COMP FOREIGN KEY (comprobante_id) REFERENCES COMPROBANTE(comprobante_id)
);

-- INCIDENCIA (detalle)
CREATE TABLE INCIDENCIA (
  incidencia_id      INT(10) NOT NULL AUTO_INCREMENT,
  nombre_incidencia  VARCHAR(255) NOT NULL,
  fecha_envio        DATE NOT NULL,
  fecha_resolucion   DATE,
  estado             TINYINT(1) NOT NULL,
  tipo_incidencia_id INT(10) NOT NULL,
  mensaje            VARCHAR(200) NOT NULL,
  prueba             BLOB,
  cliente_id         INT(10),
  empleado_id        INT(10),
  PRIMARY KEY (incidencia_id)
  -- FKs añadibles: tipo_incidencia, cliente, empleado
);

-- HUESPED: asociado a cliente y (opcionalmente) a reserva_habitacion
CREATE TABLE HUESPED (
  huesped_id    INT(11) NOT NULL AUTO_INCREMENT,
  num_doc       CHAR(9) NOT NULL,
  nombre        VARCHAR(50) NOT NULL,
  ape_paterno   VARCHAR(50) NOT NULL,
  ape_materno   VARCHAR(50) NOT NULL,
  id_cliente    INT(10) NOT NULL,
  reserva_habitacion_id INT(11) NULL,
  PRIMARY KEY (huesped_id),
  CONSTRAINT FKHUESPED_CLIENTE FOREIGN KEY (id_cliente) REFERENCES CLIENTE(cliente_id),
  CONSTRAINT FKHUESPED_RESERVAHAB FOREIGN KEY (reserva_habitacion_id) REFERENCES RESERVA_HABITACION(reserva_habitacion_id)
);
