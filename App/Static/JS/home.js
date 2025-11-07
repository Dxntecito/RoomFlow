document.addEventListener('DOMContentLoaded', function() {
    // initBookingForm();
    initSmoothScroll();
    initAnimations();
});


// function initBookingForm() {
//     const bookingBtn = document.querySelector('.booking-btn');
//     const searchBtn = document.querySelector('.search-btn');
//     const dateInputs = document.querySelectorAll('.date-input input');
    
//     // Configurar fechas por defecto
//     const today = new Date();
//     const tomorrow = new Date(today);
//     tomorrow.setDate(tomorrow.getDate() + 1);
//     const dayAfter = new Date(tomorrow);
//     dayAfter.setDate(dayAfter.getDate() + 3);
    
//     dateInputs[0].value = tomorrow.toISOString().split('T')[0];
//     dateInputs[1].value = dayAfter.toISOString().split('T')[0];
    
    
//     // Event listener para el botón de reserva
//     if (bookingBtn) {
//         bookingBtn.addEventListener('click', function() {
//             RoomFlow.showNotification('Iniciando proceso de reserva...', 'info');
//             // Aquí podrías redirigir a la página de reservas
//             setTimeout(() => {
//                 // window.location.href = 'pages/reservas.html';
//                 console.log('Iniciando proceso de reserva');
//             }, 1000);
//         });
//     }
// }



// Scroll suave para enlaces internos
function initSmoothScroll() {
    const links = document.querySelectorAll('a[href^="#"]');
    
    links.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Animaciones al hacer scroll
function initAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observar elementos para animación
    const animatedElements = document.querySelectorAll('.service-item, .about-content, .welcome-content');
    
    animatedElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(element);
    });
}

// Funcionalidad de los iconos sociales
document.addEventListener('DOMContentLoaded', function() {
    const socialIcons = document.querySelectorAll('.social-icon');
    
    socialIcons.forEach(icon => {
        icon.addEventListener('click', function(e) {
            e.preventDefault();
            const platform = this.querySelector('i').className;
            
            let message = '';
            if (platform.includes('facebook')) {
                message = 'Redirigiendo a Facebook...';
            } else if (platform.includes('twitter')) {
                message = 'Redirigiendo a Twitter...';
            } else if (platform.includes('instagram')) {
                message = 'Redirigiendo a Instagram...';
            } else if (platform.includes('linkedin')) {
                message = 'Redirigiendo a LinkedIn...';
            }
            
            RoomFlow.showNotification(message, 'info');
        });
    });
});

// Funcionalidad del menú móvil y toggle de iconos
document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.querySelector('.menu-toggle');
    const userToggle = document.querySelector('.user-toggle');
    const nav = document.querySelector('.nav');
    
    // Toggle entre menú y usuario
    if (menuToggle && userToggle) {
        menuToggle.addEventListener('click', function() {
            menuToggle.classList.add('active');
            userToggle.classList.remove('active');
        });
        
        userToggle.addEventListener('click', function() {
            userToggle.classList.add('active');
            menuToggle.classList.remove('active');
        });
    }
    
    // Menú móvil
    if (menuToggle && nav) {
        menuToggle.addEventListener('click', function() {
            nav.classList.toggle('active');
        });
    }
});

// Validación de fechas en tiempo real
document.addEventListener('DOMContentLoaded', function() {
    const dateInputs = document.querySelectorAll('.date-input input');
    
    dateInputs.forEach((input, index) => {
        input.addEventListener('change', function() {
            const checkIn = new Date(dateInputs[0].value);
            const checkOut = new Date(dateInputs[1].value);
            
            if (index === 0 && checkOut && checkIn >= checkOut) {
                // Si cambiamos la fecha de entrada y es mayor o igual a la de salida
                const newCheckOut = new Date(checkIn);
                newCheckOut.setDate(newCheckOut.getDate() + 1);
                dateInputs[1].value = newCheckOut.toISOString().split('T')[0];
            }
        });
    });
});
