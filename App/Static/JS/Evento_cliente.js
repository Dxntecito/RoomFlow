document.addEventListener("DOMContentLoaded", () => {
        const toggle = document.getElementById('toggleCliente');
        const formNatural = document.getElementById('formNatural');
        const formJuridico = document.getElementById('formJuridico');
        const tipoTexto = document.getElementById('tipoTexto');
        const tipoClienteInput = document.getElementById('tipo_cliente');

        // 🔹 Función para activar o desactivar los campos de un formulario
        function setDisabled(form, disabled) {
            form.querySelectorAll("input, select").forEach(el => el.disabled = disabled);
        }

        // 🔹 Evento del switch
        toggle.addEventListener("change", () => {
            if (toggle.checked) {
                // ✅ Modo Jurídico
                tipoTexto.textContent = "Jurídico";
                tipoClienteInput.value = "J";
                formJuridico.classList.remove("hidden");
                formNatural.classList.add("hidden");
                setDisabled(formNatural, true);
                setDisabled(formJuridico, false);
            } else {
                // ✅ Modo Natural
                tipoTexto.textContent = "Natural";
                tipoClienteInput.value = "N";
                formNatural.classList.remove("hidden");
                formJuridico.classList.add("hidden");
                setDisabled(formJuridico, true);
                setDisabled(formNatural, false);
            }
        });

        // 🔹 Al cargar la página: desactivar el formulario jurídico por defecto
        setDisabled(formJuridico, true);
    });