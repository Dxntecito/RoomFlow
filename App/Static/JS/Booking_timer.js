(function () {
  const TIMER_DURATION_MS = 10 * 60 * 1000; // 10 minutos
  const STORAGE_KEY = 'bookingTimerExpiration';
  const storage = (() => {
    try {
      const testKey = '__booking_timer__';
      window.sessionStorage.setItem(testKey, '1');
      window.sessionStorage.removeItem(testKey);
      return window.sessionStorage;
    } catch (error) {
      return window.localStorage;
    }
  })();

  let intervalId = null;
  let redirectTimeoutId = null;
  let expirationTimestamp = null;

  const getContainer = () => document.getElementById('booking_timer_container'); // legacy container
  const getModal = () => document.getElementById('booking_timer_modal');

  const DISPLAY_IDS = [
    'booking_timer_display',
    'booking_timer_display_step2',
    'booking_timer_display_step3',
    'booking_timer_display_step4',
    'booking_timer_display_step5'
  ];

  function getTimerDisplays() {
    return DISPLAY_IDS
      .map(id => document.getElementById(id))
      .filter(Boolean);
  }

  function isStepVisible(step) {
    if (!step) return false;
    const style = window.getComputedStyle(step);
    return style && style.display !== 'none';
  }

  function getCurrentTimerContainer() {
    const step2 = document.getElementById('step2');
    const step3 = document.getElementById('step3');
    const step4 = document.getElementById('step4');
    const step5 = document.getElementById('step5');

    if (isStepVisible(step2)) {
      return document.getElementById('booking_timer_container_step2');
    }
    if (isStepVisible(step3)) {
      return document.getElementById('booking_timer_container_step3');
    }
    if (isStepVisible(step4)) {
      return document.getElementById('booking_timer_container_step4');
    }
    if (isStepVisible(step5)) {
      return document.getElementById('booking_timer_container_step5');
    }
    return getContainer();
  }

  function clearBookingState() {
    try {
      localStorage.removeItem('booking_pending_data');
    } catch (err) {
      console.warn('[BookingTimer] No se pudo limpiar localStorage', err);
    }

    try {
      storage.removeItem(STORAGE_KEY);
    } catch (err) {
      console.warn('[BookingTimer] No se pudo limpiar storage', err);
    }

    if (typeof window.selectedRooms !== 'undefined') {
      window.selectedRooms = [];
    }
    if (typeof window.selectedServices !== 'undefined') {
      window.selectedServices = [];
    }
    if (typeof window.clientData !== 'undefined') {
      window.clientData = {};
    }
  }

  function formatTime(ms) {
    const totalSeconds = Math.max(0, Math.floor(ms / 1000));
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  }

  function updateDisplay(remaining) {
    const displays = getTimerDisplays();
    if (!displays.length) return;

    const formatted = formatTime(remaining);
    displays.forEach(d => {
      d.textContent = formatted;
    });
  }

  function showModal() {
    const modal = getModal();
    if (modal) {
      modal.classList.add('visible');
    }
  }

  function hideModal() {
    const modal = getModal();
    if (modal) {
      modal.classList.remove('visible');
    }
  }

  function clearTimers() {
    if (intervalId) {
      clearInterval(intervalId);
      intervalId = null;
    }
    if (redirectTimeoutId) {
      clearTimeout(redirectTimeoutId);
      redirectTimeoutId = null;
    }
  }

  function stopTimer(success = false) {
    clearTimers();
    expirationTimestamp = null;

    try {
      storage.removeItem(STORAGE_KEY);
    } catch (error) {
      console.warn('[BookingTimer] No se pudo limpiar la expiración almacenada.', error);
    }

    // Ocultar todos los contenedores de temporizador
    const containers = [
      document.getElementById('booking_timer_container'),
      document.getElementById('booking_timer_container_step2'),
      document.getElementById('booking_timer_container_step3'),
      document.getElementById('booking_timer_container_step4'),
      document.getElementById('booking_timer_container_step5')
    ];
    
    containers.forEach(container => {
      if (container) {
        container.classList.add('booking-timer--hidden');
      }
    });

    if (success) {
      hideModal();
    }
  }

  function handleExpiration() {
    stopTimer(false);
    showModal();

    redirectTimeoutId = setTimeout(() => {
      hideModal();
      clearBookingState();
      const homeUrl = window.BOOKING_HOME_URL || '/';
      window.location.href = homeUrl;
    }, 2500);
  }

  function tick() {
    if (!expirationTimestamp) return;
    const remaining = expirationTimestamp - Date.now();
    if (remaining <= 0) {
      handleExpiration();
      return;
    }

    updateDisplay(remaining);
  }

  function startTimer(forceNew = false) {
    // Verificar que NO estamos en step1 antes de iniciar el temporizador
    const step1 = document.getElementById('step1');
    const isStep1Visible = isStepVisible(step1);
    
    if (isStep1Visible) {
      // No iniciar el temporizador si estamos en step1
      return;
    }
    
    const container = getCurrentTimerContainer();
    const displays = getTimerDisplays();

    if (!container || !displays.length) {
      return;
    }

    container.classList.remove('booking-timer--hidden');

    const storedExpiration = parseInt(storage.getItem(STORAGE_KEY), 10);
    const now = Date.now();

    if (!forceNew && !Number.isNaN(storedExpiration) && storedExpiration > now) {
      expirationTimestamp = storedExpiration;
    } else {
      expirationTimestamp = now + TIMER_DURATION_MS;
      try {
        storage.setItem(STORAGE_KEY, String(expirationTimestamp));
      } catch (error) {
        console.warn('[BookingTimer] No se pudo guardar la expiración.', error);
      }
    }

    tick();
    clearTimers();
    intervalId = setInterval(tick, 1000);
  }

  // Función para actualizar la visibilidad del temporizador según el paso actual
  function updateTimerVisibility() {
    const step1 = document.getElementById('step1');
    const step2 = document.getElementById('step2');
    const step3 = document.getElementById('step3');
    const step4 = document.getElementById('step4');
    const step5 = document.getElementById('step5');
    
    const isStep1Visible = isStepVisible(step1);
    const isStep2Visible = isStepVisible(step2);
    const isStep3Visible = isStepVisible(step3);
    const isStep4Visible = isStepVisible(step4);
    const isStep5Visible = isStepVisible(step5);
    
    // Verificar si hay sesión activa
    const hasSession = typeof window.bookingHasSession !== 'undefined' && window.bookingHasSession;
    
    // Si estamos en step1 o no hay sesión, no mostrar el temporizador
    if (isStep1Visible || !hasSession) {
      stopTimer(false);
      return;
    }
    
    // Si estamos en algún paso después del 1 y hay sesión, iniciar/mostrar el temporizador
    if (isStep2Visible || isStep3Visible || isStep4Visible || isStep5Visible) {
      startTimer();
    }
  }

  window.bookingTimer = window.bookingTimer || {};
  window.bookingTimer.stop = (success = false) => stopTimer(success);
  window.bookingTimer.getRemaining = () => {
    if (!expirationTimestamp) return 0;
    return Math.max(0, expirationTimestamp - Date.now());
  };
  window.bookingTimer.updateVisibility = updateTimerVisibility;

  // Solo iniciar el temporizador si NO estamos en step1
  document.addEventListener('DOMContentLoaded', () => {
    updateTimerVisibility();
    
    // Observar cambios en la visibilidad de los pasos
    const observer = new MutationObserver(() => {
      updateTimerVisibility();
    });
    
    // Observar cambios en los atributos style de los pasos
    const step1 = document.getElementById('step1');
    const step2 = document.getElementById('step2');
    const step3 = document.getElementById('step3');
    const step4 = document.getElementById('step4');
    const step5 = document.getElementById('step5');
    
    [step1, step2, step3, step4, step5].forEach(step => {
      if (step) {
        observer.observe(step, {
          attributes: true,
          attributeFilter: ['style']
        });
      }
    });
  });
})();


