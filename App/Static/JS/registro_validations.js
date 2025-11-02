/**
 * Validaciones completas para el formulario de registro de usuarios
 */

// Configuración de restricciones por tipo de documento
const tiposDocumento = {
    '1': { // DNI
        nombre: 'DNI',
        longitud: 8,
        patron: /^\d{8}$/,
        mensaje: 'El DNI debe tener exactamente 8 dígitos'
    },
    '2': { // Pasaporte
        nombre: 'Pasaporte',
        longitudMin: 6,
        longitudMax: 20,
        patron: /^[A-Z0-9]{6,20}$/i,
        mensaje: 'El Pasaporte debe tener entre 6 y 20 caracteres alfanuméricos'
    },
    '3': { // Carnet de Extranjería
        nombre: 'Carnet de Extranjería',
        longitudMin: 9,
        longitudMax: 12,
        patron: /^[A-Z0-9]{9,12}$/i,
        mensaje: 'El Carnet de Extranjería debe tener entre 9 y 12 caracteres alfanuméricos'
    },
    '4': { // RUC
        nombre: 'RUC',
        longitud: 11,
        patron: /^\d{11}$/,
        mensaje: 'El RUC debe tener exactamente 11 dígitos'
    }
};

// Función para mostrar mensaje de validación
function mostrarMensaje(elementId, mensaje, tipo) {
    const messageElement = document.getElementById(elementId);
    if (messageElement) {
        messageElement.textContent = mensaje;
        messageElement.className = `validation-message ${tipo}`;
    }
}

// Función para ocultar mensaje de validación
function ocultarMensaje(elementId) {
    const messageElement = document.getElementById(elementId);
    if (messageElement) {
        messageElement.style.display = 'none';
    }
}

// Validación de usuario
function validarUsuario(usuario) {
    const patron = /^[a-zA-Z0-9_]{3,50}$/;
    
    if (usuario.length === 0) {
        return { valido: false, mensaje: '' };
    }
    
    if (usuario.length < 3) {
        return { valido: false, mensaje: '✗ El usuario debe tener al menos 3 caracteres' };
    }
    
    if (usuario.length > 50) {
        return { valido: false, mensaje: '✗ El usuario no debe exceder 50 caracteres' };
    }
    
    if (!patron.test(usuario)) {
        return { valido: false, mensaje: '✗ Solo se permiten letras, números y guiones bajos' };
    }
    
    return { valido: true, mensaje: '✓ Usuario válido' };
}

// Validación de email
function validarEmail(email) {
    const patron = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    
    if (email.length === 0) {
        return { valido: false, mensaje: '' };
    }
    
    if (!patron.test(email)) {
        return { valido: false, mensaje: '✗ Formato de email inválido' };
    }
    
    return { valido: true, mensaje: '✓ Email válido' };
}

// Validación de nombres y apellidos
function validarNombresApellidos(texto, campo) {
    const patron = /^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$/;
    
    if (texto.length === 0) {
        return { valido: false, mensaje: '' };
    }
    
    if (texto.length < 2) {
        return { valido: false, mensaje: `✗ ${campo} debe tener al menos 2 caracteres` };
    }
    
    if (texto.length > 50) {
        return { valido: false, mensaje: `✗ ${campo} no debe exceder 50 caracteres` };
    }
    
    if (!patron.test(texto)) {
        return { valido: false, mensaje: `✗ ${campo} solo debe contener letras y espacios` };
    }
    
    if (/\d/.test(texto)) {
        return { valido: false, mensaje: `✗ ${campo} no debe contener números` };
    }
    
    return { valido: true, mensaje: `✓ ${campo} válido` };
}

// Validación de número de documento según tipo
function validarNumeroDocumento(numDocumento, tipoDocumentoId) {
    const tipo = tiposDocumento[tipoDocumentoId];
    
    if (!tipo) {
        return { valido: false, mensaje: '✗ Tipo de documento no válido' };
    }
    
    if (numDocumento.length === 0) {
        return { valido: false, mensaje: '' };
    }
    
    if (!tipo.patron.test(numDocumento)) {
        return { valido: false, mensaje: `✗ ${tipo.mensaje}` };
    }
    
    return { valido: true, mensaje: `✓ ${tipo.nombre} válido` };
}

// Validación de teléfono
function validarTelefono(telefono) {
    const patron = /^9\d{8}$/;
    
    if (telefono.length === 0) {
        return { valido: true, mensaje: '' }; // El teléfono es opcional
    }
    
    if (telefono.length !== 9) {
        return { valido: false, mensaje: '✗ El teléfono debe tener exactamente 9 dígitos' };
    }
    
    if (!patron.test(telefono)) {
        return { valido: false, mensaje: '✗ El teléfono debe comenzar con 9 y contener solo dígitos' };
    }
    
    return { valido: true, mensaje: '✓ Teléfono válido' };
}

// Validación de contraseña
function validarContrasena(contrasena) {
    if (contrasena.length === 0) {
        return { valido: false, mensaje: '' };
    }
    
    if (contrasena.length < 6) {
        return { valido: false, mensaje: '✗ La contraseña debe tener al menos 6 caracteres' };
    }
    
    // Validación adicional de fortaleza (opcional pero recomendada)
    let fortaleza = 0;
    if (/[a-z]/.test(contrasena)) fortaleza++;
    if (/[A-Z]/.test(contrasena)) fortaleza++;
    if (/\d/.test(contrasena)) fortaleza++;
    if (/[^a-zA-Z0-9]/.test(contrasena)) fortaleza++;
    
    if (fortaleza >= 3) {
        return { valido: true, mensaje: '✓ Contraseña fuerte' };
    } else if (fortaleza >= 2) {
        return { valido: true, mensaje: '✓ Contraseña aceptable' };
    } else {
        return { valido: true, mensaje: '⚠ Contraseña débil, considere agregar mayúsculas y números' };
    }
}

// Inicializar validaciones cuando el documento esté listo
document.addEventListener('DOMContentLoaded', function() {
    
    // Referencias a elementos del formulario
    const usuarioInput = document.getElementById('usuario');
    const emailInput = document.getElementById('email');
    const contrasenaInput = document.getElementById('contrasena');
    const confirmarContrasenaInput = document.getElementById('confirmar_contrasena');
    const nombresInput = document.getElementById('nombres');
    const apellidoPaternoInput = document.getElementById('apellido_paterno');
    const apellidoMaternoInput = document.getElementById('apellido_materno');
    const tipoDocumentoSelect = document.getElementById('tipo_documento_id');
    const numDocumentoInput = document.getElementById('num_documento');
    const telefonoInput = document.getElementById('telefono');
    const formulario = document.getElementById('registroForm');
    
    // Validación de usuario en tiempo real
    if (usuarioInput) {
        usuarioInput.addEventListener('input', function() {
            const resultado = validarUsuario(this.value);
            if (resultado.mensaje) {
                mostrarMensaje('usuario-message', resultado.mensaje, resultado.valido ? 'success' : 'error');
            } else {
                ocultarMensaje('usuario-message');
            }
        });
        
        // Prevenir espacios en el usuario
        usuarioInput.addEventListener('keypress', function(e) {
            if (e.key === ' ') {
                e.preventDefault();
            }
        });
    }
    
    // Validación de email en tiempo real
    if (emailInput) {
        emailInput.addEventListener('input', function() {
            const resultado = validarEmail(this.value);
            if (resultado.mensaje) {
                mostrarMensaje('email-message', resultado.mensaje, resultado.valido ? 'success' : 'error');
            } else {
                ocultarMensaje('email-message');
            }
        });
        
        // Prevenir espacios en el email
        emailInput.addEventListener('keypress', function(e) {
            if (e.key === ' ') {
                e.preventDefault();
            }
        });
    }
    
    // Validación de contraseña en tiempo real
    if (contrasenaInput) {
        contrasenaInput.addEventListener('input', function() {
            const resultado = validarContrasena(this.value);
            
            // También validar confirmación si tiene contenido
            if (confirmarContrasenaInput && confirmarContrasenaInput.value !== '') {
                validarConfirmacionContrasena();
            }
        });
    }
    
    // Validación de confirmación de contraseña
    function validarConfirmacionContrasena() {
        if (confirmarContrasenaInput.value === '') {
            ocultarMensaje('confirm-message');
        } else if (confirmarContrasenaInput.value === contrasenaInput.value) {
            mostrarMensaje('confirm-message', '✓ Las contraseñas coinciden', 'success');
        } else {
            mostrarMensaje('confirm-message', '✗ Las contraseñas no coinciden', 'error');
        }
    }
    
    if (confirmarContrasenaInput) {
        confirmarContrasenaInput.addEventListener('input', validarConfirmacionContrasena);
    }
    
    // Validación de nombres
    if (nombresInput) {
        nombresInput.addEventListener('input', function() {
            const resultado = validarNombresApellidos(this.value, 'Nombres');
            if (resultado.mensaje) {
                mostrarMensaje('nombres-message', resultado.mensaje, resultado.valido ? 'success' : 'error');
            } else {
                ocultarMensaje('nombres-message');
            }
        });
        
        // Prevenir números en nombres
        nombresInput.addEventListener('keypress', function(e) {
            if (/\d/.test(e.key)) {
                e.preventDefault();
            }
        });
    }
    
    // Validación de apellido paterno
    if (apellidoPaternoInput) {
        apellidoPaternoInput.addEventListener('input', function() {
            const resultado = validarNombresApellidos(this.value, 'Apellido paterno');
            if (resultado.mensaje) {
                mostrarMensaje('apellido-paterno-message', resultado.mensaje, resultado.valido ? 'success' : 'error');
            } else {
                ocultarMensaje('apellido-paterno-message');
            }
        });
        
        // Prevenir números en apellido paterno
        apellidoPaternoInput.addEventListener('keypress', function(e) {
            if (/\d/.test(e.key)) {
                e.preventDefault();
            }
        });
    }
    
    // Validación de apellido materno
    if (apellidoMaternoInput) {
        apellidoMaternoInput.addEventListener('input', function() {
            const resultado = validarNombresApellidos(this.value, 'Apellido materno');
            if (resultado.mensaje) {
                mostrarMensaje('apellido-materno-message', resultado.mensaje, resultado.valido ? 'success' : 'error');
            } else {
                ocultarMensaje('apellido-materno-message');
            }
        });
        
        // Prevenir números en apellido materno
        apellidoMaternoInput.addEventListener('keypress', function(e) {
            if (/\d/.test(e.key)) {
                e.preventDefault();
            }
        });
    }
    
    // Cambio de tipo de documento
    if (tipoDocumentoSelect && numDocumentoInput) {
        tipoDocumentoSelect.addEventListener('change', function() {
            // Limpiar el campo de número de documento
            numDocumentoInput.value = '';
            ocultarMensaje('num-documento-message');
            
            // Actualizar placeholder y maxlength según el tipo
            const tipoId = this.value;
            const tipo = tiposDocumento[tipoId];
            
            if (tipo) {
                if (tipo.longitud) {
                    numDocumentoInput.setAttribute('maxlength', tipo.longitud);
                    numDocumentoInput.setAttribute('placeholder', `Ingresa tu ${tipo.nombre} (${tipo.longitud} dígitos)`);
                } else {
                    numDocumentoInput.setAttribute('maxlength', tipo.longitudMax);
                    numDocumentoInput.setAttribute('placeholder', `Ingresa tu ${tipo.nombre} (${tipo.longitudMin}-${tipo.longitudMax} caracteres)`);
                }
                
                // Cambiar el tipo de input según el tipo de documento
                if (tipoId === '1' || tipoId === '4') { // DNI o RUC
                    numDocumentoInput.setAttribute('type', 'text');
                    numDocumentoInput.setAttribute('pattern', '[0-9]*');
                    numDocumentoInput.setAttribute('inputmode', 'numeric');
                } else { // Pasaporte o Carnet de Extranjería
                    numDocumentoInput.setAttribute('type', 'text');
                    numDocumentoInput.removeAttribute('pattern');
                    numDocumentoInput.setAttribute('inputmode', 'text');
                }
            }
        });
        
        // Validación de número de documento en tiempo real
        numDocumentoInput.addEventListener('input', function() {
            const tipoId = tipoDocumentoSelect.value;
            
            // Limitar entrada según tipo de documento
            if (tipoId === '1') { // DNI - solo números
                this.value = this.value.replace(/\D/g, '').substring(0, 8);
            } else if (tipoId === '4') { // RUC - solo números
                this.value = this.value.replace(/\D/g, '').substring(0, 11);
            } else if (tipoId === '2') { // Pasaporte
                this.value = this.value.replace(/[^A-Z0-9]/gi, '').substring(0, 20).toUpperCase();
            } else if (tipoId === '3') { // Carnet de Extranjería
                this.value = this.value.replace(/[^A-Z0-9]/gi, '').substring(0, 12).toUpperCase();
            }
            
            const resultado = validarNumeroDocumento(this.value, tipoId);
            if (resultado.mensaje) {
                mostrarMensaje('num-documento-message', resultado.mensaje, resultado.valido ? 'success' : 'error');
            } else {
                ocultarMensaje('num-documento-message');
            }
        });
        
        // Prevenir entrada de caracteres inválidos según tipo de documento
        numDocumentoInput.addEventListener('keypress', function(e) {
            const tipoId = tipoDocumentoSelect.value;
            
            // Solo números para DNI y RUC
            if (tipoId === '1' || tipoId === '4') {
                if (!/\d/.test(e.key)) {
                    e.preventDefault();
                }
            }
        });
        
        // Convertir a mayúsculas para Pasaporte y Carnet de Extranjería
        numDocumentoInput.addEventListener('blur', function() {
            const tipoId = tipoDocumentoSelect.value;
            if (tipoId === '2' || tipoId === '3') {
                this.value = this.value.toUpperCase();
            }
        });
    }
    
    // Validación de teléfono
    if (telefonoInput) {
        telefonoInput.addEventListener('input', function() {
            // Solo permitir números
            this.value = this.value.replace(/\D/g, '').substring(0, 9);
            
            const resultado = validarTelefono(this.value);
            if (resultado.mensaje) {
                mostrarMensaje('telefono-message', resultado.mensaje, resultado.valido ? 'success' : 'error');
            } else {
                ocultarMensaje('telefono-message');
            }
        });
        
        // Prevenir entrada de caracteres no numéricos
        telefonoInput.addEventListener('keypress', function(e) {
            if (!/\d/.test(e.key)) {
                e.preventDefault();
            }
        });
    }
    
    // Validación completa al enviar el formulario
    if (formulario) {
        formulario.addEventListener('submit', function(e) {
            let formularioValido = true;
            let primerCampoInvalido = null;
            
            // Validar usuario
            const resultadoUsuario = validarUsuario(usuarioInput.value);
            if (!resultadoUsuario.valido) {
                mostrarMensaje('usuario-message', resultadoUsuario.mensaje || '✗ Usuario requerido', 'error');
                formularioValido = false;
                if (!primerCampoInvalido) primerCampoInvalido = usuarioInput;
            }
            
            // Validar email
            const resultadoEmail = validarEmail(emailInput.value);
            if (!resultadoEmail.valido) {
                mostrarMensaje('email-message', resultadoEmail.mensaje || '✗ Email requerido', 'error');
                formularioValido = false;
                if (!primerCampoInvalido) primerCampoInvalido = emailInput;
            }
            
            // Validar contraseña
            const resultadoContrasena = validarContrasena(contrasenaInput.value);
            if (!resultadoContrasena.valido || contrasenaInput.value.length === 0) {
                formularioValido = false;
                if (!primerCampoInvalido) primerCampoInvalido = contrasenaInput;
            }
            
            // Validar confirmación de contraseña
            if (contrasenaInput.value !== confirmarContrasenaInput.value) {
                mostrarMensaje('confirm-message', '✗ Las contraseñas no coinciden', 'error');
                formularioValido = false;
                if (!primerCampoInvalido) primerCampoInvalido = confirmarContrasenaInput;
            }
            
            // Validar nombres
            const resultadoNombres = validarNombresApellidos(nombresInput.value, 'Nombres');
            if (!resultadoNombres.valido) {
                mostrarMensaje('nombres-message', resultadoNombres.mensaje || '✗ Nombres requeridos', 'error');
                formularioValido = false;
                if (!primerCampoInvalido) primerCampoInvalido = nombresInput;
            }
            
            // Validar apellido paterno
            const resultadoApPaterno = validarNombresApellidos(apellidoPaternoInput.value, 'Apellido paterno');
            if (!resultadoApPaterno.valido) {
                mostrarMensaje('apellido-paterno-message', resultadoApPaterno.mensaje || '✗ Apellido paterno requerido', 'error');
                formularioValido = false;
                if (!primerCampoInvalido) primerCampoInvalido = apellidoPaternoInput;
            }
            
            // Validar apellido materno
            const resultadoApMaterno = validarNombresApellidos(apellidoMaternoInput.value, 'Apellido materno');
            if (!resultadoApMaterno.valido) {
                mostrarMensaje('apellido-materno-message', resultadoApMaterno.mensaje || '✗ Apellido materno requerido', 'error');
                formularioValido = false;
                if (!primerCampoInvalido) primerCampoInvalido = apellidoMaternoInput;
            }
            
            // Validar número de documento
            const resultadoNumDoc = validarNumeroDocumento(numDocumentoInput.value, tipoDocumentoSelect.value);
            if (!resultadoNumDoc.valido) {
                mostrarMensaje('num-documento-message', resultadoNumDoc.mensaje || '✗ Número de documento requerido', 'error');
                formularioValido = false;
                if (!primerCampoInvalido) primerCampoInvalido = numDocumentoInput;
            }
            
            // Validar teléfono (opcional pero si hay valor debe ser válido)
            if (telefonoInput.value) {
                const resultadoTelefono = validarTelefono(telefonoInput.value);
                if (!resultadoTelefono.valido) {
                    mostrarMensaje('telefono-message', resultadoTelefono.mensaje, 'error');
                    formularioValido = false;
                    if (!primerCampoInvalido) primerCampoInvalido = telefonoInput;
                }
            }
            
            // Si el formulario no es válido, prevenir envío y enfocar el primer campo inválido
            if (!formularioValido) {
                e.preventDefault();
                if (primerCampoInvalido) {
                    primerCampoInvalido.focus();
                    primerCampoInvalido.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        });
    }
    
    // Inicializar tipo de documento al cargar
    if (tipoDocumentoSelect) {
        tipoDocumentoSelect.dispatchEvent(new Event('change'));
    }
});

