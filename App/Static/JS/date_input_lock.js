document.addEventListener('DOMContentLoaded', () => {
  const allowedKeys = new Set([
    'Tab',
    'ArrowLeft',
    'ArrowRight',
    'ArrowUp',
    'ArrowDown',
    'Home',
    'End',
    'Escape',
    'Enter'
  ]);

  document.querySelectorAll('.date_input').forEach(input => {
    input.addEventListener('keydown', event => {
      if (allowedKeys.has(event.key)) {
        return;
      }
      event.preventDefault();
    });

    input.addEventListener('paste', event => {
      event.preventDefault();
    });
  });
});

