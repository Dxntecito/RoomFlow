const switchval = document.getElementById("tipo_cliente_switch");
//LIMPIAR ERRORES CADA QUE CAMBIE EL SELECT DE TIPO DE CLIENTE
switchval.addEventListener("change",function(){
    limpiarErrores();
}
);
// Campos de registro del Cliente
document.addEventListener("DOMContentLoaded", function () {
  // 🧾 Campos de documento (solo números)
  const docInputs = ["num_doc_natural", "num_doc_juridico"];
  docInputs.forEach(id => {
    const input = document.getElementById(id);
    if (input) {
      input.addEventListener("input", function () {
        // Elimina cualquier carácter que no sea número
        this.value = this.value.replace(/\D/g, "");
      });
    }
  });

  // 🧍‍♂️ Campos de texto (solo letras y espacios)
  const textInputs = ["nombres", "ape_paterno", "ape_materno"];
  textInputs.forEach(id => {
    const input = document.getElementById(id);
    if (input) {
      input.addEventListener("input", function () {
        // Elimina números y caracteres especiales, deja solo letras y espacios
        this.value = this.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, "");
      });
    }
  });
});

function validarPersonaJuridica() {
  limpiarErrores();

  const rucVal = document.getElementById("num_doc_juridico").value.trim();
  const razonVal = document.getElementById("razon_social").value.trim();
  const direccionVal = document.getElementById("direccion_juridica").value.trim();
  const paisVal = document.getElementById("pais_select_j").value.trim();
  const telefonoVal = document.getElementById("telefono_juridico").value.trim();
  const tipoEmpresaVal = document.getElementById("tipo_empresa").value.trim();

  let valido = true;

  // Campos obligatorios
  if (!rucVal) {
    mostrarError("input-group", "Ingrese el RUC de la empresa.");
    valido = false;
  }
  if (!razonVal) {
    mostrarError("razon_social", "Ingrese la razón social.");
    valido = false;
  }
  if (!direccionVal) {
    mostrarError("direccion_juridica", "Ingrese la dirección fiscal.");
    valido = false;
  }
  if (!paisVal) {
    mostrarError("pais_select_j", "Seleccione un país.");
    valido = false;
  }
  if (!telefonoVal) {
    mostrarError("telefono_juridico", "Ingrese un número de teléfono.");
    valido = false;
  }else if (telefonoVal.length !== 9) {
    mostrarError("telefono_juridico", "El teléfono debe tener 9 dígitos.");
    valido = false;
  }
  if (!tipoEmpresaVal) {
    mostrarError("tipo_empresa", "Seleccione un tipo de empresa.");
    valido = false;
  }

  // Validación del RUC (11 dígitos numéricos)
  if (rucVal && !/^\d{11}$/.test(rucVal)) {
    mostrarError("num_doc_juridico", "RUC inválido. Debe tener 11 dígitos numéricos.");
    valido = false;
  }

  return valido;
}

function validarPersonaNatural() {
  limpiarErrores();

  const tipo_doc_n = document.getElementById("tipo_doc_natural")
    .selectedOptions[0]
    .getAttribute("data-nombre");
  const dniVal = document.getElementById("num_doc_natural").value.trim();
  const nombresVal = document.getElementById("nombres").value.trim();
  const apePatVal = document.getElementById("ape_paterno").value.trim();
  const apeMatVal = document.getElementById("ape_materno").value.trim();
  const paisVal = document.getElementById("pais_select").value.trim();
  const numeroVal = document.getElementById("telefono_natural").value.trim();
  let valido = true;

  // Campos obligatorios
  if (!tipo_doc_n) {
    mostrarError("tipo_doc_natural", "Seleccione un tipo de documento.");
    valido = false;
  }
  if (!dniVal) {
    mostrarError("input-group", "Ingrese su número de documento.");
    valido = false;
  }
  if (!nombresVal) {
    mostrarError("nombres", "Ingrese sus nombres.");
    valido = false;
  }
  if (!apePatVal) {
    mostrarError("ape_paterno", "Ingrese su apellido paterno.");
    valido = false;
  }
  if (!apeMatVal) {
    mostrarError("ape_materno", "Ingrese su apellido materno.");
    valido = false;
  }
  if (!paisVal) {
    mostrarError("pais_select", "Seleccione un país.");
    valido = false;
  }

  // ✅ Validación teléfono
  if (!numeroVal) {
    mostrarError("telefono_natural", "Ingrese su número de teléfono.");
    valido = false;
  } else if (numeroVal.length !== 9) {
    mostrarError("telefono_natural", "El teléfono debe tener 9 dígitos.");
    valido = false;
  }

  // Validaciones específicas (DNI o Pasaporte)
  const tipo_validacion = tipo_doc_n === "DNI" ? 1 : 2;

  if (tipo_validacion === 1 && dniVal) {
    if (!/^\d{8}$/.test(dniVal)) {
      mostrarError("num_doc_natural", "DNI inválido. Debe tener 8 dígitos numéricos.");
      valido = false;
    }
  } else if (tipo_validacion === 2 && dniVal) {
    if (!/^\d{9}$/.test(dniVal)) {
      mostrarError("num_doc_natural", "Pasaporte inválido. Debe tener 9 dígitos numéricos.");
      valido = false;
    }
  }

  return valido;
}

// Función para mostrar mensaje de error debajo del input
function mostrarError(idInput, mensaje) {
  // Elimina mensaje anterior si existe
  let existente = document.querySelector(`#${idInput} + .error-msg`);
  if (existente) existente.remove();

  // Crea el mensaje
  const error = document.createElement("span");
  error.classList.add("error-msg");
  error.textContent = mensaje;
  error.style.color = "red";
  error.style.fontSize = "13px";
  error.style.display = "block";
  error.style.marginTop = "px";

  // Lo inserta justo después del input
  const input = document.getElementById(idInput);
  if (input) input.insertAdjacentElement("afterend", error);
  // Añadir listener para que al escribir se elimine este mensaje
  input.addEventListener("input", function handler() {
    const sibling = this.nextElementSibling;
    if (sibling && sibling.classList.contains("error-msg")) {
      sibling.remove();
      // Quitar este listener, para que no quede colgando
      this.removeEventListener("input", handler);
    }
  });
}
// Función para limpiar errores anteriores
function limpiarErrores() {
  document.querySelectorAll(".error-msg").forEach(e => e.remove());
}
