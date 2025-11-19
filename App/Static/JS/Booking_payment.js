const paymentMethodInputs = document.getElementsByName("payment_method");
const step4El = document.getElementById("step4");

const processPaymentBtn = document.getElementById("process_payment");
const paymentItemsDiv = document.getElementById("payment_items");
const paymentTotalAmount = document.getElementById("payment_total_amount");
const cardForm = document.getElementById("card_form");
const cardHolderInput = document.getElementById("card_holder");
const cardNumberInput = document.getElementById("card_number");
const cardExpInput = document.getElementById("card_exp");
const cardExpMonthSelect = document.getElementById("card_exp_month");
const cardExpYearSelect = document.getElementById("card_exp_year");
const cardCvvInput = document.getElementById("card_cvv");
const finalizarReservaBtn = document.getElementById("finalizar_reserva");
const step5El = document.getElementById("step5");
const downloadLink = document.getElementById("download_comprobante_link") || document.createElement("a");
const openNewTabBtn = document.getElementById("open_comprobante_newtab");
const comprobanteStatus = document.getElementById("comprobante_status");
const volverHome = document.getElementById("volver_home");
const correoComprobanteInput = document.getElementById("correo_comprobante");
const enviarComprobanteBtn = document.getElementById("enviar_comprobante_correo");
const comprobanteEmailStatus = document.getElementById("comprobante_email_status");
const qrSection = document.getElementById("qr_payment_section");
const qrImage = document.getElementById("qr_payment_image");
const transferSection = document.getElementById("transfer_payment_section");

let ultimaReservaId = null;
let confettiTimeout = null;

const setEmailStatus = (type, message) => {
  if (!comprobanteEmailStatus) return;
  comprobanteEmailStatus.textContent = message || "";
  comprobanteEmailStatus.classList.remove("success", "error");
  if (type === "success" || type === "error") {
    comprobanteEmailStatus.classList.add(type);
  }
};

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

function sanitizeCardHolder(value) {
  if (typeof value !== "string") return "";
  let cleaned = value
    .normalize("NFD")
    .replace(/[^A-Za-zÀ-ÿñÑüÜ\s]/g, "")
    .replace(/\s+/g, " ")
    .trim();
  if (cleaned.length > 50) {
    cleaned = cleaned.slice(0, 50);
  }
  return cleaned;
}

function validateCardHolder(value) {
  if (!value) return { valid: false, message: "Ingrese el nombre del titular." };
  if (!/^[A-Za-zÀ-ÿñÑüÜ]+(?:\s[A-Za-zÀ-ÿñÑüÜ]+)*$/.test(value)) {
    return { valid: false, message: "El titular solo puede contener letras y un espacio entre cada nombre." };
  }
  if (value.length > 50) {
    return { valid: false, message: "El titular no debe exceder 50 caracteres." };
  }
  return { valid: true };
}

function formatMonthValue(value) {
  if (!value || value.indexOf("-") === -1) return null;
  const [yearStr, monthStr] = value.split("-");
  const year = parseInt(yearStr, 10);
  const month = parseInt(monthStr, 10);
  if (!year || !month || month < 1 || month > 12) return null;

  const now = new Date();
  const currentYear = now.getFullYear();
  const currentMonth = now.getMonth() + 1;
  if (year < currentYear || (year === currentYear && month < currentMonth)) {
    return { valid: false, message: "La fecha de expiración debe ser futura." };
  }
  return {
    valid: true,
    year,
    month,
    formatted: `${String(month).padStart(2, "0")}/${String(year).slice(-2)}`
  };
}

function setCardExpMin() {
  if (!cardExpInput) return;
  const now = new Date();
  const min = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
  cardExpInput.min = min;
}

if (cardHolderInput) {
  cardHolderInput.addEventListener("input", () => {
    const sanitized = sanitizeCardHolder(cardHolderInput.value);
    if (cardHolderInput.value !== sanitized) {
      cardHolderInput.value = sanitized;
    }
  });
}

setCardExpMin();

// Inicializar años para el select de expiración (próximos 10 años)
if (cardExpYearSelect) {
  const currentYear = new Date().getFullYear();
  for (let i = 0; i < 10; i++) {
    const year = currentYear + i;
    const option = document.createElement("option");
    option.value = String(year).slice(-2);
    option.textContent = String(year).slice(-2);
    cardExpYearSelect.appendChild(option);
  }
}

// Sincronizar selects de mes/año con input hidden
function updateCardExpHidden() {
  if (!cardExpInput || !cardExpMonthSelect || !cardExpYearSelect) return;
  
  const month = cardExpMonthSelect.value;
  const year = cardExpYearSelect.value;
  
  if (month && year) {
    // Convertir año de 2 dígitos a 4 dígitos
    const currentYear = new Date().getFullYear();
    const currentCentury = Math.floor(currentYear / 100) * 100;
    const fullYear = currentCentury + parseInt(year);
    
    // Formato: YYYY-MM
    cardExpInput.value = `${fullYear}-${month.padStart(2, '0')}`;
  } else {
    cardExpInput.value = '';
  }
}

if (cardExpMonthSelect) {
  cardExpMonthSelect.addEventListener('change', updateCardExpHidden);
}

if (cardExpYearSelect) {
  cardExpYearSelect.addEventListener('change', updateCardExpHidden);
}

function launchConfetti() {
  if (typeof confetti !== "function") return;
  if (confettiTimeout) {
    clearInterval(confettiTimeout);
    confettiTimeout = null;
  }

  const duration = 15 * 1000;
  const animationEnd = Date.now() + duration;
  const defaults = { startVelocity: 30, spread: 360, ticks: 60, zIndex: 9999 };

  function randomInRange(min, max) {
    return Math.random() * (max - min) + min;
  }

  confettiTimeout = setInterval(() => {
    const timeLeft = animationEnd - Date.now();
    if (timeLeft <= 0) {
      clearInterval(confettiTimeout);
      confettiTimeout = null;
      return;
    }

    const particleCount = 50 * (timeLeft / duration);
    confetti(Object.assign({}, defaults, {
      particleCount,
      origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 }
    }));
    confetti(Object.assign({}, defaults, {
      particleCount,
      origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 }
    }));
  }, 250);
}

async function waitForReservationValidation(reservaId, statusLabel) {
  if (!reservaId) return false;
  let attempt = 0;
  let countdownInterval = null;
  const MAX_ATTEMPTS = 20;
  const POLL_DELAY_MS = 10_000;
  const WARN_THRESHOLD = Math.floor(MAX_ATTEMPTS * 0.75);

  const stopCountdown = () => {
    if (countdownInterval) {
      clearInterval(countdownInterval);
      countdownInterval = null;
    }
  };

  while (true) {
    if (attempt >= MAX_ATTEMPTS) {
      stopCountdown();
      if (statusLabel) statusLabel.textContent = "No fue posible validar el pago. Cancelando la reserva…";
      try {
        await fetch(`/Rutas/TEMPLATES/reserva/${encodeURIComponent(reservaId)}`, { method: "DELETE" });
      } catch (err) {
        console.error("[PAGO] Error cancelando reserva tras tiempo agotado:", err);
      }
      return false;
    }
    attempt += 1;
    let secondsLeft = POLL_DELAY_MS / 1000;
    const updateLabel = () => {
      if (!statusLabel) return;
      const extra = attempt >= WARN_THRESHOLD ? " (seguimos insistiendo…)" : "";
      statusLabel.textContent = `Esperando validación del pago... (verificación ${attempt}/${MAX_ATTEMPTS} | reintento en ${secondsLeft}s)${extra}`;
    };
    updateLabel();
    stopCountdown();
    countdownInterval = setInterval(() => {
      secondsLeft -= 1;
      if (secondsLeft <= 0) {
        stopCountdown();
        return;
      }
      updateLabel();
    }, 1000);
    try {
      const resp = await fetch(`/Rutas/TEMPLATES/reserva/${encodeURIComponent(reservaId)}/estado`, { cache: "no-store" });
      if (resp.ok) {
        const data = await resp.json();
        if (data && String(data.validado).trim() === "1") {
          stopCountdown();
          if (statusLabel) statusLabel.textContent = "Pago validado. Continuando con el proceso…";
          launchConfetti();
          return true;
        }
      } else if (resp.status === 404) {
        console.warn("[PAGO] Reserva no encontrada durante validación.");
        stopCountdown();
        return false;
      }
    } catch (err) {
      console.error("[PAGO] Error consultando validación:", err);
    }
    await sleep(POLL_DELAY_MS);
  }
}

function togglePaymentMethodUI(methodValue) {
  const value = methodValue || document.querySelector('input[name="payment_method"]:checked')?.value || "2";
  if (cardForm) cardForm.style.display = value === "2" ? "block" : "none";
  if (qrSection) qrSection.classList.toggle("hidden", value !== "4");
  if (transferSection) transferSection.classList.toggle("hidden", value !== "5");
  if (value === "4") {
    generateQrForAmount();
  }
}

function generateQrForAmount() {
  if (!qrImage) return;
  const total = computeFinalTotal();
  const payload = encodeURIComponent(`YAPE|952225506|${total.toFixed(2)}|${Date.now()}`);
  qrImage.src = `https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=${payload}`;
}

window.__updateQrPayment = generateQrForAmount;

Array.from(paymentMethodInputs).forEach(r => {
  r.addEventListener("change", () => {
    togglePaymentMethodUI(r.value);
  });
});

togglePaymentMethodUI();

document.getElementById("payment_phase")?.addEventListener("click", (e) => {
  e.preventDefault();

  limpiarErrores(); // Limpia mensajes anteriores

  // Validar todos los huéspedes de todas las habitaciones
  let primerHuespedFaltante = null;
  let primeraHabitacionFaltante = null;
  let primerIndiceFaltante = null;

  // Obtener todas las habitaciones seleccionadas
  const habitacionesForms = document.querySelectorAll('.habitacion_form');
  
  for (const habitacionForm of habitacionesForms) {
    // Obtener el ID de la habitación desde el select de cantidad de personas
    const numPersonasSelect = habitacionForm.querySelector('.numPersonas');
    if (!numPersonasSelect) continue;
    
    const roomId = numPersonasSelect.dataset.room || numPersonasSelect.id.replace('numPersonas_', '');
    const contenedorHuespedes = document.getElementById(`huespedes_${roomId}`);
    if (!contenedorHuespedes) continue;

    // Obtener todos los cards de huéspedes (incluso los ocultos)
    const huespedCards = contenedorHuespedes.querySelectorAll('.huesped_card');
    
    huespedCards.forEach((card, cardIndex) => {
      const huespedIndex = parseInt(card.dataset.huespedIndex) || (cardIndex + 1);
      const nombre = card.querySelector('.nombre_huesped')?.value.trim() || '';
      const apeP = card.querySelector('.apellido_huesped')?.value.trim() || '';
      const apeM = card.querySelector('.apellido_huesped_m')?.value.trim() || '';
      const doc = card.querySelector('.doc_huesped')?.value.trim() || '';

      // Verificar si falta algún dato
      if (!nombre || !apeP || !apeM || !doc || !/^\d{8}$/.test(doc)) {
        // Si es el primer huésped faltante encontrado, guardarlo
        if (!primerHuespedFaltante) {
          primerHuespedFaltante = huespedIndex;
          primeraHabitacionFaltante = roomId;
          primerIndiceFaltante = huespedIndex;
        }
      }
    });
  }

  // Si se encontró un huésped faltante, navegar a él
  if (primerHuespedFaltante !== null && primeraHabitacionFaltante) {
    // Navegar al huésped faltante
    if (typeof window.navigateHuesped === 'function' && window.huespedNavigationState) {
      const state = window.huespedNavigationState[primeraHabitacionFaltante];
      if (state) {
        // Calcular cuántos pasos necesitamos avanzar
        const pasosNecesarios = primerIndiceFaltante - state.current;
        
        // Navegar al huésped faltante
        if (pasosNecesarios > 0) {
          for (let i = 0; i < pasosNecesarios; i++) {
            window.navigateHuesped(primeraHabitacionFaltante, 1);
          }
        } else if (pasosNecesarios < 0) {
          for (let i = 0; i < Math.abs(pasosNecesarios); i++) {
            window.navigateHuesped(primeraHabitacionFaltante, -1);
          }
        }
        
        // Hacer scroll a la habitación correspondiente
        const numPersonasSelect = document.getElementById(`numPersonas_${primeraHabitacionFaltante}`);
        if (numPersonasSelect) {
          const habitacionForm = numPersonasSelect.closest('.habitacion_form');
          if (habitacionForm) {
            habitacionForm.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
        }
        
        // Mostrar mensaje
        const roomName = typeof roomNames !== 'undefined' && roomNames[primeraHabitacionFaltante] 
          ? roomNames[primeraHabitacionFaltante] 
          : primeraHabitacionFaltante;
        showBookingAlert(`⚠️ Por favor, completa los datos del Huésped ${primerIndiceFaltante} de la Habitación ${roomName} antes de continuar.`, 'warning');
        return;
      }
    } else {
      // Fallback: mostrar mensaje genérico
      showBookingAlert('⚠️ Por favor, completa todos los datos de los huéspedes antes de continuar.', 'warning');
      return;
    }
  }

  // Si pasa todas las validaciones, continuar al siguiente paso
  if (step3El) step3El.style.display = "none";
  if (step4El) {
    populatePaymentSummary_new();
    step4El.style.display = "block";
    // Scroll hacia arriba al cambiar de paso
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
});

// 🧩 Función auxiliar para asignar un ID temporal si el input no tiene uno
function agregarIdTemporal(elemento) {
  const tempId = "temp_" + Math.random().toString(36).substr(2, 9);
  elemento.id = tempId;
  return tempId;
}


// --- processPaymentBtn: valida tarjeta (si aplica), prepara dataReserva y habilita finalizar ---
processPaymentBtn?.addEventListener("click", async () => {
console.group("%c[PAGO] Iniciando validación y pre-procesamiento", "color: teal; font-weight: bold;");
const method = document.querySelector('input[name="payment_method"]:checked')?.value || '2';

// Validaciones de tarjeta si método card
if (method === '2') {
    const holderValue = sanitizeCardHolder(cardHolderInput?.value || "");
    if (cardHolderInput && cardHolderInput.value !== holderValue) {
      cardHolderInput.value = holderValue;
    }
    const number = (cardNumberInput?.value || "").replace(/\s+/g, '');
    // Obtener valor del input hidden o construir desde selects
    let expRaw = cardExpInput?.value || "";
    if (!expRaw && cardExpMonthSelect && cardExpYearSelect) {
      const month = cardExpMonthSelect.value;
      const year = cardExpYearSelect.value;
      if (month && year) {
        const currentYear = new Date().getFullYear();
        const currentCentury = Math.floor(currentYear / 100) * 100;
        const fullYear = currentCentury + parseInt(year);
        expRaw = `${fullYear}-${month.padStart(2, '0')}`;
      }
    }
    const cvv = (cardCvvInput?.value || "").trim();

    console.log("[PAGO] Método card seleccionado. Validando campos de tarjeta...");
    const holderValidation = validateCardHolder(holderValue);
    if (!holderValidation.valid) {
      showBookingAlert(holderValidation.message, 'warning');
      console.groupEnd();
      return;
    }

    if (!number || !expRaw || !cvv) {
      showBookingAlert("Complete todos los datos de la tarjeta.", "warning");
      console.groupEnd();
      return;
    }
    if (!/^\d{13,19}$/.test(number)) { showBookingAlert("Número de tarjeta inválido.", "warning"); console.groupEnd(); return; }

    const expResult = formatMonthValue(expRaw);
    if (!expResult || !expResult.valid) {
      showBookingAlert(expResult?.message || "Fecha de expiración inválida.", "warning");
      console.groupEnd();
      return;
    }

    if (!/^\d{3,4}$/.test(cvv)) { showBookingAlert("CVV inválido.", "warning"); console.groupEnd(); return; }
}

// Mostrar resumen actualizado
populatePaymentSummary_new();
finalizarReservaBtn.click();

console.groupEnd();
});
// --- finalizarReservaBtn: flujo completo (guardar reserva -> guardar transaccion -> generar comprobante) ---

if (finalizarReservaBtn) {
  finalizarReservaBtn.addEventListener("click", async () => {
    // === MOSTRAR MODAL DE PROCESAMIENTO ===
    const modal = document.getElementById("paymentModal");
    const loader = document.getElementById("loader");
    const status = document.getElementById("paymentStatus");

    modal.style.display = "flex";
    loader.style.display = "block";
    status.textContent = "Procesando pago...";
    status.classList.remove("success");

    finalizarReservaBtn.disabled = true;
    finalizarReservaBtn.textContent = "Guardando reserva...";
    console.group("%c[FINALIZAR] Inicio del flujo guardar_reserva -> transaccion -> comprobante", "color: blue; font-weight: bold;");

    // RECOLECTAR datos de reserva
    let dataReserva;
    try {
      if (typeof recolectarDatosReserva !== 'function') throw new Error("recolectarDatosReserva() no encontrada");
      dataReserva = recolectarDatosReserva();
      console.log("[FINALIZAR] dataReserva:", dataReserva);
    } catch (err) {
      console.error("[FINALIZAR] Error construyendo dataReserva:", err);
      showBookingAlert("No se pudieron recolectar los datos de la reserva. Revisa la consola.", "error");
      finalizarReservaBtn.disabled = false;
      finalizarReservaBtn.textContent = "Finalizar Reserva";
      modal.style.display = "none"; // cerrar modal si hay error
      console.groupEnd();
      return;
    }

    // === 1) Guardar reserva ===
    let reservaId = null;
    try {
      console.log("[FINALIZAR] Enviando request a /Rutas/TEMPLATES/guardar_reserva ...");
      const resp = await fetch("/Rutas/TEMPLATES/guardar_reserva", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dataReserva)
      });

      const rawText = await resp.text();
      console.log("[FINALIZAR] Response HTTP:", resp.status, resp.ok);
      console.log("[FINALIZAR] Response RAW:", rawText);

      let result;
      try {
        result = JSON.parse(rawText);
        console.log("[FINALIZAR] JSON parseado:", result);
      } catch (e) {
        console.error("[FINALIZAR] No se pudo parsear JSON:", e);
        showBookingAlert("Respuesta inesperada del servidor. Revisa la consola.", "error");
        throw e;
      }

      if (resp.ok && result && result.success && result.reserva_id) {
        reservaId = result.reserva_id;
        console.log("[FINALIZAR] Reserva guardada OK. ID:", reservaId);
      } else {
        console.error("[FINALIZAR] El backend devolvió un formato inesperado:", result);
        showBookingAlert("Ocurrió un problema al guardar la reserva. Revisa la consola.", "error");
        throw new Error("Formato de respuesta inválido al guardar reserva");
      }
    } catch (errSave) {
      console.error("[FINALIZAR] Error guardando reserva:", errSave);
      finalizarReservaBtn.disabled = false;
      finalizarReservaBtn.textContent = "Finalizar Reserva";
      modal.style.display = "none";
      console.groupEnd();
      return;
    }

    ultimaReservaId = reservaId;

    // Esperar validación externa
    status.textContent = "Esperando validación del pago...";
    const validado = await waitForReservationValidation(reservaId, status);
    if (!validado) {
      loader.style.display = "none";
      status.textContent = "No fue posible validar el pago automáticamente. Redirigiendo al inicio…";
      finalizarReservaBtn.disabled = false;
      finalizarReservaBtn.textContent = "Finalizar Reserva";
      setTimeout(() => {
        window.location.href = window.BOOKING_HOME_URL || "/";
      }, 3000);
      console.groupEnd();
      return;
    }

    // === 2) Guardar transacción ===
    const selectedPaymentRadio = document.querySelector('input[name="payment_method"]:checked');
    if (!selectedPaymentRadio) {
      showBookingAlert("Por favor, selecciona un método de pago antes de continuar.", "warning");
      console.warn("⚠️ No se seleccionó ningún método de pago.");
      modal.style.display = "none";
      return;
    }

    const selectedPaymentMethod = parseInt(selectedPaymentRadio.value); 
    const FinalTotal = computeFinalTotal();

    try {    
      console.log("[FINALIZAR] Enviando transacción:", { reservaId, selectedPaymentMethod, FinalTotal });

      const resp = await fetch("/Rutas/guardar_transaccion", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          reservaId: reservaId,
          paymentMethodInputs: selectedPaymentMethod,
          finalTotal: FinalTotal,
          estado: 1
        })
      });

      const transText = await resp.text();
      console.log("[FINALIZAR] transResp HTTP:", resp.status, resp.ok);
      console.log("[FINALIZAR] transResp RAW:", transText);

      let transResult;
      try {
        transResult = JSON.parse(transText);
        console.log("[FINALIZAR] transResult:", transResult);
      } catch (e) {
        console.error("[FINALIZAR] No se parseó transResult:", e);
        throw e;
      }

      if (!(resp.ok && transResult && (transResult.transaccion_id || transResult.success))) {
        console.warn("[FINALIZAR] Advertencia: no se pudo guardar la transacción correctamente.", transResult);
      } else {
        console.log("[FINALIZAR] Transacción registrada OK:", transResult);
      }

    } catch (errTrans) {
      console.error("[FINALIZAR] Error guardando transacción:", errTrans);
      showBookingAlert("Error al guardar la transacción. Revisa la consola.", "error");
    }

    // === 3) Generar comprobante ===
    try {
      if (step4El) step4El.style.display = "none";
      if (step5El) step5El.style.display = "block";
      
      // Limpiar datos de reserva para desactivar interceptación de navegación
      // El pago ya se completó, permitir navegación libre
      if (typeof selectedRooms !== 'undefined') {
        selectedRooms = [];
      }
      if (typeof selectedServices !== 'undefined') {
        selectedServices = [];
      }
      if (typeof serviceQuantities !== 'undefined') {
        serviceQuantities = {};
      }
      if (typeof clientData !== 'undefined') {
        clientData = {};
      }
      localStorage.removeItem('booking_pending_data');
      
      // Detener temporizador si está corriendo
      if (window.bookingTimer && typeof window.bookingTimer.stop === 'function') {
        window.bookingTimer.stop(false);
      }
      
      // Scroll hacia arriba al cambiar de paso
      window.scrollTo({ top: 0, behavior: 'smooth' });
      if (comprobanteStatus) comprobanteStatus.textContent = "Generando comprobante...";

      console.log("[FINALIZAR] Solicitando PDF a /Rutas/crear_comprobante/" + encodeURIComponent(reservaId));

      const pdfResp = await fetch(`/Rutas/crear_comprobante/${encodeURIComponent(reservaId)}`, {
        method: "GET",
        headers: { "Accept": "application/pdf" }
      });

      if (!pdfResp.ok) {
        const txt = await pdfResp.text();
        console.error("[FINALIZAR] Error al generar PDF. Status:", pdfResp.status, "Body:", txt);
        throw new Error("No se pudo generar el comprobante PDF");
      }

      const pdfBlob = await pdfResp.blob();
      const pdfUrl = URL.createObjectURL(pdfBlob);
      const filename = `Comprobante_${reservaId}.pdf`;

      ultimaReservaId = reservaId;

      const downloadLink = document.getElementById("download_comprobante_link");
      const openTabBtn = document.getElementById("open_comprobante_newtab");

      if (downloadLink) {
        downloadLink.href = pdfUrl;
        downloadLink.download = filename;
        downloadLink.style.display = "inline-block";
      }

      if (openTabBtn) {
        openTabBtn.style.display = "inline-block";
        openTabBtn.onclick = () => window.open(pdfUrl, "_blank");
      }

      if (comprobanteStatus) comprobanteStatus.textContent = "Comprobante generado correctamente.";
      console.log("[FINALIZAR] Comprobante disponible:", filename);

      if (window.bookingTimer && typeof window.bookingTimer.stop === 'function') {
        window.bookingTimer.stop(true);
      }

      // ✅ Todo salió bien: mostrar mensaje de éxito en el modal
      loader.style.display = "none";
      status.textContent = "✅ Pago exitoso";
      status.classList.add("success");

      await new Promise(r => setTimeout(r, 1500)); // Espera 1.5s
      modal.style.display = "none";

    } catch (errPdf) {
      console.error("[FINALIZAR] Error generando comprobante:", errPdf);
      if (comprobanteStatus) comprobanteStatus.textContent = "Error generando comprobante. Intente descargar luego.";
      showBookingAlert("Se produjo un error al generar el comprobante. Revisa la consola.", "error");
      modal.style.display = "none";
    }

    finalizarReservaBtn.disabled = false;
    finalizarReservaBtn.textContent = "Finalizar Reserva";
    console.groupEnd();
  });
}


volverHome?.addEventListener("click", () => {
  if (window.bookingTimer && typeof window.bookingTimer.stop === 'function') {
    window.bookingTimer.stop(true);
  }
});


enviarComprobanteBtn?.addEventListener("click", async () => {
  if (!ultimaReservaId) {
    showBookingAlert("Aún no se ha generado un comprobante para esta reserva.", "warning");
    return;
  }

  const correo = correoComprobanteInput?.value.trim();
  if (!correo) {
    setEmailStatus("error", "Ingresa un correo electrónico válido.");
    correoComprobanteInput?.focus();
    return;
  }

  const correoValido = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo);
  if (!correoValido) {
    setEmailStatus("error", "El formato del correo no es válido.");
    correoComprobanteInput?.focus();
    return;
  }

  setEmailStatus(null, "Enviando comprobante...");
  enviarComprobanteBtn.disabled = true;

  try {
    const resp = await fetch(`/Rutas/enviar_comprobante/${encodeURIComponent(ultimaReservaId)}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: correo })
    });

    const result = await resp.json().catch(() => ({ success: false, message: "Respuesta inesperada del servidor." }));

    if (resp.ok && result?.success) {
      setEmailStatus("success", result.message || "Comprobante enviado correctamente.");
    } else {
      const mensaje = result?.message || "No se pudo enviar el comprobante por correo.";
      setEmailStatus("error", mensaje);
    }
  } catch (error) {
    console.error("[COMPROBANTE] Error enviando correo:", error);
    setEmailStatus("error", "Ocurrió un error al enviar el comprobante. Intenta nuevamente.");
  } finally {
    enviarComprobanteBtn.disabled = false;
  }
});


