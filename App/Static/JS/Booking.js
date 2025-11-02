document.addEventListener("DOMContentLoaded", function () {
  const entrada = document.getElementById("Start_booking_date");
  const salida = document.getElementById("End_booking_date");

  // ⏰ Establecer fecha y hora mínima (actual)
  const ahora = new Date();
  const formatoLocal = ahora.toISOString().slice(0, 16); // YYYY-MM-DDTHH:mm
  entrada.min = formatoLocal;

  // 🎯 Cuando se seleccione una fecha de entrada:
  entrada.addEventListener("change", function () {
    if (entrada.value) {
      salida.disabled = false;
      salida.min = entrada.value;

      // Si ya hay fecha de salida, validamos diferencia mínima
      validarDiferenciaHoras();
    } else {
      salida.disabled = true;
      salida.value = "";
    }
  });

  // ⏱ Validar en tiempo real cuando cambie la salida
  salida.addEventListener("change", validarDiferenciaHoras);

  // 🧾 Validación al enviar formulario
  document.querySelector(".booking_phase").addEventListener("submit", function (event) {
    const entradaVal = entrada.value.trim();
    const salidaVal = salida.value.trim();

    if (!entradaVal || !salidaVal) {
      event.preventDefault();
      alert("⚠️ Debes completar ambas fechas antes de buscar.");
      return;
    }

    const fechaEntrada = new Date(entradaVal);
    const fechaSalida = new Date(salidaVal);
    const ahora = new Date();

    if (fechaEntrada < ahora) {
      event.preventDefault();
      alert("⚠️ La fecha de entrada no puede ser anterior a la fecha actual.");
      return;
    }

    if (fechaSalida <= fechaEntrada) {
    // Bloquea fechas anteriores o iguales a la entrada
    salida.min = new Date(fechaEntrada.getTime() + 60 * 60 * 1000).toISOString().slice(0, 16);
    salida.value = salida.min; // Ajusta automáticamente a 1 hora después
    return;
    }
    const diferenciaHoras = (fechaSalida - fechaEntrada) / (1000 * 60 * 60);
    if (diferenciaHoras < 3) {
      event.preventDefault();
      alert("⚠️ Debe haber al menos 3 horas de diferencia entre entrada y salida.");
    }
  });

  // 📏 Función para validar diferencia mínima de 3 horas
  function validarDiferenciaHoras() {
    if (!entrada.value || !salida.value) return;

    const fechaEntrada = new Date(entrada.value);
    const fechaSalida = new Date(salida.value);
    const diferenciaHoras = (fechaSalida - fechaEntrada) / (1000 * 60 * 60);

    if (fechaSalida <= fechaEntrada) {
      alert("⚠️ La fecha de salida debe ser posterior a la de entrada.");
      salida.value = "";
      return;
    }

    if (diferenciaHoras < 1) {
      alert("⚠️ Debe haber al menos 1 horas de diferencia entre la entrada y la salida.");
      // Ajusta automáticamente la salida
      const nuevaSalida = new Date(fechaEntrada.getTime() + 1 * 60 * 60 * 1000);
      salida.value = nuevaSalida.toISOString().slice(0, 16);
    }
  }
});
