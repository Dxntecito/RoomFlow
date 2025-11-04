const paymentMethodInputs = document.getElementsByName("payment_method");
const step4El = document.getElementById("step4");

const processPaymentBtn = document.getElementById("process_payment");
const paymentItemsDiv = document.getElementById("payment_items");
const paymentTotalAmount = document.getElementById("payment_total_amount");
const cardForm = document.getElementById("card_form");
const finalizarReservaBtn = document.getElementById("finalizar_reserva");
const step5El = document.getElementById("step5");
const downloadLink = document.getElementById("download_comprobante_link") || document.createElement("a");
const openNewTabBtn = document.getElementById("open_comprobante_newtab");
const comprobanteStatus = document.getElementById("comprobante_status");
const volverHome = document.getElementById("volver_home");


// Si el usuario cambia el método de pago, ocultar/mostrar formularios
Array.from(paymentMethodInputs).forEach(r => {
  r.addEventListener("change", () => {
    const method = document.querySelector('input[name="payment_method"]:checked')?.value;
    if (method === "card") {
      cardForm.style.display = "block";
    } else {
      // por ahora no implementado -> ocultar formulario de tarjeta
      cardForm.style.display = "none";
    }
  });
});

// UI: cambio de método de pago (muestra/oculta form tarjeta)
Array.from(document.getElementsByName("payment_method") || []).forEach(r => {
r.addEventListener("change", () => {
    const method = document.querySelector('input[name="payment_method"]:checked')?.value;
    const cardForm = document.getElementById("card_form");
    if (cardForm) cardForm.style.display = (method === "card") ? "block" : "none";
});
});

document.getElementById("payment_phase")?.addEventListener("click", (e) => {
  e.preventDefault();

  limpiarErrores(); // Limpia mensajes anteriores

  // Seleccionamos todos los campos dinámicos de huéspedes
  const nombres = document.querySelectorAll(".nombre_huesped");
  const apellidosP = document.querySelectorAll(".apellido_huesped");
  const apellidosM = document.querySelectorAll(".apellido_huesped_m");
  const documentos = document.querySelectorAll(".doc_huesped");

  let valido = true;

  // Validar cada grupo de huésped
  nombres.forEach((input, index) => {
    const nombre = input.value.trim();
    const apeP = apellidosP[index]?.value.trim();
    const apeM = apellidosM[index]?.value.trim();
    const doc = documentos[index]?.value.trim();

    if (!nombre) {
      mostrarError(input.id || agregarIdTemporal(input), "Ingrese el nombre del huésped.");
      valido = false;
    }
    if (!apeP) {
      mostrarError(apellidosP[index].id || agregarIdTemporal(apellidosP[index]), "Ingrese el apellido paterno.");
      valido = false;
    }
    if (!apeM) {
      mostrarError(apellidosM[index].id || agregarIdTemporal(apellidosM[index]), "Ingrese el apellido materno.");
      valido = false;
    }
    if (!doc) {
      mostrarError(documentos[index].id || agregarIdTemporal(documentos[index]), "Ingrese el número de documento.");
      valido = false;
    } else if (!/^\d{8}$/.test(doc)) {
      mostrarError(documentos[index].id || agregarIdTemporal(documentos[index]), "El documento debe tener 8 dígitos numéricos.");
      valido = false;
    }
  });

  // Si algo no está válido, detener el flujo
  if (!valido) return;

  // Si pasa todas las validaciones, continuar al siguiente paso
  if (step3El) step3El.style.display = "none";
  if (step4El) {
    populatePaymentSummary();
    step4El.style.display = "block";
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
const method = document.querySelector('input[name="payment_method"]:checked')?.value || 'card';

// Validaciones de tarjeta si método card
if (method === 'card') {
    const holder = document.getElementById("card_holder")?.value.trim();
    const number = (document.getElementById("card_number")?.value || "").replace(/\s+/g, '');
    const exp = document.getElementById("card_exp")?.value.trim();
    const cvv = document.getElementById("card_cvv")?.value.trim();

    console.log("[PAGO] Método card seleccionado. Validando campos de tarjeta...");
    if (!holder || !number || !exp || !cvv) {
    alert("Complete todos los datos de la tarjeta.");
    console.groupEnd();
    return;
    }
    if (!/^\d{13,19}$/.test(number)) { alert("Número de tarjeta inválido."); console.groupEnd(); return; }
    if (!/^\d{2}\/\d{2}$/.test(exp)) { alert("Fecha de expiración inválida. Formato MM/AA."); console.groupEnd(); return; }
    if (!/^\d{3,4}$/.test(cvv)) { alert("CVV inválido."); console.groupEnd(); return; }
}

// Mostrar resumen actualizado
populatePaymentSummary();
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
      alert("No se pudieron recolectar los datos de la reserva. Revisa la consola.");
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
        alert("Respuesta inesperada del servidor. Revisa la consola.");
        throw e;
      }

      if (resp.ok && result && result.success && result.reserva_id) {
        reservaId = result.reserva_id;
        console.log("[FINALIZAR] Reserva guardada OK. ID:", reservaId);
      } else {
        console.error("[FINALIZAR] El backend devolvió un formato inesperado:", result);
        alert("Ocurrió un problema al guardar la reserva. Revisa la consola.");
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

    // === 2) Guardar transacción ===
    const selectedPaymentRadio = document.querySelector('input[name="payment_method"]:checked');
    if (!selectedPaymentRadio) {
      alert("Por favor, selecciona un método de pago antes de continuar.");
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
        console.warn("[FINALIZAR] Error en la creación de transacción:", transResult);
        alert("Advertencia: No se pudo guardar la transacción correctamente.");
      } else {
        console.log("[FINALIZAR] Transacción registrada OK:", transResult);
      }

    } catch (errTrans) {
      console.error("[FINALIZAR] Error guardando transacción:", errTrans);
      alert("Error al guardar la transacción. Revisa la consola.");
    }

    // === 3) Generar comprobante ===
    try {
      if (step4El) step4El.style.display = "none";
      if (step5El) step5El.style.display = "block";
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

      // ✅ Todo salió bien: mostrar mensaje de éxito en el modal
      loader.style.display = "none";
      status.textContent = "✅ Pago exitoso";
      status.classList.add("success");

      await new Promise(r => setTimeout(r, 1500)); // Espera 1.5s
      modal.style.display = "none";

    } catch (errPdf) {
      console.error("[FINALIZAR] Error generando comprobante:", errPdf);
      if (comprobanteStatus) comprobanteStatus.textContent = "Error generando comprobante. Intente descargar luego.";
      alert("Se produjo un error al generar el comprobante. Revisa la consola.");
      modal.style.display = "none";
    }

    finalizarReservaBtn.disabled = false;
    finalizarReservaBtn.textContent = "Finalizar Reserva";
    console.groupEnd();
  });
}


