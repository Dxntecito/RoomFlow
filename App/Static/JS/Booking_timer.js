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

  const getContainer = () => document.getElementById('booking_timer_container');
  const getDisplay = () => document.getElementById('booking_timer_display');
  const getModal = () => document.getElementById('booking_timer_modal');

  function formatTime(ms) {
    const totalSeconds = Math.max(0, Math.floor(ms / 1000));
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  }

  function updateDisplay(remaining) {
    const display = getDisplay();
    if (!display) return;
    display.textContent = formatTime(remaining);
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

    const container = getContainer();
    if (container) {
      container.classList.add('booking-timer--hidden');
    }

    if (success) {
      hideModal();
    }
  }

  function handleExpiration() {
    stopTimer(false);
    showModal();

    redirectTimeoutId = setTimeout(() => {
      hideModal();
      startTimer(true);
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
    const container = getContainer();
    const display = getDisplay();

    if (!container || !display) {
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

  window.bookingTimer = window.bookingTimer || {};
  window.bookingTimer.stop = (success = false) => stopTimer(success);
  window.bookingTimer.getRemaining = () => {
    if (!expirationTimestamp) return 0;
    return Math.max(0, expirationTimestamp - Date.now());
  };

  document.addEventListener('DOMContentLoaded', startTimer);
})();


