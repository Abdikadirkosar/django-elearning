/* ==========================================================================
   E-Learn Management System - Vanilla JavaScript Interactions
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Mobile Menu Navigation Toggle
  const navToggle = document.getElementById('navToggle');
  const navLinks = document.getElementById('navLinks');

  if (navToggle && navLinks) {
    navToggle.addEventListener('click', () => {
      navLinks.classList.toggle('active');
    });
  }

  // 2. Auto-Dismiss Alert Messages after 5 seconds
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    const closeBtn = alert.querySelector('.alert-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => {
        alert.style.display = 'none';
      });
    }

    setTimeout(() => {
      alert.style.opacity = '0';
      alert.style.transition = 'opacity 0.5s ease';
      setTimeout(() => {
        alert.remove();
      }, 500);
    }, 5000);
  });

  // 3. Instant Client-Side Course Search Filter (for /courses/ page)
  const clientSearchInput = document.getElementById('clientSearchInput');
  const courseCards = document.querySelectorAll('.course-card-item');

  if (clientSearchInput && courseCards.length > 0) {
    clientSearchInput.addEventListener('keyup', (e) => {
      const term = e.target.value.toLowerCase().strip ? e.target.value.toLowerCase().strip() : e.target.value.toLowerCase().trim();
      courseCards.forEach(card => {
        const title = card.getAttribute('data-title') || card.innerText.toLowerCase();
        const category = card.getAttribute('data-category') || '';

        if (title.includes(term) || category.includes(term)) {
          card.style.display = 'flex';
        } else {
          card.style.display = 'none';
        }
      });
    });
  }

  // 4. Dynamic Progress Bars
  document.querySelectorAll('.progress-bar-fill[data-progress]').forEach(bar => {
    bar.style.width = (bar.getAttribute('data-progress') || '0') + '%';
  });
});

