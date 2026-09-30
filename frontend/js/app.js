/**
 * AI Health Risk Prediction System - Frontend Logic (Landing Page)
 * Features: Mobile menu toggle, smooth navigation, scrollspy, and backend API health monitor.
 */

document.addEventListener('DOMContentLoaded', () => {
  initMobileMenu();
  initSmoothScroll();
  initScrollSpy();
  initApiHealthCheck();
  initPageTransitions();
});

/**
 * Mobile Navigation Drawer Toggle
 */
function initMobileMenu() {
  const hamburgerBtn = document.getElementById('hamburger-btn');
  const mobileNav = document.getElementById('mobile-nav');

  if (!hamburgerBtn || !mobileNav) return;

  function toggleMenu(open) {
    const shouldOpen = open !== undefined ? open : !mobileNav.classList.contains('open');
    if (shouldOpen) {
      mobileNav.classList.add('open');
      hamburgerBtn.classList.add('open');
      hamburgerBtn.setAttribute('aria-expanded', 'true');
      mobileNav.setAttribute('aria-hidden', 'false');
    } else {
      mobileNav.classList.remove('open');
      hamburgerBtn.classList.remove('open');
      hamburgerBtn.setAttribute('aria-expanded', 'false');
      mobileNav.setAttribute('aria-hidden', 'true');
    }
  }

  hamburgerBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    toggleMenu();
  });

  // Close when clicking mobile links
  const mobileLinks = mobileNav.querySelectorAll('.mobile-nav-link');
  mobileLinks.forEach((link) => {
    link.addEventListener('click', () => {
      toggleMenu(false);
    });
  });

  // Close when clicking outside
  document.addEventListener('click', (e) => {
    if (mobileNav.classList.contains('open') && !mobileNav.contains(e.target) && !hamburgerBtn.contains(e.target)) {
      toggleMenu(false);
    }
  });

  // Close on Escape key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && mobileNav.classList.contains('open')) {
      toggleMenu(false);
    }
  });
}

/**
 * Smooth Scroll handling for internal links
 */
function initSmoothScroll() {
  const internalLinks = document.querySelectorAll('a[href^="#"]');

  internalLinks.forEach((link) => {
    link.addEventListener('click', function (e) {
      const targetId = this.getAttribute('href');
      if (!targetId || targetId === '#') return;

      const targetElement = document.querySelector(targetId);
      if (targetElement) {
        e.preventDefault();
        targetElement.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });

        // Update URL hash cleanly without jumping
        if (history.pushState) {
          history.pushState(null, null, targetId);
        } else {
          location.hash = targetId;
        }
      }
    });
  });
}

/**
 * ScrollSpy: Update active state in desktop navigation as user scrolls
 */
function initScrollSpy() {
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-menu .nav-link');

  if (!sections.length || !navLinks.length) return;

  const observerOptions = {
    root: null,
    rootMargin: '-20% 0px -70% 0px',
    threshold: 0
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const id = entry.target.getAttribute('id');
        navLinks.forEach((link) => {
          const href = link.getAttribute('href');
          if (href === `#${id}`) {
            link.classList.add('active');
          } else {
            link.classList.remove('active');
          }
        });
      }
    });
  }, observerOptions);

  sections.forEach((section) => observer.observe(section));
}

/**
 * Backend API Health Check (Port 8001)
 */
const API_BASE_URL = (typeof window !== 'undefined' && window.location.origin && window.location.origin.startsWith('http'))
  ? window.location.origin
  : 'http://127.0.0.1:8001';

async function initApiHealthCheck() {
  const dot = document.getElementById('backend-status-dot');
  const text = document.getElementById('backend-status-text');
  const badge = document.getElementById('backend-status-badge');

  if (!dot || !text || !badge) return;

  try {
    const response = await fetch(`${API_BASE_URL}/api/health`);
    if (!response.ok) {
      throw new Error(`HTTP status ${response.status}`);
    }
    const data = await response.json();

    if (data.status === 'ok') {
      dot.className = 'status-indicator-dot active';
      text.textContent = 'FastAPI Backend Operational (Port 8001)';
      badge.textContent = 'API: ONLINE (200)';
    } else {
      dot.className = 'status-indicator-dot';
      text.textContent = 'Backend returned unexpected response';
      badge.textContent = `API: ${data.status || 'UNKNOWN'}`;
    }
  } catch (error) {
    dot.className = 'status-indicator-dot error';
    text.textContent = `Backend offline (${API_BASE_URL})`;
    badge.textContent = 'API: OFFLINE';
    console.info('Backend check status info:', error.message);
  }
}

/**
 * Smooth Page Navigation Transition (Landing -> Assessment)
 */
function initPageTransitions() {
  const startButtons = document.querySelectorAll(
    '#btn-start-assessment, #nav-start-btn, #mob-nav-assessment, a[href="assessment.html"]'
  );

  let isNavigating = false;

  startButtons.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      // Respect external or modified clicks (new tab / window)
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) {
        return;
      }

      const targetUrl = btn.getAttribute('href') || 'assessment.html';

      // Prevent duplicate multiple clicks
      if (isNavigating) {
        e.preventDefault();
        return;
      }

      // Check user preference for reduced motion
      const prefersReducedMotion = window.matchMedia &&
        window.matchMedia('(prefers-reduced-motion: reduce)').matches;

      if (prefersReducedMotion) {
        // Direct immediate navigation without animation delays
        return;
      }

      e.preventDefault();
      isNavigating = true;

      // Provide immediate tactical button feedback
      btn.classList.add('btn-navigating');

      // Trigger smooth clinical exit animation on main page
      document.body.classList.add('page-transition-exiting');

      // Smoothly navigate after the exit transition completes (350ms)
      setTimeout(() => {
        window.location.href = targetUrl;
      }, 350);
    });
  });

  // Handle bfcache / browser back-forward history restoration
  window.addEventListener('pageshow', () => {
    document.body.classList.remove('page-transition-exiting');
    startButtons.forEach((b) => b.classList.remove('btn-navigating'));
    isNavigating = false;
  });
}

