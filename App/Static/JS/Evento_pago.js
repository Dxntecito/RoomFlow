


document.addEventListener("DOMContentLoaded", () => {
        const btnPagar = document.getElementById("btn-pagar");
        const form = document.getElementById("form-pago");
        const modal = document.getElementById("modal-pago");
        const anim = document.getElementById("animacion-pago");
        const texto = document.getElementById("texto-pago");

        // ================================
        // 🔹 FUNCIONES DE VALIDACIÓN
        // ================================
        function validarEvento() {
            const campos = ["evento-fecha", "evento-hora-entrada", "evento-hora-salida"];
            for (const id of campos) {
                const campo = document.getElementById(id);
                if (!campo.value) return false;
            }

            const tipoEvento = form.querySelector('[name="tipo_evento_id"]').value;
            const nombreEvento = form.querySelector('[name="nombre_evento"]').value.trim();
            return tipoEvento && nombreEvento;
        }

        function validarCliente() {
            const tipo = document.getElementById("tipo_cliente").value;
            const formNatural = document.getElementById("formNatural");
            const formJuridico = document.getElementById("formJuridico");

            // Campos según tipo
            const camposN = ["ape_paterno", "ape_materno", "nombres", "pais_id", "telefono", "tipo_doc_id", "nro_doc"];
            const camposJ = ["ruc", "razon_social", "telefono", "pais_id", "direccion"];
            const campos = tipo === "N" ? camposN : camposJ;

            // Escoger formulario activo
            const formActivo = tipo === "N" ? formNatural : formJuridico;

            for (const name of campos) {
                const input = formActivo.querySelector(`[name="${name}"]`);
                if (!input || input.disabled) continue; // ignora los deshabilitados
                if (!input.value.trim()) return false;
                const pattern = input.getAttribute("pattern");
                if (pattern && !new RegExp(pattern).test(input.value.trim())) return false;
            }
            return true;
        }


        function validarPago() {
            const metodo = form.querySelector('input[name="metodo_pago_id"]:checked');
            if (!metodo) return false;

            const metodoNombre = metodo.dataset.nombre.toLowerCase();
            if (metodoNombre.includes("tarjeta")) {
                const num = form.querySelector('[name="num_tarjeta"]').value.trim();
                const cvv = form.querySelector('[name="codigo_seguridad"]').value.trim();
                return num && cvv;
            } else if (metodoNombre.includes("efectivo")) {
                const monto = form.querySelector('[name="monto_efectivo"]').value.trim();
                return monto;
            } else if (metodoNombre.includes("monedero")) {
                const tel = form.querySelector('[name="telefono_monedero"]').value.trim();
                const clave = form.querySelector('[name="clave_monedero"]').value.trim();
                return tel && clave;
            }
            return true;
        }

        // ================================
        // 🔹 ACTUALIZAR ESTADO DEL BOTÓN
        // ================================
        function actualizarEstadoBoton() {
            const todoValido = validarEvento() && validarCliente() && validarPago();
            btnPagar.disabled = !todoValido;
        }

        // Monitoreamos cambios en todos los inputs y selects
        form.querySelectorAll("input, select").forEach(el => {
            el.addEventListener("input", actualizarEstadoBoton);
            el.addEventListener("change", actualizarEstadoBoton);
        });

        // ================================
        // 🔹 AL HACER CLICK EN PAGAR
        // ================================
        btnPagar.addEventListener("click", async (e) => {
            e.preventDefault();

            if (btnPagar.disabled) return; // seguridad adicional

            modal.style.display = "flex";
            anim.className = "animacion-pago";
            texto.textContent = "Procesando pago...";

            const formData = new FormData(form);
            formData.append("numero_horas", horas);
            formData.append("precio_final", total);

            try {
                const response = await fetch("/Eventos/procesar_pago", {
                    method: "POST",
                    body: formData
                });
                const data = await response.json();

                if (data.success) {
                    anim.className = "check-success";
                    texto.textContent = "¡Pago exitoso!";
                    setTimeout(() => window.location.href = data.redirect_url, 1500);
                } else {
                    showFlash(data.message || "Error al procesar el pago.");
                    anim.className = "check-error";
                    texto.textContent = "Error al procesar el pago.";
                    setTimeout(() => modal.style.display = "none", 2000);
                }
            } catch (err) {
                console.error(err);
                showFlash("Error de conexión. Intenta nuevamente.");
                anim.className = "check-error";
                texto.textContent = "Error de conexión.";
                setTimeout(() => modal.style.display = "none", 2000);
            }
        });

        // Inicializar botón
        actualizarEstadoBoton();
    });