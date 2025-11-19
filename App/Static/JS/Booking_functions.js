const step3El = document.getElementById("step3");
const step1 = document.getElementById("step1");
const step2 = document.getElementById("step2");
const step3 = document.getElementById("step3");

const selectedContainer = document.getElementById("selected_rooms");

const totalDisplay = document.getElementById("Total_sum");
const nextLink = document.getElementById("next_booking_link");
const backToRooms = document.getElementById("back_to_rooms");
const nextToGuests = document.getElementById("next_to_guests");
const backToClient = document.getElementById("back_to_client");
const finalizarReserva = document.getElementById("finalizar_reserva");
const habitacionesContainer = document.getElementById("habitaciones_container");

const tipoSwitch = document.getElementById("tipo_cliente_switch");
const tipoLabel = document.getElementById("tipo_cliente_label");
const naturalFields = document.getElementById("natural_fields");
const juridicaFields = document.getElementById("juridica_fields");
const nextToGuestsBtn = document.getElementById("next_to_guests");
const backToRoomsBtn = document.getElementById("back_to_rooms");

// inputs naturales
const numDocNatural = document.getElementById("num_doc_natural");
const nombres = document.getElementById("nombres");
const apePaterno = document.getElementById("ape_paterno");
const apeMaterno = document.getElementById("ape_materno");
const telefonoNatural = document.getElementById("telefono_natural");
const paisSelect = document.getElementById("pais_select");
const startDateInput = document.getElementById("Start_booking_date");
const endDateInput = document.getElementById("End_booking_date");
const tipo_doc_natural_select = document.getElementById("tipo_doc_natural");
const servicesContainer = document.getElementById("selected_services_container");
const serviceCheckboxes = document.querySelectorAll(".service-checkbox");
const travelMotiveInput = document.getElementById("motivo_viaje");
// inputs juridicos
const numDocJuridico = document.getElementById("num_doc_juridico");
const paisjuridica = document.getElementById("pais_select_j");
const razonSocial = document.getElementById("razon_social");
const direccionJuridica = document.getElementById("direccion_juridica");
const telefonojuridica = document.getElementById("telefono_juridico");
const tipoempresa = document.getElementById("tipo_empresa");
const telefonoInput = document.getElementById("telefono_natural");


// Referencias DOM


let tipo_validacion;
// --- Variables de estado ---
let roomsTotal = 0;
let servicesTotal = 0;
let total = 0;
let selectedRooms = [];
let clientData = {};
let selectedServices = [];
// Objeto para almacenar cantidades de servicios: { serviceId: cantidad }
let serviceQuantities = {};
// const tipoEmpresa = document.getElementById("tipo_empresa");
// correo (opcional/global)
const correoCliente = document.getElementById("correo_cliente");

//CREACION DE DIV DE HABITACION AGREGADA
function createSelectedRoomDiv(roomId) {
const roomName = roomNames[roomId];
const price = parseFloat(roomPrices[roomId]) || 0;
// Si ya existe, no duplicar
if (document.getElementById("room_selected_" + roomId)) return;

const div = document.createElement("div");
div.className = "room_selected_style";
div.id = "room_selected_" + roomId;
div.innerHTML = `
    <p>Hab. ${roomName} — S/. ${price.toFixed(2)}</p>
    <button type="button" class="remove_room">x</button>
`;
selectedContainer.appendChild(div);

// evento X para quitar
div.querySelector(".remove_room").addEventListener("click", () => {
    const cb = document.getElementById("checkbox_booking_" + roomId);
    if (cb) {
    cb.checked = false;
    cb.dispatchEvent(new Event('change'));
    } else {
    // si no hay checkbox (caso raro), solo eliminar y ajustar total
    div.remove();
    total -= price;
    if (total < 0) total = 0;
    updateTotalDisplay();
    selectedRooms = selectedRooms.filter(id => id !== roomId);
    }
});
}
//ACTUALIZAR TOTAL DEL PRECIO A PAGAR POR HABITACIONES ACUMULADAS EN DIV DE RESUMEN
function updateTotalDisplay() {
total = roomsTotal + servicesTotal;
totalDisplay.textContent = "Total: S/. " + total.toFixed(2);
}

function toggleServicesSection() {
  if (!servicesContainer) return;
  if (selectedRooms.length > 0) {
    servicesContainer.classList.remove("hidden");
  } else {
    servicesContainer.classList.add("hidden");
  }
}

function resetServicesSelection() {
  selectedServices = [];
  serviceQuantities = {};
  servicesTotal = 0;
  // Resetear todos los servicios a cantidad 0
  document.querySelectorAll('.service-card-horizontal').forEach(card => {
    const serviceId = card.dataset.serviceId;
    const quantityDisplay = card.querySelector('.quantity-display');
    const totalDisplay = card.querySelector('.service-price-total');
    if (quantityDisplay) quantityDisplay.textContent = '0';
    if (totalDisplay) totalDisplay.textContent = '0.00';
    card.classList.remove('selected');
  });
}

// Manejo de servicios con cantidad (botones + y -)
document.addEventListener('DOMContentLoaded', () => {
  // Event listeners para botones de cantidad de servicios
  document.querySelectorAll('.quantity-btn--plus').forEach(btn => {
    btn.addEventListener('click', function() {
      if (selectedRooms.length === 0) {
        alert('Por favor, selecciona al menos una habitación primero.');
        return;
      }
      const serviceId = this.dataset.service;
      const card = document.querySelector(`.service-card-horizontal[data-service-id="${serviceId}"]`);
      if (!card) return;
      
      const quantityDisplay = card.querySelector('.quantity-display');
      const totalDisplay = card.querySelector('.service-price-total');
      const priceUnit = parseFloat(card.dataset.price) || 0;
      
      let currentQty = parseInt(quantityDisplay.textContent) || 0;
      currentQty++;
      
      quantityDisplay.textContent = currentQty;
      const totalPrice = currentQty * priceUnit;
      totalDisplay.textContent = totalPrice.toFixed(2);
      
      // Actualizar estado del botón menos
      const minusBtn = card.querySelector('.quantity-btn--minus');
      if (minusBtn) minusBtn.disabled = false;
      
      // Actualizar arrays y totales
      if (!selectedServices.includes(serviceId)) {
        selectedServices.push(serviceId);
      }
      serviceQuantities[serviceId] = currentQty;
      
      // Recalcular total de servicios
      servicesTotal = 0;
      Object.keys(serviceQuantities).forEach(sid => {
        const qty = serviceQuantities[sid] || 0;
        const price = parseFloat(document.querySelector(`.service-card-horizontal[data-service-id="${sid}"]`)?.dataset.price || 0);
        servicesTotal += qty * price;
      });
      
      card.classList.add('selected');
      updateTotalDisplay();
      if (typeof populatePaymentSummary_new === 'function') {
        populatePaymentSummary_new();
      }
    });
  });
  
  document.querySelectorAll('.quantity-btn--minus').forEach(btn => {
    btn.addEventListener('click', function() {
      const serviceId = this.dataset.service;
      const card = document.querySelector(`.service-card-horizontal[data-service-id="${serviceId}"]`);
      if (!card) return;
      
      const quantityDisplay = card.querySelector('.quantity-display');
      const totalDisplay = card.querySelector('.service-price-total');
      const priceUnit = parseFloat(card.dataset.price) || 0;
      
      let currentQty = parseInt(quantityDisplay.textContent) || 0;
      if (currentQty > 0) {
        currentQty--;
        quantityDisplay.textContent = currentQty;
        const totalPrice = currentQty * priceUnit;
        totalDisplay.textContent = totalPrice.toFixed(2);
        
        // Actualizar estado del botón menos
        this.disabled = currentQty === 0;
        
        if (currentQty === 0) {
          selectedServices = selectedServices.filter(id => id !== serviceId);
          delete serviceQuantities[serviceId];
          card.classList.remove('selected');
        } else {
          serviceQuantities[serviceId] = currentQty;
        }
        
        // Recalcular total de servicios
        servicesTotal = 0;
        Object.keys(serviceQuantities).forEach(sid => {
          const qty = serviceQuantities[sid] || 0;
          const price = parseFloat(document.querySelector(`.service-card-horizontal[data-service-id="${sid}"]`)?.dataset.price || 0);
          servicesTotal += qty * price;
        });
        
        updateTotalDisplay();
        if (typeof populatePaymentSummary_new === 'function') {
          populatePaymentSummary_new();
        }
      }
    });
  });
  
  // Inicializar estado de botones menos (deshabilitados si cantidad es 0)
  document.querySelectorAll('.quantity-btn--minus').forEach(btn => {
    const serviceId = btn.dataset.service;
    const card = document.querySelector(`.service-card-horizontal[data-service-id="${serviceId}"]`);
    if (card) {
      const quantityDisplay = card.querySelector('.quantity-display');
      const currentQty = parseInt(quantityDisplay.textContent) || 0;
      btn.disabled = currentQty === 0;
    }
  });
});
//SELECCION DE HABITACION Y ADDICCION AL DIV DE RESUMEN
document.querySelectorAll('.checkbox_booking').forEach(cb => {
cb.addEventListener('change', function() {
    const roomId = this.value;
    const roomName = roomNames[roomId];
    const price = parseFloat(roomPrices[roomId]) || 0;
    
    if (this.checked) {
    selectedRooms.push(roomId);
    roomsTotal += price;

    const div = document.createElement("div");
    div.className = "room_selected_style";
    div.id = "room_selected_" + roomId;
    div.innerHTML = `
        <p>Hab. ${roomName} — S/. ${price.toFixed(2)}</p>
        <button type="button" class="remove_room">x</button>
    `;
    selectedContainer.appendChild(div);

    div.querySelector(".remove_room").addEventListener("click", () => {
        cb.checked = false;
        cb.dispatchEvent(new Event('change'));
    });
    } else {
    selectedRooms = selectedRooms.filter(id => id !== roomId);
    roomsTotal -= price;
    document.getElementById("room_selected_" + roomId)?.remove();
    }

    updateTotalDisplay();
    toggleServicesSection();
    if (selectedRooms.length === 0) {
      resetServicesSelection();
      updateTotalDisplay();
    }
});
});
// Si tu tabla se actualiza dinámicamente (por ejemplo por AJAX) necesitas re-run bindCheckboxEvents()
function bindCheckboxEvents() {
document.querySelectorAll('.checkbox_booking').forEach(cb => {
    if (cb.dataset.bound === "true") return;
    cb.dataset.bound = "true";

    cb.addEventListener('change', function() {
    const roomId = this.value;
    const price = parseFloat(roomPrices[roomId]) || 0;

    if (this.checked) {
        if (!selectedRooms.includes(roomId)) selectedRooms.push(roomId);
        roomsTotal += price;
        createSelectedRoomDiv(roomId);
    } else {
        selectedRooms = selectedRooms.filter(id => id !== roomId);
        roomsTotal -= price;
        const el = document.getElementById("room_selected_" + roomId);
        if (el) el.remove();
    }
    if (roomsTotal < 0) roomsTotal = 0;
    updateTotalDisplay();
    toggleServicesSection();
    if (selectedRooms.length === 0) {
      resetServicesSelection();
      updateTotalDisplay();
    }
    });
});
}
// función para alternar vistas según switch
function toggleClienteView() {
const esJuridico = tipoSwitch.checked;
if (esJuridico) {
    tipoLabel.textContent = "Persona Jurídica";
    naturalFields.style.display = "none";
    juridicaFields.style.display = "block";
} else {
    tipoLabel.textContent = "Persona Natural";
    naturalFields.style.display = "block";
    juridicaFields.style.display = "none";
}
}
// limpiar campos al cambiar tipo (opcional, recomendable)
function limpiarCampos() {
// naturales
numDocNatural.value = "";
nombres.value = "";
apePaterno.value = "";
apeMaterno.value = "";
telefonoNatural.value = "";
paisSelect.value = "";

// juridicos
numDocJuridico.value = "";
razonSocial.value = "";
direccionJuridica.value = "";
paisjuridica.value="";
tipoempresa.value = "";
telefonojuridica.value="";
}
//VALIDACION DNI
function esDniValido(dni) {
return /^[0-9]{8}$/.test(dni);
}
//VALIDACION RUC
function esRucValido(ruc) {
return /^[0-9]{11}$/.test(ruc);
}
//VALIDACION PASAPORTE
function esPasaporteValido(pasaporte) {
return /^[A-Za-z0-9]{6,12}$/.test(pasaporte);
}
//GENERAR FORMULARIOS SEGUN CANTIDAD DE HUESPEDES POR HABITACION
function generarFormulariosHuespedes() {
habitacionesContainer.innerHTML = "";
selectedRooms.forEach(roomId => {
const capacidad = parseInt(roomCapacities[roomId]) || 1;
const div = document.createElement("div");
div.className = "habitacion_form";
div.innerHTML = `
    <h3>Habitación ${roomNames[roomId]}</h3>
    <label>Cantidad de personas:</label>
    <select class="numPersonas" id="numPersonas_${roomId}" data-room="${roomId}">
    ${Array.from({length: capacidad}, (_, i) => `<option value="${i+1}">${i+1}</option>`).join('')}
    </select>
    <div class="yo_container">
    <input type="checkbox" class="yoHospedare" data-room="${roomId}" id="yoHospedare_${roomId}">
    <label for="yoHospedare_${roomId}">Yo me hospedaré aquí</label>
    </div>
    <div class="contenedorHuespedes" id="huespedes_${roomId}"></div>
`;
habitacionesContainer.appendChild(div);

const select = div.querySelector(".numPersonas");
select.addEventListener("change", () => generarCamposHuespedes(roomId));
generarCamposHuespedes(roomId);
});

// bindear comportamiento de "yoHospedare"
bindYoMeHospedareControls();
}
//MANEJO DE CHECKBOXS DE HOSPEDAJE
function bindYoMeHospedareControls() {
  const checkboxes = document.querySelectorAll(".yoHospedare");
  const TIPO_CLIENTE_VAL = document.getElementById("tipo_cliente_switch");
  const juridico_VAL = TIPO_CLIENTE_VAL.checked;
  // ✅ Si se cumple cierta condición, ocultar todos los checkboxes
  if (juridico_VAL || usuarioId) {
    checkboxes.forEach(cb => {
      cb.style.display = "none";
      const lab = document.querySelector(`label[for="${cb.id}"]`);
      if (lab) lab.style.display = "none";
    });
    return; // No continuar con el resto de la función
  }

  checkboxes.forEach(cb => {
    // Evitar duplicar listeners
    cb.removeEventListener('change', cb._yoHospedareHandler);

    const handler = (e) => {
      const target = e.target;

      // Control de habilitar/deshabilitar otros checkboxes
      if (target.checked) {
        checkboxes.forEach(other => {
          if (other === target) return;
          other.checked = false;
          other.disabled = true;
          other.style.display = "none";
          const lab = document.querySelector(`label[for="${other.id}"]`);
          if (lab) lab.style.display = "none";
        });
      } else {
        checkboxes.forEach(other => {
          if (other === target) return;
          other.disabled = false;
          other.style.display = "";
          const lab = document.querySelector(`label[for="${other.id}"]`);
          if (lab) lab.style.display = "";
        });
      }

      // --- Rellenar campos del huésped con los datos del cliente ---
      const roomId = target.dataset.room;
      const contenedor = document.getElementById(`huespedes_${roomId}`);
      if (!contenedor) return;

      const nombreCliente = document.getElementById("nombres")?.value.trim() || "";
      const apePatCliente = document.getElementById("ape_paterno")?.value.trim() || "";
      const apeMatCliente = document.getElementById("ape_materno")?.value.trim() || "";
      const docCliente = document.getElementById("num_doc_natural")?.value.trim() || "";

      if (target.checked) {
        const inputNombre = contenedor.querySelector(".nombre_huesped");
        const inputApeP = contenedor.querySelector(".apellido_huesped");
        const inputApeM = contenedor.querySelector(".apellido_huesped_m");
        const inputDoc = contenedor.querySelector(".doc_huesped");

        if (inputNombre) inputNombre.value = nombreCliente;
        if (inputApeP) inputApeP.value = apePatCliente;
        if (inputApeM) inputApeM.value = apeMatCliente;
        if (inputDoc) inputDoc.value = docCliente;
      } else {
        const inputs = contenedor.querySelectorAll(".nombre_huesped, .apellido_huesped, .apellido_huesped_m, .doc_huesped");
        inputs.forEach(i => i.value = "");
      }
    };

    cb._yoHospedareHandler = handler;
    cb.addEventListener('change', handler);
  });
}
// Estado de navegación de huéspedes por habitación (global para acceso desde otros scripts)
window.huespedNavigationState = window.huespedNavigationState || {};
const huespedNavigationState = window.huespedNavigationState;

//GENERACION DE CAMPOS SGEGUN CANTIDAD DE HUESPEDES
function generarCamposHuespedes(roomId, cantidadManual = null) {
    const contenedor = document.getElementById(`huespedes_${roomId}`);
    const cantidad = cantidadManual ?? parseInt(document.getElementById(`numPersonas_${roomId}`)?.value) ?? 1;
    if (!contenedor) return;
    
    // Guardar datos existentes antes de regenerar
    const datosExistentes = {};
    const cardsExistentes = contenedor.querySelectorAll('.huesped_card');
    cardsExistentes.forEach(card => {
        const index = parseInt(card.dataset.huespedIndex) || 1;
        datosExistentes[index] = {
            nombre: card.querySelector('.nombre_huesped')?.value || '',
            apeP: card.querySelector('.apellido_huesped')?.value || '',
            apeM: card.querySelector('.apellido_huesped_m')?.value || '',
            doc: card.querySelector('.doc_huesped')?.value || ''
        };
    });
    
    // Obtener cantidad anterior
    const cantidadAnterior = cardsExistentes.length;
    
    // Resetear estado de navegación para esta habitación
    huespedNavigationState[roomId] = {
        current: 1,
        total: cantidad
    };
    
    // Remover navegación anterior si existe
    const navAnterior = contenedor.querySelector('.huesped-navigation');
    if (navAnterior) navAnterior.remove();
    
    // Limpiar contenedor
    contenedor.innerHTML = "";
    
    // Generar todos los formularios de huéspedes
    for (let i = 1; i <= cantidad; i++) {
        const card = document.createElement("div");
        card.className = `huesped_card ${i === 1 ? 'active' : ''}`;
        card.dataset.huespedIndex = i;
        
        // Preservar datos si existen y la cantidad aumentó o se mantuvo
        const datos = datosExistentes[i] || {};
        
        card.innerHTML = `
            <h4>Huésped ${i}</h4>
            <input class="nombre_huesped" placeholder="Nombre" oninput="validarNombreApellido(this)" value="${datos.nombre || ''}">
            <input class="apellido_huesped" placeholder="Apellido Paterno" oninput="validarNombreApellido(this)" value="${datos.apeP || ''}">
            <input class="apellido_huesped_m" placeholder="Apellido Materno" oninput="validarNombreApellido(this)" value="${datos.apeM || ''}">
            <input class="doc_huesped" placeholder="N° Documento" maxlength="8" oninput="validarDocumento(this)" value="${datos.doc || ''}">
        `;
        contenedor.appendChild(card);
    }
    
    // Agregar navegación solo si hay más de 1 huésped
    if (cantidad > 1) {
        const nav = document.createElement("div");
        nav.className = "huesped-navigation";
        nav.innerHTML = `
            <button type="button" class="huesped-navigation__button huesped-navigation__button--prev" 
                    data-room="${roomId}" data-action="prev" disabled>
                <i class="fas fa-chevron-left"></i> Anterior
            </button>
            <span class="huesped-navigation__info">
                <span class="huesped-current">1</span> de <span class="huesped-total">${cantidad}</span>
            </span>
            <button type="button" class="huesped-navigation__button huesped-navigation__button--next" 
                    data-room="${roomId}" data-action="next">
                Siguiente <i class="fas fa-chevron-right"></i>
            </button>
        `;
        contenedor.appendChild(nav);
        
        // Agregar event listeners a los botones
        const prevBtn = nav.querySelector('[data-action="prev"]');
        const nextBtn = nav.querySelector('[data-action="next"]');
        
        prevBtn.addEventListener('click', () => window.navigateHuesped(roomId, -1));
        nextBtn.addEventListener('click', () => window.navigateHuesped(roomId, 1));
    }
}

// Función para navegar entre huéspedes (global para acceso desde otros scripts)
window.navigateHuesped = function(roomId, direction) {
    const state = huespedNavigationState[roomId];
    if (!state) return;
    
    const contenedor = document.getElementById(`huespedes_${roomId}`);
    if (!contenedor) return;
    
    // Ocultar huésped actual
    const currentCard = contenedor.querySelector(`.huesped_card[data-huesped-index="${state.current}"]`);
    if (currentCard) {
        currentCard.classList.remove('active');
    }
    
    // Calcular nuevo índice
    state.current += direction;
    
    // Asegurar que esté en rango
    if (state.current < 1) state.current = 1;
    if (state.current > state.total) state.current = state.total;
    
    // Mostrar nuevo huésped
    const newCard = contenedor.querySelector(`.huesped_card[data-huesped-index="${state.current}"]`);
    if (newCard) {
        newCard.classList.add('active');
    }
    
    // Actualizar botones y contador
    updateHuespedNavigation(roomId);
};

// Función para actualizar el estado de los botones de navegación
function updateHuespedNavigation(roomId) {
    const contenedor = document.getElementById(`huespedes_${roomId}`);
    if (!contenedor) return;
    
    const state = huespedNavigationState[roomId];
    if (!state) return;
    
    const prevBtn = contenedor.querySelector('[data-action="prev"]');
    const nextBtn = contenedor.querySelector('[data-action="next"]');
    const currentSpan = contenedor.querySelector('.huesped-current');
    const totalSpan = contenedor.querySelector('.huesped-total');
    
    if (prevBtn) {
        prevBtn.disabled = state.current === 1;
    }
    if (nextBtn) {
        nextBtn.disabled = state.current === state.total;
    }
    if (currentSpan) {
        currentSpan.textContent = state.current;
    }
    if (totalSpan) {
        totalSpan.textContent = state.total;
    }
}

// Validación para los campos de nombre y apellidos (no permitir números)
function validarNombreApellido(input) {
    const valor = input.value;
    // Reemplaza cualquier número por nada
    input.value = valor.replace(/[0-9]/g, '');
}

// Validación para el campo de documento (solo permitir números y verificar duplicados)
function validarDocumento(input) {
    const valor = input.value;
    // Reemplaza cualquier letra o carácter no numérico por nada
    input.value = valor.replace(/[^0-9]/g, '');
    
    // Validar duplicados solo si hay un valor
    if (input.value.trim().length > 0) {
        validarDocumentoDuplicado(input);
    }
}

// Función para validar documentos duplicados entre todos los huéspedes
function validarDocumentoDuplicado(inputActual) {
    const docActual = inputActual.value.trim();
    if (!docActual || docActual.length === 0) return;
    
    // Obtener el card del huésped actual
    const cardActual = inputActual.closest('.huesped_card');
    if (!cardActual) return;
    
    const roomIdActual = cardActual.closest('.contenedorHuespedes')?.id.replace('huespedes_', '');
    const indexActual = parseInt(cardActual.dataset.huespedIndex) || 0;
    
    // Buscar en todas las habitaciones
    const todasLasHabitaciones = document.querySelectorAll('.contenedorHuespedes');
    
    for (const contenedor of todasLasHabitaciones) {
        const cards = contenedor.querySelectorAll('.huesped_card');
        
        for (const card of cards) {
            const docInput = card.querySelector('.doc_huesped');
            if (!docInput || docInput === inputActual) continue;
            
            const docOtro = docInput.value.trim();
            const indexOtro = parseInt(card.dataset.huespedIndex) || 0;
            const roomIdOtro = contenedor.id.replace('huespedes_', '');
            
            // Si encontramos un documento duplicado
            if (docOtro === docActual && docOtro.length > 0) {
                // Mostrar popup
                alert('⚠️ No se puede ingresar el mismo número de documento para dos huéspedes. El documento duplicado ha sido eliminado.');
                
                // Borrar el documento del input actual
                inputActual.value = '';
                inputActual.focus();
                
                return;
            }
        }
    }
}

//RECOLECTAR TODOS LOS DATOS DE LA RESERVA PARA ENVIAR AL SERVIDOR
function recolectarDatosReserva() {
const fechaEntradaRaw = startDateInput?.value || null;
const fechaSalidaRaw = endDateInput?.value || null;

let fecha_ingreso = null, hora_ingreso = null;
let fecha_salida = null, hora_salida = null;

if (fechaEntradaRaw) {
    if (fechaEntradaRaw.includes("T")) {
    const [fecha, hora] = fechaEntradaRaw.split("T");
    fecha_ingreso = fecha;
    hora_ingreso = hora ? (hora.length === 5 ? hora + ":00" : hora) : null;
    } else {
    fecha_ingreso = fechaEntradaRaw;
    hora_ingreso = null;
    }
}
if (fechaSalidaRaw) {
    if (fechaSalidaRaw.includes("T")) {
    const [fecha, hora] = fechaSalidaRaw.split("T");
    fecha_salida = fecha;
    hora_salida = hora ? (hora.length === 5 ? hora + ":00" : hora) : null;
    } else {
    fecha_salida = fechaSalidaRaw;
    hora_salida = null;
    }
}

const habitaciones = selectedRooms.map(roomId => {
    const huespedesDivs = document.querySelectorAll(`#huespedes_${roomId} .huesped_card`);
    const huespedes = Array.from(huespedesDivs).map(div => ({
    nombre: div.querySelector(".nombre_huesped")?.value || "",
    ape_paterno: div.querySelector(".apellido_huesped")?.value || "",
    ape_materno : div.querySelector(".apellido_huesped_m")?.value || "",
    documento: div.querySelector(".doc_huesped")?.value || ""
    }));
    const yoHospedare = document.getElementById(`yoHospedare_${roomId}`)?.checked || false;
    return {
    id_habitacion: roomId,
    nombre: roomNames[roomId],
    precio: roomPrices[roomId],
    huespedes: huespedes,
    yo_me_hospedo: yoHospedare
    };
});


  const motivoViaje = travelMotiveInput ? travelMotiveInput.value.trim() : null;
  const servicios = selectedServices.map(serviceId => ({
    servicio_id: serviceId,
    nombre: serviceNames[serviceId],
    precio_unitario: parseFloat(servicePrices[serviceId]) || 0,
    cantidad: serviceQuantities[serviceId] || 1
  }));

  return {
    cliente: clientData,
    habitaciones: habitaciones,
    total: total,
    fecha_reserva: new Date().toISOString(),
    fecha_ingreso: fecha_ingreso,
    hora_ingreso: hora_ingreso,
    fecha_salida: fecha_salida,
    hora_salida: hora_salida,
    motivo_viaje: motivoViaje || null,
    servicios: servicios,
    bandera: banderita,
    usuario_id: usuarioId
};


}
// Rellena el resumen con las habitaciones seleccionadas y el total
// Mostrar resumen de pago con habitaciones + servicios

// Mostrar resumen de pago (habitaciones + servicios)
function obtenerServiciosSeleccionados() {
  const serviciosArray = [];

  console.log("🔍 obtenerServiciosSeleccionados - Inicio");
  console.log("🔍 serviceQuantities:", serviceQuantities);

  let usarServiceQuantities = false;

  // Validar si serviceQuantities tiene AL MENOS un valor > 0
  if (typeof serviceQuantities !== "undefined" && serviceQuantities) {
    usarServiceQuantities = Object.values(serviceQuantities)
      .some(q => parseInt(q || 0) > 0);
  }

  // 🟦 CASO 1: Usar serviceQuantities si tiene valores > 0
  if (usarServiceQuantities) {
    console.log("✅ Se usarán serviceQuantities (cantidades > 0)");

    Object.keys(serviceQuantities).forEach(serviceId => {
      const cantidad = parseInt(serviceQuantities[serviceId] || 0);

      if (cantidad > 0) {

        const card = document.querySelector(
          `.service-card-horizontal[data-service-id="${serviceId}"]`
        );

        let nombre, precioUnitario;

        if (card) {
          nombre = card.dataset.name || "Servicio sin nombre";
          precioUnitario = parseFloat(card.dataset.price) || 0;
        } else {
          nombre = serviceNames?.[serviceId] || "Servicio sin nombre";
          precioUnitario = parseFloat(servicePrices?.[serviceId] || 0);
        }

        serviciosArray.push({
          nombre,
          cantidad,
          precioUnitario,
          precioNumero: precioUnitario * cantidad
        });
      }
    });

    console.log("🔍 Fin. Servicios encontrados:", serviciosArray.length);
    return serviciosArray;
  }

  // 🟥 CASO 2: Leer cantidades desde el DOM
  console.log("⚠️ No hay cantidades > 0 en serviceQuantities, leyendo desde el DOM…");

  document.querySelectorAll(".service-card-horizontal").forEach(card => {
    const serviceId = card.dataset.serviceId;
    const quantityDisplay = card.querySelector(".quantity-display");

    const cantidad = parseInt(quantityDisplay?.textContent || "0") || 0;

    if (cantidad > 0) {
      const nombre = card.dataset.name || "Servicio sin nombre";
      const precioUnitario = parseFloat(card.dataset.price) || 0;

      // sincronizar con serviceQuantities
      if (typeof serviceQuantities !== "undefined") {
        serviceQuantities[serviceId] = cantidad;
      }

      serviciosArray.push({
        nombre,
        cantidad,
        precioUnitario,
        precioNumero: precioUnitario * cantidad
      });

      console.log("➕ Servicio DOM:", nombre, cantidad);
    }
  });

  console.log("🔍 Fin. Servicios encontrados:", serviciosArray.length);
  return serviciosArray;
}


// --- Tu Función Modificada ---

function populatePaymentSummary_new() {
  // Obtener los elementos del DOM directamente
  const paymentItemsDiv = document.getElementById("payment_items");
  const paymentTotalAmount = document.getElementById("payment_total_amount");
  
  if (!paymentItemsDiv) {
    console.error("❌ paymentItemsDiv no encontrado en el DOM");
    return;
  }
  
  if (!paymentTotalAmount) {
    console.error("❌ paymentTotalAmount no encontrado en el DOM");
  }
  
  paymentItemsDiv.innerHTML = "";
  let localTotal = 0;

  // 🛏️ Habitaciones
  // --- Lógica de habitaciones (se mantiene) ---
  if (Array.isArray(selectedRooms) && selectedRooms.length > 0) {
    selectedRooms.forEach(id => {
      const name  = (typeof roomNames  !== "undefined" && roomNames[id])  ? roomNames[id]  : id;
      const price = (typeof roomPrices !== "undefined" && roomPrices[id]) ? parseFloat(roomPrices[id]) : 0;
      const safePrice = isNaN(price) ? 0 : price;

      localTotal += safePrice;

      const item = document.createElement("div");
      item.className = "payment_item";
      item.innerHTML = `<span>Habitación ${name}</span> <span>S/. ${safePrice.toFixed(2)}</span>`;
      paymentItemsDiv.appendChild(item);
    });
  }
  // ---------------------------------------------

  // ✨ Servicios Adicionales
  // Obtener los servicios seleccionados y agregarlos a la lista
  const serviciosSeleccionados = obtenerServiciosSeleccionados();
  
  // Debug logs
  console.log("🔍 Debug - Servicios seleccionados:", serviciosSeleccionados);
  console.log("🔍 Debug - serviceQuantities:", typeof serviceQuantities !== 'undefined' ? serviceQuantities : 'no definido');
  console.log("🔍 Debug - serviceNames:", typeof serviceNames !== 'undefined' ? serviceNames : 'no definido');
  console.log("🔍 Debug - servicePrices:", typeof servicePrices !== 'undefined' ? servicePrices : 'no definido');
  console.log("🔍 Debug - paymentItemsDiv:", paymentItemsDiv);

  if (serviciosSeleccionados && serviciosSeleccionados.length > 0) {
    console.log("✅ Agregando", serviciosSeleccionados.length, "servicios al resumen");
    
    const header = document.createElement("h3");
    header.textContent = "Servicios Adicionales:";
    // Pequeño estilo para separarlo visualmente de las habitaciones
    header.style.marginTop = "10px"; 
    header.style.fontSize = "1em";
    header.style.marginBottom = "8px";
    paymentItemsDiv.appendChild(header);

    serviciosSeleccionados.forEach((servicio, index) => {
      console.log(`✅ Agregando servicio ${index + 1}:`, servicio);
      localTotal += servicio.precioNumero; // Sumar el precio al total

      const item = document.createElement("div");
      item.className = "payment_item service_item"; // Clase adicional para servicios
      // Mostrar siempre la cantidad, incluso si es 1
      const cantidad = servicio.cantidad || 1;
      const precioUnitario = servicio.precioUnitario || (servicio.precioNumero / cantidad);
      // Formato: "Nombre del servicio (Cantidad: X) - Precio unitario: S/. X.XX"
      item.innerHTML = `<span>${servicio.nombre} (Cantidad: ${cantidad}) - Precio unitario: S/. ${precioUnitario.toFixed(2)}</span> <span>S/. ${servicio.precioNumero.toFixed(2)}</span>`;
      paymentItemsDiv.appendChild(item);
      console.log("✅ Item agregado al DOM:", item);
    });
  } else {
    console.log("⚠️ No hay servicios seleccionados para agregar");
  }
  // ---------------------------------------------


  // 🔢 Total final (usa computeFinalTotal/total si existen)
  let finalTotal = localTotal;
  if (typeof computeFinalTotal === "function") {
    // Si computeFinalTotal existe, asegúrate de que tiene en cuenta localTotal si es necesario,
    // o simplemente úsalo si es la fuente final de la verdad.
    finalTotal = computeFinalTotal(); 
  } else if (typeof total !== "undefined" && !isNaN(total)) {
    finalTotal = parseFloat(total);
  }

  if (paymentTotalAmount) {
    paymentTotalAmount.textContent = Number(finalTotal || 0).toFixed(2);
  }

  // Actualizar QR si lo usas
  if (typeof window.__updateQrPayment === "function") {
    window.__updateQrPayment();
  }
}


// Helper: calcular total desde selectedRooms/roomPrices si `total` no existe
function computeFinalTotal() {
if (typeof total !== 'undefined' && !isNaN(total)) return parseFloat(total);
let sum = 0;
if (Array.isArray(selectedRooms)) {
    selectedRooms.forEach(id => {
    const p = (roomPrices && roomPrices[id]) ? parseFloat(roomPrices[id]) : 0;
    sum += (isNaN(p) ? 0 : p);
    });
}
if (Array.isArray(selectedServices)) {
    selectedServices.forEach(id => {
    const p = (servicePrices && servicePrices[id]) ? parseFloat(servicePrices[id]) : 0;
    sum += (isNaN(p) ? 0 : p);
    });
}
return sum;
}
// Helper: descarga blob como archivo
function downloadBlob(blob, filename) {
const url = URL.createObjectURL(blob);
const a = document.createElement("a");
a.href = url;
a.download = filename;
document.body.appendChild(a);
a.click();
a.remove();
URL.revokeObjectURL(url);
}
// Mostrar resumen de pago (llenado sencillo)

//BOTON BUSCAR CLIENTE NATURAL
document.addEventListener("DOMContentLoaded", () => {
  const tipoDoc = document.getElementById("tipo_doc_natural");
  const numDoc = document.getElementById("num_doc_natural");
  const buscarBtn = document.getElementById("buscar_natural_doc");

  const campos = {
    nombres: document.getElementById("nombres"),
    apePaterno: document.getElementById("ape_paterno"),
    apeMaterno: document.getElementById("ape_materno"),
    telefono: document.getElementById("telefono_natural"),
    pais: document.getElementById("pais_select"),
  };

  const bloquearCampos = (estado = true) => {
    Object.values(campos).forEach(c => c.disabled = estado);
  };
  bloquearCampos(true);
  numDoc.disabled = true;

  tipoDoc.addEventListener("change", () => {
    if (tipoDoc.value && tipoDoc.value !== "-1") {
      numDoc.disabled = false;
    } else {
      numDoc.value = "";
      numDoc.disabled = true;
    }
  });

  buscarBtn.addEventListener("click", async () => {
    const modo = buscarBtn.textContent.trim();

    if (modo === "Buscar") {
      const numDocVal = numDoc.value.trim();
      const tipoVal = tipoDoc.value;

      if (!tipoVal || tipoVal === "-1") {
        alert("Seleccione un tipo de documento.");
        return;
      }
      if (!numDocVal) {
        alert("Ingrese el número de documento.");
        return;
      }

      try {
        const res = await fetch(`/Rutas/buscar_cliente_natural?num_doc=${encodeURIComponent(numDocVal)}`);
        if (!res.ok) {
          if (res.status === 404) {
            alert("Cliente no encontrado. Complete los datos manualmente.");
            bloquearCampos(false);
            tipoDoc.disabled = true;
            numDoc.disabled = true;
            buscarBtn.textContent = "Borrar";
            return;
          }
          throw new Error("Error en la búsqueda");
        }

        const data = await res.json();
        // ✅ Cliente encontrado
        campos.nombres.value = data.nombres || "";
        campos.apePaterno.value = data.ape_paterno || "";
        campos.apeMaterno.value = data.ape_materno || "";
        campos.telefono.value = data.telefono || "";
        campos.pais.value = data.id_pais || "";

        bloquearCampos(true);
        tipoDoc.disabled = true;
        numDoc.disabled = true;
        buscarBtn.textContent = "Borrar";
      } catch (err) {
        console.error("❌ Error en la búsqueda:", err);
        alert("Hubo un problema al buscar el cliente.");
      }

    } else if (modo === "Borrar") {
      numDoc.value = "";
      tipoDoc.value = "-1";
      Object.values(campos).forEach(c => c.value = "");
      bloquearCampos(true);
      tipoDoc.disabled = false;
      numDoc.disabled = true;
      buscarBtn.textContent = "Buscar";
    }
  });
});
//BOTON BUSCAR CLIENTE JURIDICO
document.addEventListener("DOMContentLoaded", () => {
  const numDoc = document.getElementById("num_doc_juridico");
  const razonSocial = document.getElementById("razon_social");
  const tipoEmpresa = document.getElementById("tipo_empresa");
  const direccion = document.getElementById("direccion_juridica");
  const telefono = document.getElementById("telefono_juridico");
  const pais = document.getElementById("pais_select_j");
  const buscarBtn = document.getElementById("buscar_juridica_doc");

  const campos = { razonSocial, tipoEmpresa, direccion, telefono, pais };

  const bloquearCampos = (estado = true) => {
    Object.values(campos).forEach(c => c.disabled = estado);
  };

  bloquearCampos(true);
  numDoc.disabled = false;

  buscarBtn.addEventListener("click", async () => {
    const modo = buscarBtn.textContent.trim();
    const numDocVal = numDoc.value.trim();

    if (modo === "Buscar") {
      if (!numDocVal) {
        alert("Ingrese el número de RUC.");
        return;
      }
      if (numDocVal.length !== 11) {
        alert("El RUC debe tener exactamente 11 dígitos.");
        return;
      }

      try {
        const res = await fetch(`/Rutas/buscar_cliente_juridico?num_doc=${encodeURIComponent(numDocVal)}`);
        if (!res.ok) {
          if (res.status === 404) {
            alert("Cliente no encontrado. Complete los datos manualmente.");
            bloquearCampos(false);
            numDoc.disabled = true;
            buscarBtn.textContent = "Borrar";
            return;
          }
          throw new Error("Error en la búsqueda");
        }

        const data = await res.json();
        // 🟢 Cliente jurídico encontrado
        razonSocial.value = data.razon_social || "";
        direccion.value = data.direccion || "";
        telefono.value = data.telefono || "";
        pais.value = data.id_pais || "";
        tipoEmpresa.value = data.tipoemp_id || "";

        bloquearCampos(true);
        numDoc.disabled = true;
        buscarBtn.textContent = "Borrar";
      } catch (err) {
        console.error("❌ Error en la búsqueda:", err);
        alert("Hubo un problema al buscar el cliente jurídico.");
      }

    } else if (modo === "Borrar") {
      numDoc.value = "";
      Object.values(campos).forEach(c => c.value = "");
      bloquearCampos(true);
      numDoc.disabled = false;
      buscarBtn.textContent = "Buscar";
    }
  });
});

