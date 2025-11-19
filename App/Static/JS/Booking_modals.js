/**
 * Sistema de Modales Profesionales para Booking
 * Reemplaza alert() y confirm() nativos con modales personalizados
 */

// Crear contenedor de modales si no existe
if (!document.getElementById('booking-modals-container')) {
  const modalsContainer = document.createElement('div');
  modalsContainer.id = 'booking-modals-container';
  document.body.appendChild(modalsContainer);
}

/**
 * Muestra un modal de alerta (reemplazo de alert())
 * @param {string} message - Mensaje a mostrar
 * @param {string} type - Tipo: 'info', 'warning', 'error', 'success'
 * @param {string} title - Título opcional
 * @returns {Promise} - Se resuelve cuando se cierra el modal
 */
function showBookingAlert(message, type = 'info', title = null) {
  return new Promise((resolve) => {
    const overlay = document.createElement('div');
    overlay.className = 'booking-modal-overlay';
    
    const icons = {
      info: '<i class="fas fa-info-circle"></i>',
      warning: '<i class="fas fa-exclamation-triangle"></i>',
      error: '<i class="fas fa-times-circle"></i>',
      success: '<i class="fas fa-check-circle"></i>'
    };
    
    const titles = {
      info: title || 'Información',
      warning: title || 'Advertencia',
      error: title || 'Error',
      success: title || 'Éxito'
    };
    
    overlay.innerHTML = `
      <div class="booking-modal">
        <div class="booking-modal__header">
          <div class="booking-modal__icon booking-modal__icon--${type}">
            ${icons[type] || icons.info}
          </div>
          <h3 class="booking-modal__title">${titles[type]}</h3>
        </div>
        <div class="booking-modal__body">
          <p class="booking-modal__message">${message}</p>
        </div>
        <div class="booking-modal__footer">
          <button class="booking-modal__button booking-modal__button--primary" data-action="ok">
            Aceptar
          </button>
        </div>
      </div>
    `;
    
    document.getElementById('booking-modals-container').appendChild(overlay);
    
    // Mostrar con animación
    setTimeout(() => overlay.classList.add('show'), 10);
    
    // Cerrar al hacer clic en el botón
    const okButton = overlay.querySelector('[data-action="ok"]');
    const closeModal = () => {
      overlay.classList.remove('show');
      setTimeout(() => {
        overlay.remove();
        resolve();
      }, 300);
    };
    
    okButton.addEventListener('click', closeModal);
    
    // Cerrar al hacer clic fuera del modal
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) {
        closeModal();
      }
    });
    
    // Cerrar con ESC
    const handleEsc = (e) => {
      if (e.key === 'Escape') {
        closeModal();
        document.removeEventListener('keydown', handleEsc);
      }
    };
    document.addEventListener('keydown', handleEsc);
  });
}

/**
 * Muestra un modal de confirmación (reemplazo de confirm())
 * @param {string} message - Mensaje a mostrar
 * @param {string} title - Título opcional
 * @param {string} confirmText - Texto del botón de confirmación
 * @param {string} cancelText - Texto del botón de cancelación
 * @returns {Promise<boolean>} - true si se confirma, false si se cancela
 */
function showBookingConfirm(message, title = 'Confirmar', confirmText = 'Aceptar', cancelText = 'Cancelar') {
  return new Promise((resolve) => {
    const overlay = document.createElement('div');
    overlay.className = 'booking-modal-overlay';
    
    overlay.innerHTML = `
      <div class="booking-modal">
        <div class="booking-modal__header">
          <div class="booking-modal__icon booking-modal__icon--question">
            <i class="fas fa-question-circle"></i>
          </div>
          <h3 class="booking-modal__title">${title}</h3>
        </div>
        <div class="booking-modal__body">
          <p class="booking-modal__message">${message}</p>
        </div>
        <div class="booking-modal__footer">
          <button class="booking-modal__button booking-modal__button--secondary" data-action="cancel">
            ${cancelText}
          </button>
          <button class="booking-modal__button booking-modal__button--primary" data-action="confirm">
            ${confirmText}
          </button>
        </div>
      </div>
    `;
    
    document.getElementById('booking-modals-container').appendChild(overlay);
    
    // Mostrar con animación
    setTimeout(() => overlay.classList.add('show'), 10);
    
    // Función para cerrar
    const closeModal = (result) => {
      overlay.classList.remove('show');
      setTimeout(() => {
        overlay.remove();
        resolve(result);
      }, 300);
    };
    
    // Botones
    const confirmButton = overlay.querySelector('[data-action="confirm"]');
    const cancelButton = overlay.querySelector('[data-action="cancel"]');
    
    confirmButton.addEventListener('click', () => closeModal(true));
    cancelButton.addEventListener('click', () => closeModal(false));
    
    // Cerrar con ESC (cancela)
    const handleEsc = (e) => {
      if (e.key === 'Escape') {
        closeModal(false);
        document.removeEventListener('keydown', handleEsc);
      }
    };
    document.addEventListener('keydown', handleEsc);
    
    // No cerrar al hacer clic fuera (requiere decisión explícita)
  });
}

// Hacer funciones globales
window.showBookingAlert = showBookingAlert;
window.showBookingConfirm = showBookingConfirm;

