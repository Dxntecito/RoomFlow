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
let total = 0;
let selectedRooms = [];
let clientData = {};
// const tipoEmpresa = document.getElementById("tipo_empresa");
// correo (opcional/global)
const correoCliente = document.getElementById("correo_cliente");

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
function updateTotalDisplay() {
totalDisplay.textContent = "Total: S/. " + total.toFixed(2);
}
document.querySelectorAll('.checkbox_booking').forEach(cb => {
cb.addEventListener('change', function() {
    const roomId = this.value;
    const roomName = roomNames[roomId];
    const price = parseFloat(roomPrices[roomId]) || 0;
    
    if (this.checked) {
    selectedRooms.push(roomId);
    total += price;

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
    total -= price;
    document.getElementById("room_selected_" + roomId)?.remove();
    }

    totalDisplay.textContent = "Total: S/. " + total.toFixed(2);
});
});
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
// --- Filtrado de filas según selects ---

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
        total += price;
        createSelectedRoomDiv(roomId);
    } else {
        selectedRooms = selectedRooms.filter(id => id !== roomId);
        total -= price;
        if (total < 0) total = 0;
        const el = document.getElementById("room_selected_" + roomId);
        if (el) el.remove();
    }
    updateTotalDisplay();
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
function esDniValido(dni) {
return /^[0-9]{8}$/.test(dni);
}
function esRucValido(ruc) {
return /^[0-9]{11}$/.test(ruc);
}
function esPasaporteValido(pasaporte) {
return /^[A-Za-z0-9]{6,12}$/.test(pasaporte);
}
function bindYoMeHospedareControls() {
  const checkboxes = document.querySelectorAll(".yoHospedare");
  const TIPO_CLIENTE_VAL = document.getElementById("tipo_cliente_switch");
  const juridico_VAL = TIPO_CLIENTE_VAL.checked;
  // ✅ Si se cumple cierta condición, ocultar todos los checkboxes
  if (juridico_VAL) {
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


function generarCamposHuespedes(roomId, cantidadManual = null) {
const contenedor = document.getElementById(`huespedes_${roomId}`);
const cantidad = cantidadManual ?? parseInt(document.getElementById(`numPersonas_${roomId}`)?.value) ?? 1;
if (!contenedor) return;
contenedor.innerHTML = "";
for (let i = 1; i <= cantidad; i++) {
    contenedor.innerHTML += `
    <div class="huesped_card">
        <h4>Huésped ${i}</h4>
        <input class="nombre_huesped" placeholder="Nombre">
        <input class="apellido_huesped" placeholder="Apellido Paterno">
        <input class ="apellido_huesped_m" placeholder="Apellido Materno">
        <input class="doc_huesped" placeholder="N° Documento" maxlength="8">
    </div>
    `;
}
}
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

return {
    cliente: clientData,
    habitaciones: habitaciones,
    total: total,
    fecha_reserva: new Date().toISOString(),
    fecha_ingreso: fecha_ingreso,
    hora_ingreso: hora_ingreso,
    fecha_salida: fecha_salida,
    hora_salida: hora_salida
};
}
// Rellena el resumen con las habitaciones seleccionadas y el total
function populatePaymentSummary() {
  paymentItemsDiv.innerHTML = "";
  let localTotal = 0;

  if (!selectedRooms || selectedRooms.length === 0) {
    paymentItemsDiv.innerHTML = "<p>No hay habitaciones seleccionadas.</p>";
    paymentTotalAmount.textContent = "0.00";
    return;
  }

  selectedRooms.forEach(id => {
    const name = (typeof roomNames !== 'undefined' && roomNames[id]) ? roomNames[id] : id;
    const price = (typeof roomPrices !== 'undefined' && roomPrices[id]) ? parseFloat(roomPrices[id]) : 0;
    localTotal += price;
    const item = document.createElement("div");
    item.className = "payment_item";
    item.innerHTML = `<span>Habitación ${name}</span> <span>S/. ${price.toFixed(2)}</span>`;
    paymentItemsDiv.appendChild(item);
  });

  // si la variable global total existe, preferimos usarla (por si hay descuentos o cálculo adicional)
  const finalTotal = (typeof total !== 'undefined' && !isNaN(total)) ? parseFloat(total) : localTotal;
  paymentTotalAmount.textContent = finalTotal.toFixed(2);
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
function populatePaymentSummary() {
paymentItemsDiv.innerHTML = "";
let localTotal = 0;
if (!Array.isArray(selectedRooms) || selectedRooms.length === 0) {
    paymentItemsDiv.innerHTML = "<p>No hay habitaciones seleccionadas.</p>";
    paymentTotalAmount.textContent = "0.00";
    return;
}
selectedRooms.forEach(id => {
    const name = (typeof roomNames !== 'undefined' && roomNames[id]) ? roomNames[id] : id;
    const price = (typeof roomPrices !== 'undefined' && roomPrices[id]) ? parseFloat(roomPrices[id]) : 0;
    localTotal += isNaN(price) ? 0 : price;
    const item = document.createElement("div");
    item.className = "payment_item";
    item.innerHTML = `<span>Habitación ${name}</span> <span>S/. ${ (isNaN(price) ? 0 : price).toFixed(2) }</span>`;
    paymentItemsDiv.appendChild(item);
});
const final = computeFinalTotal();
paymentTotalAmount.textContent = Number(final || localTotal).toFixed(2);
}

document.addEventListener("DOMContentLoaded", () => {
  // ======== CLIENTE NATURAL ========
  const btnBuscarNatural = document.getElementById("buscar_natural_doc");
  const numDocNatural = document.getElementById("num_doc_natural");

  btnBuscarNatural.addEventListener("click", async () => {
    if (btnBuscarNatural.dataset.mode !== "borrar") {
      // --- MODO BUSCAR ---
      const numDoc = numDocNatural.value.trim();
      if (!numDoc) {
        alert("Ingrese un número de documento.");
        return;
      }

      try {
        const response = await fetch(`/Rutas/buscar_cliente_natural?num_doc=${encodeURIComponent(numDoc)}`);
        const data = await response.json();

        if (!response.ok) {
          alert(data.mensaje || data.error || "Cliente no encontrado.");
          return;
        }

        // --- CLIENTE ENCONTRADO: rellenar campos ---
        document.getElementById("nombres").value = data.nombres || "";
        document.getElementById("ape_paterno").value = data.ape_paterno || "";
        document.getElementById("ape_materno").value = data.ape_materno || "";
        document.getElementById("telefono_natural").value = data.telefono || "";
        document.getElementById("pais_select").value = data.id_pais || "";

        // Bloquear los campos
        bloquearCampos(["nombres", "ape_paterno", "ape_materno", "telefono_natural", "pais_select", "num_doc_natural"]);

        // Cambiar botón
        btnBuscarNatural.textContent = "Borrar";
        btnBuscarNatural.dataset.mode = "borrar";
      } catch (error) {
        console.error("Error al buscar cliente natural:", error);
        alert("Ocurrió un error al buscar el cliente.");
      }
    } else {
      // --- MODO BORRAR ---
      limpiarCampos(["nombres", "ape_paterno", "ape_materno", "telefono_natural", "pais_select", "num_doc_natural"]);
      desbloquearCampos(["nombres", "ape_paterno", "ape_materno", "telefono_natural", "pais_select", "num_doc_natural"]);

      btnBuscarNatural.textContent = "Buscar";
      delete btnBuscarNatural.dataset.mode;
    }
  });

  // ======== CLIENTE JURÍDICO ========
  const btnBuscarJuridico = document.getElementById("buscar_juridica_doc");
  const numDocJuridico = document.getElementById("num_doc_juridico");

  btnBuscarJuridico.addEventListener("click", async () => {
    if (btnBuscarJuridico.dataset.mode !== "borrar") {
      // --- MODO BUSCAR ---
      const numDoc = numDocJuridico.value.trim();
      if (!numDoc) {
        alert("Ingrese un RUC.");
        return;
      }

      try {
        const response = await fetch(`/Rutas/buscar_cliente_juridico?num_doc=${encodeURIComponent(numDoc)}`);
        const data = await response.json();

        if (!response.ok) {
          alert(data.mensaje || data.error || "Cliente no encontrado.");
          return;
        }

        // --- CLIENTE ENCONTRADO: rellenar campos ---
        document.getElementById("razon_social").value = data.razon_social || "";
        document.getElementById("telefono_juridico").value = data.telefono || "";
        document.getElementById("pais_select_j").value = data.id_pais || "";
        document.getElementById("direccion_juridica").value = data.direccion || "";
        document.getElementById("tipo_empresa").value = data.tipoemp_id || "";

        // Bloquear los campos
        bloquearCampos([
          "razon_social",
          "telefono_juridico",
          "pais_select_j",
          "direccion_juridica",
          "tipo_empresa",
          "num_doc_juridico",
        ]);

        // Cambiar botón
        btnBuscarJuridico.textContent = "Borrar";
        btnBuscarJuridico.dataset.mode = "borrar";
      } catch (error) {
        console.error("Error al buscar cliente jurídico:", error);
        alert("Ocurrió un error al buscar el cliente.");
      }
    } else {
      // --- MODO BORRAR ---
      limpiarCampos([
        "razon_social",
        "telefono_juridico",
        "pais_select_j",
        "direccion_juridica",
        "tipo_empresa",
        "num_doc_juridico",
      ]);
      desbloquearCampos([
        "razon_social",
        "telefono_juridico",
        "pais_select_j",
        "direccion_juridica",
        "tipo_empresa",
        "num_doc_juridico",
      ]);

      btnBuscarJuridico.textContent = "Buscar";
      delete btnBuscarJuridico.dataset.mode;
    }
  });

  // ======== Funciones auxiliares ========
  function bloquearCampos(ids) {
    ids.forEach(id => {
      const el = document.getElementById(id);
      if (el) el.disabled = true;
    });
  }

  function desbloquearCampos(ids) {
    ids.forEach(id => {
      const el = document.getElementById(id);
      if (el) el.disabled = false;
    });
  }

  function limpiarCampos(ids) {
    ids.forEach(id => {
      const el = document.getElementById(id);
      if (el && el.tagName === "SELECT") {
        el.selectedIndex = 0;
      } else if (el) {
        el.value = "";
      }
    });
  }
});

