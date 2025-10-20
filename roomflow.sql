CREATE TABLE AMENIDAD (
  amenidad_id     int(11) NOT NULL AUTO_INCREMENT, 
  nombre_amenidad varchar(50) NOT NULL, 
  precio          numeric(4, 2) NOT NULL, 
  estado          tinyint(1) NOT NULL, 
  PRIMARY KEY (amenidad_id));
CREATE TABLE CATEGORIA (
  categoria_id     int(10) NOT NULL AUTO_INCREMENT, 
  nombre_categoria varchar(50) UNIQUE, 
  precio_categoria decimal(10, 2), 
  estado           tinyint(1) NOT NULL, 
  PRIMARY KEY (categoria_id));
CREATE TABLE CLIENTE (
  cliente_id      int(10) NOT NULL AUTO_INCREMENT, 
  direccion       varchar(255), 
  telefono        char(9) UNIQUE, 
  f_registro      date NOT NULL, 
  num_doc         varchar(20) UNIQUE, 
  id_tipo_cliente char(1) NOT NULL, 
  id_pais         int(10) NOT NULL, 
  id_tipoemp      int(10), 
  ape_paterno     varchar(50), 
  ape_materno     varchar(50), 
  nombres         varchar(50), 
  razon_social    varchar(50) UNIQUE, 
  PRIMARY KEY (cliente_id));
CREATE TABLE COMPROBANTE (
  comprobante_id     int(11) NOT NULL, 
  tipo_comprobante   char(1) NOT NULL, 
  numero_comprobante varchar(20) NOT NULL, 
  fecha_comprobante  date NOT NULL, 
  hora_comprobante   time NOT NULL, 
  monto_total        decimal(10, 2) NOT NULL, 
  PRIMARY KEY (comprobante_id));
CREATE TABLE DETALLE_COMPROBANTE (
  detalle_id      int(10) NOT NULL AUTO_INCREMENT, 
  comprobante_id  int(11) NOT NULL, 
  cantidad        int(10) NOT NULL, 
  precio_unitario decimal(10, 2) NOT NULL, 
  subtotal        decimal(10, 2) NOT NULL, 
  PRIMARY KEY (detalle_id));
CREATE TABLE DETALLE_TURNO (
  empleado_id int(10) NOT NULL, 
  turno_id    int(10) NOT NULL, 
  fecha       date NOT NULL, 
  PRIMARY KEY (empleado_id, 
  turno_id));
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
  estado           int(10) NOT NULL, 
  PRIMARY KEY (empleado_id));
CREATE TABLE EVENTO (
  id_evento              int(10) NOT NULL AUTO_INCREMENT, 
  nombre_evento          varchar(100) NOT NULL, 
  fecha                  date NOT NULL, 
  hora_inicio            time(4) NOT NULL, 
  hora_fin               time(4) NOT NULL, 
  estado                 tinyint(1) NOT NULL, 
  tipo_evento_id         int(11) NOT NULL, 
  tipo_reserva_id        int(10) NOT NULL, 
  detalle_comprobante_id int(10) NOT NULL, 
  PRIMARY KEY (id_evento));
CREATE TABLE PISO(
  piso_id int(10) NOT NULL AUTO_INCREMENT,
  numero char (2) NOT NULL,
  estado tinyint(1) NOT NULL,
  PRIMARY KEY (piso_id));
CREATE TABLE HABITACION (
  habitacion_id          int(10) NOT NULL AUTO_INCREMENT, 
  numero                 char(3) NOT NULL, 
  estado                 tinyint(1) NOT NULL, 
  categoria_id           int(10) NOT NULL, 
  id_categoria           int(10) NOT NULL, 
  detalle_comprobante_id int(10) NOT NULL, 
  piso_id                int(10) NOT NULL,
  PRIMARY KEY (habitacion_id));
CREATE TABLE INCIDENCIA (
  incidencia_id      int(10) NOT NULL AUTO_INCREMENT, 
  nombre_incidencia  varchar(255) NOT NULL, 
  fecha_envio        date NOT NULL, 
  fecha_resolucion   date, 
  estado             tinyint(1) NOT NULL, 
  descripcion        varchar(250) NOT NULL, 
  tipo_incidencia_id int(10) NOT NULL, 
  mensaje            varchar(200) NOT NULL, 
  prueba             blob NOT NULL, 
  cliente_id         int(10) NOT NULL, 
  empleado_id        int(10) NOT NULL, 
  PRIMARY KEY (incidencia_id));
CREATE TABLE METODO_PAGO (
  id_metodo_pago int(10) NOT NULL AUTO_INCREMENT, 
  nombre         varchar(20) NOT NULL, 
  estado         tinyint(1) NOT NULL, 
  PRIMARY KEY (id_metodo_pago));
CREATE TABLE NOTA_CREDITO (
  nota_credito_id int(11) NOT NULL AUTO_INCREMENT, 
  comprobante_id  int(11) NOT NULL, 
  fecha_emision   date NOT NULL, 
  motivo          varchar(100) NOT NULL, 
  monto_credito   numeric(5, 2) NOT NULL, 
  estado          tinyint(1) NOT NULL, 
  PRIMARY KEY (nota_credito_id));
CREATE TABLE PAIS (
  pais_id int(10) NOT NULL AUTO_INCREMENT, 
  nombre  varchar(50) NOT NULL, 
  estado  tinyint(1) NOT NULL, 
  PRIMARY KEY (pais_id));
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
  reserva_id       int(10) NOT NULL AUTO_INCREMENT, 
  fecha_registro   date NOT NULL, 
  fecha_ingreso    date, 
  fecha_salida     date, 
  tipo_transaccion varchar(20) NOT NULL, 
  monto_total      decimal(10, 2) NOT NULL, 
  motivo           varchar(200), 
  promocion_id     int(11) NOT NULL, 
  cliente_id       int(10) NOT NULL, 
  empleado_id2     int(10) NOT NULL, 
  PRIMARY KEY (reserva_id));
CREATE TABLE ROL (
  rol_id      int(10) NOT NULL AUTO_INCREMENT, 
  nombre_rol  varchar(50) NOT NULL, 
  descripcion varchar(100) NOT NULL, 
  estado      tinyint(1) NOT NULL, 
  PRIMARY KEY (rol_id));
CREATE TABLE ROOM_SERVICE (
  reserva_id             int(10) NOT NULL, 
  room_service_id        int(11) NOT NULL AUTO_INCREMENT, 
  detalle_comprobante_id int(10) NOT NULL, 
  PRIMARY KEY (room_service_id));
CREATE TABLE ROOM_SERVICE_AMENIDAD (
  room_service_id int(11) NOT NULL, 
  amenidad_id     int(11) NOT NULL, 
  PRIMARY KEY (room_service_id, 
  amenidad_id));
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
CREATE TABLE TIPO_EMPRESA (
  tipo_id     int(10) NOT NULL AUTO_INCREMENT, 
  nombre_tipo varchar(50) NOT NULL, 
  estado      tinyint(1) NOT NULL, 
  PRIMARY KEY (tipo_id));
CREATE TABLE TIPO_EVENTO (
  tipo_evento_id     int(11) NOT NULL AUTO_INCREMENT, 
  nombre_tipo_evento varchar(50) NOT NULL, 
  estado             tinyint(1) NOT NULL, 
  PRIMARY KEY (tipo_evento_id));
CREATE TABLE TIPO_INCIDENCIA (
  id_tipo_incidencia     int(10) NOT NULL AUTO_INCREMENT, 
  nombre_tipo_incidencia varchar(100) NOT NULL, 
  estado                 tinyint(1) NOT NULL, 
  PRIMARY KEY (id_tipo_incidencia));
CREATE TABLE TIPO_PROMOCION (
  id_tipo_promocion int(11) NOT NULL AUTO_INCREMENT, 
  nombre            varchar(20) NOT NULL, 
  estado            tinyint(1) NOT NULL, 
  PRIMARY KEY (id_tipo_promocion));
CREATE TABLE TRANSACCION (
  pago_id        int(11) NOT NULL AUTO_INCREMENT, 
  comprobante_id int(11) NOT NULL, 
  metodo_pago_id int(10) NOT NULL, 
  fecha_pago     date NOT NULL, 
  monto          numeric(10, 0) NOT NULL, 
  estado         tinyint(1) NOT NULL, 
  id_reserva     int(10) NOT NULL, 
  PRIMARY KEY (pago_id));
CREATE TABLE TURNO (
  turno_id     int(10) NOT NULL AUTO_INCREMENT, 
  nombre_turno varchar(20) NOT NULL, 
  hora_inicio  time NOT NULL, 
  hora_fin     time NOT NULL, 
  PRIMARY KEY (turno_id));
CREATE TABLE USUARIO (
  usuario_id     int(10) NOT NULL AUTO_INCREMENT, 
  usuario        varchar(50) NOT NULL UNIQUE, 
  contrasena     char(64) NOT NULL, 
  email          varchar(100) NOT NULL UNIQUE, 
  estado         tinyint(1) NOT NULL, 
  fecha_creacion date NOT NULL, 
  id_rol         int(10) NOT NULL, 
  PRIMARY KEY (usuario_id));
CREATE TABLE HUESPED (
  huesped_id    int(11) NOT NULL, 
  num_doc       char(9) NOT NULL, 
  nombre        varchar(50) NOT NULL, 
  ape_paterno   varbinary(50) NOT NULL, 
  ape_materno   varchar(50) NOT NULL, 
  id_cliente    int(10) NOT NULL, 
  id_habitacion int(10) NOT NULL, 
  PRIMARY KEY (huesped_id, 
  num_doc));
CREATE TABLE RESERVA_HABITACION (
  habitacion_id int(10) NOT NULL, 
  reserva_id    int(10) NOT NULL, 
  PRIMARY KEY (habitacion_id, 
  reserva_id));
-- BLOQUE ALTER CORREGIDO (quita espacios en identificadores)
ALTER TABLE `USUARIO` ADD CONSTRAINT `FK_USUARIO505418` FOREIGN KEY (id_rol) REFERENCES `ROL` (rol_id);
ALTER TABLE `CLIENTE` ADD CONSTRAINT `FK_CLIENTE393375` FOREIGN KEY (id_tipo_cliente) REFERENCES `TIPO_CLIENTE` (tipo_cliente_id);
ALTER TABLE `CLIENTE` ADD CONSTRAINT `FK_CLIENTE638454` FOREIGN KEY (id_pais) REFERENCES `PAIS` (pais_id);
ALTER TABLE `CLIENTE` ADD CONSTRAINT `FK_CLIENTE738953` FOREIGN KEY (id_tipoemp) REFERENCES `TIPO_DOCUMENTO` (tipo_doc_id);
ALTER TABLE `CLIENTE` ADD CONSTRAINT `FK_CLIENTE695164` FOREIGN KEY (id_tipoemp) REFERENCES `TIPO_EMPRESA` (tipo_id);
ALTER TABLE `HUESPED` ADD CONSTRAINT `FKHUESPED655618` FOREIGN KEY (id_cliente) REFERENCES `CLIENTE` (cliente_id);
ALTER TABLE `HUESPED` ADD CONSTRAINT `FKHUESPED217740` FOREIGN KEY (id_habitacion) REFERENCES `HABITACION` (habitacion_id);
ALTER TABLE `HABITACION` ADD CONSTRAINT `FK_HABITACIO224172` FOREIGN KEY (id_categoria) REFERENCES `CATEGORIA` (categoria_id);
ALTER TABLE `HABITACION` ADD CONSTRAINT `FK_HABITACION_PISO` FOREIGN KEY (piso_id) REFERENCES `PISO` (piso_id);
ALTER TABLE `PROMOCION` ADD CONSTRAINT `FK_PROMOCION990367` FOREIGN KEY (tipo_promocion_id) REFERENCES `TIPO_PROMOCION` (id_tipo_promocion);
ALTER TABLE `RESERVA` ADD CONSTRAINT `FK_RESERVA548259` FOREIGN KEY (promocion_id) REFERENCES `PROMOCION` (id_promocion);
ALTER TABLE `RESERVA` ADD CONSTRAINT `FK_RESERVA243209` FOREIGN KEY (cliente_id) REFERENCES `CLIENTE` (cliente_id);
ALTER TABLE `TRANSACCION` ADD CONSTRAINT `FK_TRANSACCI788607` FOREIGN KEY (metodo_pago_id) REFERENCES `METODO_PAGO` (id_metodo_pago);
ALTER TABLE `TRANSACCION` ADD CONSTRAINT `FK_TRANSACCI751302` FOREIGN KEY (id_reserva) REFERENCES `RESERVA` (reserva_id);
ALTER TABLE `DETALLE_COMPROBANTE` ADD CONSTRAINT `FK_DETALLE_C40515` FOREIGN KEY (comprobante_id) REFERENCES `COMPROBANTE` (comprobante_id);
ALTER TABLE `EMPLEADO` ADD CONSTRAINT `FK_EMPLEADO604002` FOREIGN KEY (tipo_empleado_id) REFERENCES `TIPO_EMPLEADO` (tipo_id);
ALTER TABLE `DETALLE_TURNO` ADD CONSTRAINT `FK_DETALLE_T212050` FOREIGN KEY (empleado_id) REFERENCES `EMPLEADO` (empleado_id);
ALTER TABLE `DETALLE_TURNO` ADD CONSTRAINT `FK_DETALLE_T774231` FOREIGN KEY (turno_id) REFERENCES `TURNO` (turno_id);
ALTER TABLE `COMPROBANTE` ADD CONSTRAINT `FK_COMPROBAN25084` FOREIGN KEY (comprobante_id) REFERENCES `NOTA_CREDITO` (nota_credito_id);
ALTER TABLE `INCIDENCIA` ADD CONSTRAINT `FK_INCIDENCI239323` FOREIGN KEY (tipo_incidencia_id) REFERENCES `TIPO_INCIDENCIA` (id_tipo_incidencia);
ALTER TABLE `ROOM_SERVICE_AMENIDAD` ADD CONSTRAINT `FK_ROOM_SERV825075` FOREIGN KEY (room_service_id) REFERENCES `ROOM_SERVICE` (room_service_id);
ALTER TABLE `ROOM_SERVICE_AMENIDAD` ADD CONSTRAINT `FK_ROOM_SERV10855` FOREIGN KEY (amenidad_id) REFERENCES `AMENIDAD` (amenidad_id);
ALTER TABLE `EVENTO` ADD CONSTRAINT `FK_EVENTO84136` FOREIGN KEY (tipo_evento_id) REFERENCES `TIPO_EVENTO` (tipo_evento_id);
ALTER TABLE `EVENTO` ADD CONSTRAINT `FK_EVENTO794866` FOREIGN KEY (tipo_reserva_id) REFERENCES `RESERVA` (reserva_id);
ALTER TABLE `ROOM_SERVICE` ADD CONSTRAINT `FK_ROOM_SERV300422` FOREIGN KEY (reserva_id) REFERENCES `RESERVA` (reserva_id);
ALTER TABLE `EVENTO` ADD CONSTRAINT `FK_EVENTO387349` FOREIGN KEY (detalle_comprobante_id) REFERENCES `DETALLE_COMPROBANTE` (detalle_id);
ALTER TABLE `ROOM_SERVICE` ADD CONSTRAINT `FK_ROOM_SERV591653` FOREIGN KEY (detalle_comprobante_id) REFERENCES `DETALLE_COMPROBANTE` (detalle_id);
ALTER TABLE `HABITACION` ADD CONSTRAINT `FK_HABITACIO721366` FOREIGN KEY (detalle_comprobante_id) REFERENCES `DETALLE_COMPROBANTE` (detalle_id);
ALTER TABLE `RESERVA_HABITACION` ADD CONSTRAINT `FKRESERVA_HA569661` FOREIGN KEY (habitacion_id) REFERENCES `HABITACION` (habitacion_id);
ALTER TABLE `RESERVA` ADD CONSTRAINT `FK_RESERVA407528` FOREIGN KEY (empleado_id2) REFERENCES `EMPLEADO` (empleado_id);
ALTER TABLE `RESERVA_HABITACION` ADD CONSTRAINT `FKRESERVA_HA967758` FOREIGN KEY (reserva_id) REFERENCES `RESERVA` (reserva_id);

