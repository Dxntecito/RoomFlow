document.addEventListener("DOMContentLoaded", () => {
    console.log("✅ eventos.js cargado correctamente");
    console.log("📘 tiposEventos:", typeof tiposEventos !== "undefined" ? tiposEventos : "NO DEFINIDO");

    // ==============================
    // 🔹 VARIABLES GLOBALES
    // ==============================
    let totalEvento = 0;
    let totalServicios = 0;
    let horas = 0;

    // ==============================
    // 🔹 FUNCIONES DE CÁLCULO
    // ==============================
    function calcularHoras(entrada, salida) {
        if (!entrada || !salida) return 0;
        const [h1, m1] = entrada.split(":").map(Number);
        const [h2, m2] = salida.split(":").map(Number);
        let diff = (h2 + m2 / 60) - (h1 + m1 / 60);
        if (diff < 0) diff += 24;
        return diff;
    }

    function actualizarResumen() {
        const fecha = document.getElementById("evento-fecha")?.value || "";
        const entrada = document.getElementById("evento-hora-entrada")?.value || "";
        const salida = document.getElementById("evento-hora-salida")?.value || "";
        const tipoEventoSelect = document.querySelector('select[name="tipo_evento_id"]');
        const tipoEventoIdRaw = tipoEventoSelect ? tipoEventoSelect.value : null;
        const tipoEventoId = tipoEventoIdRaw ? parseInt(tipoEventoIdRaw) : null;

        horas = calcularHoras(entrada, salida);

        // Validar que tiposEventos esté disponible
        if (typeof tiposEventos === "undefined") {
            console.error("❌ tiposEventos no está definido. Verifica el orden de scripts en tu HTML.");
            return;
        }

        const precioBase = tipoEventoId ? (Number(tiposEventos[tipoEventoId]) || 0) : 0;
        totalEvento = horas * precioBase;

        // Mostrar fecha
        document.getElementById("resumen-fecha").textContent = fecha || "—";

        // Mostrar horas y precio
        const resumenHorasEl = document.getElementById("resumen-horas");
        if (!tipoEventoId) {
            resumenHorasEl.textContent = "—";
        } else if (horas > 0) {
            resumenHorasEl.textContent = `${horas.toFixed(1)} × S/ ${precioBase.toFixed(2)}`;
        } else {
            resumenHorasEl.textContent = `S/ ${precioBase.toFixed(2)} por hora`;
        }

        actualizarTotalGeneral();
    }

    function actualizarTotalGeneral() {
        const totalGeneral = totalEvento + totalServicios;
        document.getElementById("resumen-total").textContent = `S/ ${totalGeneral.toFixed(2)}`;
    }

    // ==============================
    // 🔹 MODAL DE SERVICIOS
    // ==============================
    const modal = document.getElementById("modal-servicios");
    const openModalBtn = document.getElementById("btn-abrir-modal");
    const accordionContainer = modal?.querySelector(".accordion");
    const btnConfirmar = modal?.querySelector(".btn-confirmar");
    const btnCancelar = modal?.querySelector(".btn-cancelar");
    const btnCerrar = modal?.querySelector(".close-modal");

    function abrirModal() {
        modal.style.display = "flex";
        cargarServicios();
    }

    function cerrarModal() {
        modal.style.display = "none";
    }

    modal?.addEventListener("click", (e) => {
        if (e.target === modal) cerrarModal();
    });

    [btnCancelar, btnCerrar].forEach(btn => {
        btn?.addEventListener("click", cerrarModal);
    });

    // ==============================
    // 🔹 CARGAR SERVICIOS (desde Flask)
    // ==============================
    async function cargarServicios() {
        try {
            const res = await fetch("/Eventos/servicios");
            const data = await res.json();

            if (!data.success) throw new Error(data.error);
            renderizarAcordeon(data.data);
        } catch (err) {
            console.error("❌ Error cargando servicios:", err);
            accordionContainer.innerHTML = `<p style="color:red;text-align:center;">Error al cargar servicios</p>`;
        }
    }

    // ==============================
    // 🔹 RENDERIZAR ACORDEÓN
    // ==============================
    function renderizarAcordeon(servicios) {
        accordionContainer.innerHTML = "";

        // Agrupar por tipo
        const agrupado = {};
        servicios.forEach(s => {
            if (!agrupado[s.nombre_tipo]) agrupado[s.nombre_tipo] = [];
            agrupado[s.nombre_tipo].push(s);
        });

        Object.entries(agrupado).forEach(([tipo, lista]) => {
            const item = document.createElement("div");
            item.classList.add("accordion-item");
            item.innerHTML = `
                <button class="accordion-header">${tipo}</button>
                <div class="accordion-content">
                    <div class="cards-container">
                        ${lista.map(s => `
                            <div class="card-servicio">
                                <h4>${s.nombre_servicio}</h4>
                                <p class="precio">S/ ${parseFloat(s.precio).toFixed(2)}</p>
                                <label>
                                    <input type="checkbox"
                                           data-nombre="${s.nombre_servicio}"
                                           data-precio="${s.precio}">
                                    Seleccionar
                                </label>
                            </div>
                        `).join("")}
                    </div>
                </div>
            `;
            accordionContainer.appendChild(item);
        });

        inicializarAcordeon();
    }

    // ==============================
    // 🔹 FUNCIONALIDAD DEL ACORDEÓN
    // ==============================
    function inicializarAcordeon() {
        document.querySelectorAll(".accordion-header").forEach(header => {
            header.addEventListener("click", () => {
                const item = header.parentElement;
                const active = item.classList.contains("active");
                document.querySelectorAll(".accordion-item").forEach(i => i.classList.remove("active"));
                if (!active) item.classList.add("active");
            });
        });
    }

    // ==============================
    // 🔹 CONFIRMAR SERVICIOS
    // ==============================
    btnConfirmar?.addEventListener("click", () => {
        const serviciosSeleccionados = document.querySelectorAll(".card-servicio input[type='checkbox']:checked");
        const listaServicios = document.getElementById("lista-servicios-seleccionados");
        listaServicios.innerHTML = "";

        totalServicios = 0;

        if (serviciosSeleccionados.length === 0) {
            listaServicios.innerHTML = "<small>No se han agregado servicios</small>";
        } else {
            serviciosSeleccionados.forEach(chk => {
                const nombre = chk.dataset.nombre;
                const precio = parseFloat(chk.dataset.precio);
                totalServicios += precio;

                const item = document.createElement("div");
                item.classList.add("summary-row");
                item.innerHTML = `
    <div>${nombre}</div>
    <div>S/ ${precio.toFixed(2)}</div>
`;

                // Inserta al inicio de la lista
                listaServicios.prepend(item);

            });
        }

        actualizarTotalGeneral();
        cerrarModal();
    });

    // ==============================
    // 🔹 EVENTOS DE FORMULARIO
    // ==============================
    document.getElementById("evento-fecha")?.addEventListener("change", actualizarResumen);
    document.getElementById("evento-hora-entrada")?.addEventListener("change", actualizarResumen);
    document.getElementById("evento-hora-salida")?.addEventListener("change", actualizarResumen);
    document.querySelector('select[name="tipo_evento_id"]')?.addEventListener("change", actualizarResumen);

    openModalBtn?.addEventListener("click", (e) => {
        e.preventDefault();
        abrirModal();
    });

    // ==============================
    // 🔹 INICIALIZACIÓN FINAL
    // ==============================
    actualizarResumen();
});


