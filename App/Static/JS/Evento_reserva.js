document.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("search-button");
    const fechaInput = document.getElementById("search-fecha");
    const entradaInput = document.getElementById("search-hora-entrada");
    const salidaInput = document.getElementById("search-hora-salida");
    const eventoFecha = document.getElementById("evento-fecha");
    const eventoEntrada = document.getElementById("evento-hora-entrada");
    const eventoSalida = document.getElementById("evento-hora-salida");
    const errorBox = document.getElementById("search-error");

    const showError = msg => {
        errorBox.textContent = msg;
        errorBox.style.display = "block";
    };
    const hideError = () => errorBox.style.display = "none";
    const limpiar = () => {
        [fechaInput, entradaInput, salidaInput].forEach(el => el.value = "");
        [eventoFecha, eventoEntrada, eventoSalida].forEach(el => el && (el.value = ""));
    };

    const hayConflicto = (entrada, salida, reservas) => {
        const [h1, m1] = entrada.split(":").map(Number);
        const [h2, m2] = salida.split(":").map(Number);
        const inicio = h1 * 60 + m1, fin = h2 * 60 + m2;

        return reservas.some(r => {
            const [rH1, rM1] = r.hora_inicio.split(":").map(Number);
            const [rH2, rM2] = r.hora_fin.split(":").map(Number);
            const ini = rH1 * 60 + rM1, finR = rH2 * 60 + rM2;
            return inicio < finR && fin > ini;
        });
    };

    btn.addEventListener("click", async e => {
        e.preventDefault();
        hideError();

        const fecha = fechaInput.value;
        const hEntrada = entradaInput.value;
        const hSalida = salidaInput.value;

        if (!fecha || !hEntrada || !hSalida) {
            showError("Completa todos los campos de fecha y hora.");
            limpiar();
            return;
        }

        const fechaInicio = new Date(`${fecha}T${hEntrada}`);
        const fechaFin = new Date(`${fecha}T${hSalida}`);
        const hoy = new Date(); hoy.setHours(0, 0, 0, 0);

        if (new Date(fecha) < hoy) {
            showError("No puedes seleccionar una fecha anterior al día actual.");
            limpiar();
            return;
        }
        if (fechaFin <= fechaInicio) {
            showError("La hora de salida debe ser posterior a la de entrada.");
            limpiar();
            return;
        }

        const tresHorasAntes = new Date(fechaInicio.getTime() - 3 * 60 * 60 * 1000);
        if (new Date() > tresHorasAntes) {
            showError("Las reservas deben hacerse con al menos 3 horas de anticipación.");
            limpiar();
            return;
        }

        try {
            const res = await fetch(`/Eventos/reservas_fecha?fecha=${fecha}`);
            const data = await res.json();

            if (!data.success) {
                showError(data.message || "Error al verificar disponibilidad.");
                limpiar();
                return;
            }

            if (hayConflicto(hEntrada, hSalida, data.reservas)) {
                showError("Ya existe una reserva en ese horario.");
                limpiar();
                return;
            }

            // Copiar valores
            hideError();
            if (eventoFecha) eventoFecha.value = fecha;
            if (eventoEntrada) eventoEntrada.value = hEntrada;
            if (eventoSalida) eventoSalida.value = hSalida;

        } catch (err) {
            console.error(err);
            showError("Error al consultar disponibilidad.");
            limpiar();
        }
    });
});
