CREATE TABLE AMENIDAD (
  amenidad_id     int(11) NOT NULL AUTO_INCREMENT, 
  nombre_amenidad varchar(50) NOT NULL, 
  precio          decimal(8, 2) NOT NULL, 
  estado          tinyint(1) NOT NULL, 
  PRIMARY KEY (amenidad_id));
CREATE TABLE CATEGORIA (
  categoria_id     int(10) NOT NULL AUTO_INCREMENT, 
  nombre_categoria varchar(50) NOT NULL UNIQUE, 
  precio_categoria decimal(10, 2) NOT NULL, 
  estado           tinyint(1) NOT NULL, 
  capacidad        int(11) NOT NULL, 
  PRIMARY KEY (categoria_id));
CREATE TABLE CLIENTE (
  cliente_id      int(10) NOT NULL AUTO_INCREMENT, 
  direccion       varchar(255), 
  telefono        char(9) UNIQUE, 
  f_registro      date NOT NULL, 
  num_doc         varchar(20) UNIQUE, 
  id_tipo_cliente char(1) NOT NULL, 
  id_pais         int(10) NOT NULL, 
  tipo_doc_id      int(10), 
  ape_paterno     varchar(50), 
  ape_materno     varchar(50), 
  nombres         varchar(50), 
  razon_social    varchar(50) UNIQUE, 
  PRIMARY KEY (cliente_id));
CREATE TABLE COMPROBANTE (
  comprobante_id     int(11) NOT NULL AUTO_INCREMENT, 
  tipo_comprobante   char(1) NOT NULL, 
  numero_comprobante varchar(20) NOT NULL UNIQUE, 
  fecha_comprobante  date NOT NULL, 
  hora_comprobante   time NOT NULL, 
  monto_total        decimal(10, 2) NOT NULL, 
  transaccion_id     int(11) NOT NULL UNIQUE, 
  PRIMARY KEY (comprobante_id));
CREATE TABLE DETALLE_COMPROBANTE (
  detalle_id      int(10) NOT NULL AUTO_INCREMENT, 
  comprobante_id  int(11) NOT NULL, 
  cantidad        int(10) NOT NULL, 
  precio_unitario decimal(10, 2) NOT NULL, 
  subtotal        decimal(10, 2) NOT NULL, 
  habitacion_id   int(10), 
  id_evento       int(10), 
  id_roomservice  int(10), 
  PRIMARY KEY (detalle_id));
CREATE TABLE EMPLEADO (
  empleado_id      int(10) NOT NULL AUTO_INCREMENT, 
  cod_empleado     int(11) NOT NULL UNIQUE, 
  dni              varchar(8) NOT NULL UNIQUE, 
  ape_paterno      varchar(50) NOT NULL, 
  ape_materno      varchar(50) NOT NULL, 
  nombres          varchar(50) NOT NULL, 
  sexo             char(1) NOT NULL, 
  movil            varchar(9) NOT NULL, 
  tipo_empleado_id int(10) NOT NULL, 
  estado           tinyint(1) NOT NULL, 
  PRIMARY KEY (empleado_id));
CREATE TABLE EVENTO (
  id_evento      int(10) NOT NULL AUTO_INCREMENT, 
  nombre_evento  varchar(100) NOT NULL, 
  fecha          date NOT NULL, 
  hora_inicio    time(4) NOT NULL, 
  hora_fin       time(4) NOT NULL, 
  numero_horas   decimal(5, 2) NOT NULL, 
  precio_final   decimal(10, 2) NOT NULL, 
  tipo_evento_id int(11) NOT NULL, 
  reserva_id     int(10) NOT NULL, 
  PRIMARY KEY (id_evento));
CREATE TABLE HABITACION (
  habitacion_id int(10) NOT NULL AUTO_INCREMENT, 
  numero        char(3) NOT NULL, 
  estado        tinyint(1) NOT NULL, 
  id_categoria  int(10) NOT NULL, 
  piso_id       int(10) NOT NULL, 
  PRIMARY KEY (habitacion_id));
CREATE TABLE HUESPED (
  huesped_id            int(11) NOT NULL AUTO_INCREMENT, 
  num_doc               char(9) NOT NULL, 
  nombre                varchar(50) NOT NULL, 
  ape_paterno           varchar(50) NOT NULL, 
  ape_materno           varchar(50) NOT NULL, 
  id_cliente            int(10) NOT NULL, 
  reserva_habitacion_id int(11), 
  PRIMARY KEY (huesped_id));
CREATE TABLE INCIDENCIA (
  incidencia_id      int(10) NOT NULL AUTO_INCREMENT, 
  nombre_incidencia  varchar(255) NOT NULL, 
  fecha_envio        date NOT NULL, 
  fecha_resolucion   date, 
  estado             tinyint(1) NOT NULL, 
  tipo_incidencia_id int(10) NOT NULL, 
  mensaje            varchar(200) NOT NULL, 
  prueba             blob, 
  cliente_id         int(10), 
  empleado_id        int(10), 
  PRIMARY KEY (incidencia_id));
CREATE TABLE METODO_PAGO (
  id_metodo_pago int(10) NOT NULL AUTO_INCREMENT, 
  nombre         varchar(20) NOT NULL, 
  estado         tinyint(1) NOT NULL, 
  PRIMARY KEY (id_metodo_pago));
CREATE TABLE NOTA_CREDITO (
  nota_credito_id int(11) NOT NULL AUTO_INCREMENT, 
  comprobante_id  int(11) NOT NULL UNIQUE, 
  fecha_emision   date NOT NULL, 
  motivo          varchar(100) NOT NULL, 
  monto_credito   decimal(10, 2) NOT NULL, 
  estado          tinyint(1) NOT NULL, 
  PRIMARY KEY (nota_credito_id));
CREATE TABLE PAIS (
  pais_id int(10) NOT NULL AUTO_INCREMENT, 
  nombre  varchar(50) NOT NULL, 
  estado  tinyint(1) NOT NULL, 
  PRIMARY KEY (pais_id));
CREATE TABLE PISO (
  piso_id int(10) NOT NULL AUTO_INCREMENT, 
  numero  char(2) NOT NULL, 
  estado  tinyint(1) NOT NULL, 
  precio  decimal(5, 2), 
  PRIMARY KEY (piso_id));
CREATE TABLE PROMOCION (
  id_promocion      int(11) NOT NULL AUTO_INCREMENT, 
  porcentaje        int(11) NOT NULL, 
  descripcion       varchar(25) NOT NULL, 
  estado            tinyint(1) NOT NULL, 
  fecha_inicio      date NOT NULL, 
  fecha_fin         date NOT NULL, 
  tipo_promocion_id int(11) NOT NULL, 
  PRIMARY KEY (id_promocion));
CREATE TABLE RESERVA (
  reserva_id     int(10) NOT NULL AUTO_INCREMENT, 
  fecha_registro date NOT NULL, 
  hora_registro  time(4) NOT NULL, 
  monto_total    decimal(10, 2) DEFAULT 0 NOT NULL, 
  promocion_id   int(11), 
  cliente_id     int(10) NOT NULL, 
  empleado_id    int(10), 
  tipo_reserva   char(1), 
  fecha_ingreso         date, 
  hora_ingreso          time,
  fecha_salida          date,
  hora_salida           time, 
  estado         tinyint(1) DEFAULT 1 NOT NULL, 
  motivo         varchar(200), 
  PRIMARY KEY (reserva_id));
CREATE TABLE RESERVA_HABITACION (
  reserva_habitacion_id int(11) NOT NULL AUTO_INCREMENT, 
  reserva_id            int(10) NOT NULL, 
  habitacion_id         int(10) NOT NULL,
  PRIMARY KEY (reserva_habitacion_id));
CREATE TABLE RESERVA_SERVICIO (
  reserva_servicio_id int(11) NOT NULL AUTO_INCREMENT, 
  reserva_id          int(10) NOT NULL, 
  servicio_id         int(11) NOT NULL, 
  cantidad            int(10) NOT NULL, 
  precio_unitario     decimal(10, 2), 
  PRIMARY KEY (reserva_servicio_id));
CREATE TABLE ROL (
  rol_id      int(10) NOT NULL AUTO_INCREMENT, 
  nombre_rol  varchar(50) NOT NULL, 
  descripcion varchar(100) NOT NULL, 
  estado      tinyint(1) NOT NULL, 
  PRIMARY KEY (rol_id));
CREATE TABLE ROOM_SERVICE (
  room_service_id       int(10) NOT NULL AUTO_INCREMENT, 
  reserva_habitacion_id int(11) NOT NULL, 
  fecha_pedido          date NOT NULL, 
  hora_pedido           time(4) NOT NULL, 
  PRIMARY KEY (room_service_id));
CREATE TABLE ROOM_SERVICE_AMENIDAD (
  room_service_id int(10) NOT NULL, 
  amenidad_id     int(11) NOT NULL, 
  cantidad        int(11) DEFAULT 1 NOT NULL, 
  detalle_id      int(10), 
  PRIMARY KEY (room_service_id, 
  amenidad_id));
CREATE TABLE SERVICIO (
  servicio_id     int(11) NOT NULL AUTO_INCREMENT, 
  nombre_servicio varchar(50) NOT NULL, 
  descripcion     varchar(100) NOT NULL, 
  precio          decimal(5, 2) NOT NULL, 
  estado          tinyint(1) NOT NULL, 
  PRIMARY KEY (servicio_id));
CREATE TABLE TIPO_CLIENTE (
  tipo_cliente_id char(1) NOT NULL, 
  descripcion     varchar(50) NOT NULL, 
  estado          tinyint(1) NOT NULL, 
  PRIMARY KEY (tipo_cliente_id));
CREATE TABLE TIPO_DOCUMENTO (
  tipo_doc_id     int(10) NOT NULL AUTO_INCREMENT, 
  nombre_tipo_doc varchar(20) NOT NULL, 
  estado          tinyint(1) NOT NULL, 
  PRIMARY KEY (tipo_doc_id));
CREATE TABLE TIPO_EMPLEADO (
  tipo_id     int(10) NOT NULL AUTO_INCREMENT, 
  nombre_tipo varchar(100) NOT NULL UNIQUE, 
  PRIMARY KEY (tipo_id));
CREATE TABLE TIPO_EVENTO (
  tipo_evento_id     int(11) NOT NULL AUTO_INCREMENT, 
  nombre_tipo_evento varchar(50) NOT NULL, 
  estado             tinyint(1) NOT NULL, 
  PRIMARY KEY (tipo_evento_id));
CREATE TABLE TIPO_INCIDENCIA (
  id_tipo int(10) NOT NULL AUTO_INCREMENT, 
  nombre  varchar(20) NOT NULL UNIQUE, 
  estado  tinyint(3) NOT NULL, 
  PRIMARY KEY (id_tipo));
CREATE TABLE TIPO_PROMOCION (
  id_tipo_promocion int(11) NOT NULL AUTO_INCREMENT, 
  nombre            varchar(20) NOT NULL, 
  estado            tinyint(1) NOT NULL, 
  PRIMARY KEY (id_tipo_promocion));
CREATE TABLE TRANSACCION (
  transaccion_id int(11) NOT NULL AUTO_INCREMENT, 
  metodo_pago_id int(10) NOT NULL, 
  fecha_pago     date NOT NULL, 
  monto          decimal(10, 2) NOT NULL, 
  estado         tinyint(1) NOT NULL, 
  reserva_id     int(10) NOT NULL, 
  PRIMARY KEY (transaccion_id));
CREATE TABLE USUARIO (
  usuario_id     int(10) NOT NULL AUTO_INCREMENT, 
  usuario        varchar(50) NOT NULL UNIQUE, 
  contrasena     char(64) NOT NULL, 
  email          varchar(100) NOT NULL UNIQUE, 
  estado         tinyint(1) NOT NULL, 
  fecha_creacion date NOT NULL, 
  id_rol         int(10) NOT NULL, 
  PRIMARY KEY (usuario_id));
ALTER TABLE INCIDENCIA ADD CONSTRAINT FKINCIDENCIA29620 FOREIGN KEY (tipo_incidencia_id) REFERENCES TIPO_INCIDENCIA (id_tipo);
ALTER TABLE EMPLEADO ADD CONSTRAINT FKEMPLEADO371783 FOREIGN KEY (tipo_empleado_id) REFERENCES TIPO_EMPLEADO (tipo_id);
ALTER TABLE DETALLE_COMPROBANTE ADD CONSTRAINT FKDETALLE_CO813500 FOREIGN KEY (habitacion_id) REFERENCES HABITACION (habitacion_id);
ALTER TABLE DETALLE_COMPROBANTE ADD CONSTRAINT FKDETALLE_CO645244 FOREIGN KEY (id_evento) REFERENCES RESERVA (reserva_id);
ALTER TABLE DETALLE_COMPROBANTE ADD CONSTRAINT FKDETALLE_CO859057 FOREIGN KEY (id_roomservice) REFERENCES ROOM_SERVICE (room_service_id);
ALTER TABLE TRANSACCION ADD CONSTRAINT FKTRANSACCIO229953 FOREIGN KEY (reserva_id) REFERENCES RESERVA (reserva_id);
ALTER TABLE RESERVA_SERVICIO ADD CONSTRAINT FKRESERVA_SE95483 FOREIGN KEY (servicio_id) REFERENCES SERVICIO (servicio_id);
ALTER TABLE RESERVA_SERVICIO ADD CONSTRAINT FKRESERVA_SE99314 FOREIGN KEY (reserva_id) REFERENCES RESERVA (reserva_id);
ALTER TABLE CLIENTE ADD CONSTRAINT FK_CLIENTE_PAIS FOREIGN KEY (id_pais) REFERENCES PAIS (pais_id);
ALTER TABLE CLIENTE ADD CONSTRAINT FK_CLIENTE_TIPOCLI FOREIGN KEY (id_tipo_cliente) REFERENCES TIPO_CLIENTE (tipo_cliente_id);
ALTER TABLE CLIENTE ADD CONSTRAINT FK_CLIENTE_TIPODOC FOREIGN KEY (tipo_doc_id) REFERENCES TIPO_DOCUMENTO (tipo_doc_id);
ALTER TABLE DETALLE_COMPROBANTE ADD CONSTRAINT FK_DETALLE_COMP_COMPROBANTE FOREIGN KEY (comprobante_id) REFERENCES COMPROBANTE (comprobante_id);
ALTER TABLE EVENTO ADD CONSTRAINT FK_EVENTO_RESERVA FOREIGN KEY (reserva_id) REFERENCES RESERVA (reserva_id);
ALTER TABLE EVENTO ADD CONSTRAINT FK_EVENTO_TIPO FOREIGN KEY (tipo_evento_id) REFERENCES TIPO_EVENTO (tipo_evento_id);
ALTER TABLE HABITACION ADD CONSTRAINT FK_HABITACION_CATEGORIA FOREIGN KEY (id_categoria) REFERENCES CATEGORIA (categoria_id);
ALTER TABLE HABITACION ADD CONSTRAINT FK_HABITACION_PISO FOREIGN KEY (piso_id) REFERENCES PISO (piso_id);
ALTER TABLE NOTA_CREDITO ADD CONSTRAINT FK_NOTA_COMP FOREIGN KEY (comprobante_id) REFERENCES COMPROBANTE (comprobante_id);
ALTER TABLE PROMOCION ADD CONSTRAINT FK_PROMOCION_TIPO FOREIGN KEY (tipo_promocion_id) REFERENCES TIPO_PROMOCION (id_tipo_promocion);
ALTER TABLE RESERVA ADD CONSTRAINT FK_RESERVA_CLIENTE FOREIGN KEY (cliente_id) REFERENCES CLIENTE (cliente_id);
ALTER TABLE RESERVA ADD CONSTRAINT FK_RESERVA_EMPLEADO FOREIGN KEY (empleado_id) REFERENCES EMPLEADO (empleado_id);
ALTER TABLE RESERVA ADD CONSTRAINT FK_RESERVA_PROMO FOREIGN KEY (promocion_id) REFERENCES PROMOCION (id_promocion);
ALTER TABLE RESERVA_HABITACION ADD CONSTRAINT FK_RESERVAHABITACION_HABITACION FOREIGN KEY (habitacion_id) REFERENCES HABITACION (habitacion_id);
ALTER TABLE RESERVA_HABITACION ADD CONSTRAINT FK_RESERVAHABITACION_RESERVA FOREIGN KEY (reserva_id) REFERENCES RESERVA (reserva_id);
ALTER TABLE ROOM_SERVICE ADD CONSTRAINT FK_ROOM_SERVICE_RESERVAHAB FOREIGN KEY (reserva_habitacion_id) REFERENCES RESERVA_HABITACION (reserva_habitacion_id);
ALTER TABLE ROOM_SERVICE_AMENIDAD ADD CONSTRAINT FK_RSAMENIDAD_AMENIDAD FOREIGN KEY (amenidad_id) REFERENCES AMENIDAD (amenidad_id);
ALTER TABLE ROOM_SERVICE_AMENIDAD ADD CONSTRAINT FK_RSAMENIDAD_DETALLE FOREIGN KEY (detalle_id) REFERENCES DETALLE_COMPROBANTE (detalle_id);
ALTER TABLE ROOM_SERVICE_AMENIDAD ADD CONSTRAINT FK_RSAMENIDAD_ROOM_SERVICE FOREIGN KEY (room_service_id) REFERENCES ROOM_SERVICE (room_service_id);
ALTER TABLE COMPROBANTE ADD CONSTRAINT FK_TRANSACCION_COMPROBANTE FOREIGN KEY (transaccion_id) REFERENCES TRANSACCION (transaccion_id);
ALTER TABLE TRANSACCION ADD CONSTRAINT FK_TRANSACCION_METODO FOREIGN KEY (metodo_pago_id) REFERENCES METODO_PAGO (id_metodo_pago);
ALTER TABLE USUARIO ADD CONSTRAINT FK_USUARIO_ROL FOREIGN KEY (id_rol) REFERENCES ROL (rol_id);
ALTER TABLE HUESPED ADD CONSTRAINT FKHUESPED_CLIENTE FOREIGN KEY (id_cliente) REFERENCES CLIENTE (cliente_id);
ALTER TABLE HUESPED ADD CONSTRAINT FKHUESPED_RESERVAHAB FOREIGN KEY (reserva_habitacion_id) REFERENCES RESERVA_HABITACION (reserva_habitacion_id);
