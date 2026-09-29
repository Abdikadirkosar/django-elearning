/* ==========================================================================
   AQOONPLUS - Main JavaScript
   Developer: Dev. Abdikadir
   ========================================================================== */

'use strict';

(function initMobileNav() {
  const toggle = document.getElementById('navToggle');
  const menu   = document.getElementById('mobileMenu');
  if (!toggle || !menu) return;

  toggle.addEventListener('click', () => {
    const isOpen = menu.classList.toggle('active');
    toggle.setAttribute('aria-expanded', isOpen.toString());
    document.body.style.overflow = isOpen ? 'hidden' : '';
  });

  // Close when a link inside the menu is clicked
  menu.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      menu.classList.remove('active');
      toggle.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    });
  });

  // Close on outside click
  document.addEventListener('click', (e) => {
    if (!menu.contains(e.target) && !toggle.contains(e.target)) {
      menu.classList.remove('active');
      toggle.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
    }
  });

  // Close on Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && menu.classList.contains('active')) {
      menu.classList.remove('active');
      toggle.setAttribute('aria-expanded', 'false');
      document.body.style.overflow = '';
      toggle.focus();
    }
  });
})();

(function initAlerts() {
  document.querySelectorAll('.alert-close').forEach(btn => {
    btn.addEventListener('click', () => {
      const alert = btn.closest('.alert');
      if (alert) {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-8px)';
        alert.style.transition = 'all 0.3s ease';
        setTimeout(() => alert.remove(), 300);
      }
    });
  });
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      if (alert.parentNode) {
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-8px)';
        alert.style.transition = 'all 0.4s ease';
        setTimeout(() => alert.remove(), 400);
      }
    }, 5000);
  });
})();

(function initCourseFilter() {
  const searchInput = document.getElementById('courseSearch');
  const categorySelect = document.getElementById('categoryFilter');
  const courseCards = document.querySelectorAll('[data-course-card]');
  const noResultsEl = document.getElementById('noCoursesMsg');
  if (!searchInput && !categorySelect) return;
  function filterCourses() {
    const query = (searchInput ? searchInput.value.toLowerCase() : '');
    const category = (categorySelect ? categorySelect.value.toLowerCase() : '');
    let visible = 0;
    courseCards.forEach(card => {
      const title = (card.dataset.title || '').toLowerCase();
      const cat = (card.dataset.category || '').toLowerCase();
      const instructor = (card.dataset.instructor || '').toLowerCase();
      const matchesQuery = !query || title.includes(query) || instructor.includes(query) || cat.includes(query);
      const matchesCat = !category || cat === category;
      if (matchesQuery && matchesCat) { card.style.display = ''; visible++; }
      else { card.style.display = 'none'; }
    });
    if (noResultsEl) noResultsEl.style.display = visible === 0 ? '' : 'none';
  }
  if (searchInput) searchInput.addEventListener('input', filterCourses);
  if (categorySelect) categorySelect.addEventListener('change', filterCourses);
})();

(function initNavbarSearch() {
  const navSearchInput = document.getElementById('navSearchInput');
  if (!navSearchInput) return;
  navSearchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      const q = navSearchInput.value.trim();
      if (q) window.location.href = `/courses/?q=${encodeURIComponent(q)}`;
    }
  });
})();

(function initCategoryPills() {
  const pills = document.querySelectorAll('[data-category-pill]');
  const categorySelect = document.getElementById('categoryFilter');
  pills.forEach(pill => {
    pill.addEventListener('click', () => {
      pills.forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      if (categorySelect) {
        categorySelect.value = pill.dataset.categoryPill || '';
        categorySelect.dispatchEvent(new Event('change'));
      }
    });
  });
})();

(function initPasswordToggle() {
  document.querySelectorAll('[data-pw-toggle]').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.dataset.pwToggle;
      const input = document.getElementById(targetId);
      if (!input) return;
      const isText = input.type === 'text';
      input.type = isText ? 'password' : 'text';
      btn.textContent = isText ? '👁' : '🙈';
    });
  });
})();

(function markActiveLink() {
  const path = window.location.pathname;
  document.querySelectorAll('.navbar-links a, .mobile-links a').forEach(link => {
    const href = link.getAttribute('href');
    if (href === path) link.classList.add('active');
    else if (path.startsWith('/courses/') && href === '/courses/') link.classList.add('active');
    else if (path.startsWith('/dashboard/') && href === '/dashboard/') link.classList.add('active');
    else if (path.startsWith('/about/') && href === '/about/') link.classList.add('active');
    else if (path.startsWith('/contact/') && href === '/contact/') link.classList.add('active');
  });
})();

(function initCounterAnimation() {
  const counters = document.querySelectorAll('[data-count]');
  if (!counters.length) return;
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const target = parseInt(el.dataset.count, 10);
        const suffix = el.dataset.suffix || '';
        let current = 0;
        const increment = Math.ceil(target / 60);
        const timer = setInterval(() => {
          current += increment;
          if (current >= target) { current = target; clearInterval(timer); }
          el.textContent = current.toLocaleString() + suffix;
        }, 20);
        observer.unobserve(el);
      }
    });
  }, { threshold: 0.3 });
  counters.forEach(el => observer.observe(el));
})();
