document.addEventListener('DOMContentLoaded', () => {
    const radios = document.querySelectorAll('input[name="metodo_pago_id"]');
    const tarjetaFields = document.getElementById('tarjeta-fields');
    const efectivoFields = document.getElementById('efectivo-fields');
    const monederoFields = document.getElementById('monedero-fields');

    function mostrarCampos(nombreMetodo) {
        [tarjetaFields, efectivoFields, monederoFields].forEach(div => div.classList.add('hidden'));

        if (nombreMetodo === 'tarjeta') tarjetaFields.classList.remove('hidden');
        else if (nombreMetodo === 'efectivo') efectivoFields.classList.remove('hidden');
        else if (nombreMetodo === 'yape' || nombreMetodo === 'monedero virtual') monederoFields.classList.remove('hidden');
    }

    radios.forEach(radio => {
        radio.addEventListener('change', () => mostrarCampos(radio.dataset.nombre));
    });

    const checked = document.querySelector('input[name="metodo_pago_id"]:checked');
    if (checked) mostrarCampos(checked.dataset.nombre);
});
