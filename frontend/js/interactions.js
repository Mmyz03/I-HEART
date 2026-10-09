/**
 * I-HEART: Intelligent Health Evaluation And Risk Tracking
 * Smooth Page Navigation Transitions & Native Scroll Reveal System
 * 
 * Features:
 * - Smooth fade + vertical translate page-to-page navigation (Home <-> Assessment <-> Results)
 * - Hardware-accelerated native IntersectionObserver Scroll Reveal animations
 * - Micro-staggered card and section entrances
 * - Full accessibility guard with 'prefers-reduced-motion' support
 * - Browser back/forward cache (bfcache) restoration handling
 */

(function () {
  'use strict';

  let globalObserver = null;

  document.addEventListener('DOMContentLoaded', () => {
    initPageTransitions();
    initScrollReveal();
    initBackToTop();
  });

  /**
   * Smooth Page Navigation Transition System
   */
  function initPageTransitions() {
    const transitionLinks = document.querySelectorAll(
      'a[href$=".html"], a[href="index.html"], a[href="assessment.html"], a[href="results.html"], #btn-start-assessment, #btn-hero-start, #btn-back, #btn-return-home, #btn-new-assessment, #nav-start-btn, #nav-back-home-btn, #nav-new-assessment-btn'
    );

    let isNavigating = false;

    transitionLinks.forEach((link) => {
      // Avoid overriding brand switcher which toggles dark/light theme
      if (link.classList.contains('nav-brand') || link.id === 'brand-link') {
        return;
      }

      link.addEventListener('click', (e) => {
        // Respect external, target="_blank", or modifier clicks (Cmd/Ctrl/Shift/Middle click)
        if (
          e.metaKey ||
          e.ctrlKey ||
          e.shiftKey ||
          e.altKey ||
          e.button !== 0 ||
          link.target === '_blank' ||
          link.getAttribute('rel') === 'external'
        ) {
          return;
        }

        const href = link.getAttribute('href');
        if (!href || href.startsWith('#') || href.startsWith('javascript:') || href.startsWith('mailto:')) {
          return;
        }

        // Check user preference for reduced motion
        const prefersReducedMotion = window.matchMedia &&
          window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        if (prefersReducedMotion) {
          // Direct immediate navigation without animation delay
          return;
        }

        // Prevent duplicate multiple clicks
        if (isNavigating) {
          e.preventDefault();
          return;
        }

        e.preventDefault();
        isNavigating = true;

        // Provide immediate tactical button feedback
        link.classList.add('btn-navigating');

        // Trigger smooth clinical exit animation on main page
        document.body.classList.add('page-transition-exiting');

        // Smoothly navigate after exit transition completes (280ms)
        setTimeout(() => {
          window.location.href = href;
        }, 280);

        // Safety timeout fallback: ensure navigation happens if page events stall
        setTimeout(() => {
          if (isNavigating) {
            window.location.href = href;
          }
        }, 750);
      });
    });

    // Handle bfcache / browser back-forward history restoration
    window.addEventListener('pageshow', () => {
      document.body.classList.remove('page-transition-exiting');
      transitionLinks.forEach((b) => b.classList.remove('btn-navigating'));
      isNavigating = false;
    });
  }

  /**
   * Scroll Reveal Animation System (Native IntersectionObserver)
   */
  function initScrollReveal() {
    const revealElements = document.querySelectorAll('.reveal-on-scroll:not(.is-revealed)');
    if (!revealElements.length) return;

    const prefersReducedMotion = window.matchMedia &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefersReducedMotion || !('IntersectionObserver' in window)) {
      // Immediately reveal all elements without motion
      revealElements.forEach((el) => el.classList.add('is-revealed'));
      return;
    }

    if (!globalObserver) {
      const observerOptions = {
        root: null,
        rootMargin: '0px 0px -40px 0px',
        threshold: 0.08
      };

      globalObserver = new IntersectionObserver((entries, obs) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('is-revealed');
            obs.unobserve(entry.target); // Unobserve once revealed so it remains visible permanently
          }
        });
      }, observerOptions);
    }

    revealElements.forEach((el) => {
      const rect = el.getBoundingClientRect();
      // If element is already in active viewport on page initialization, reveal it
      if (rect.top < window.innerHeight && rect.bottom > 0 && rect.height > 0) {
        el.classList.add('is-revealed');
      } else {
        globalObserver.observe(el);
      }
    });
  }

  /**
   * Floating Back to Top System
   */
  function initBackToTop() {
    let btn = document.getElementById('btn-back-to-top');

    // Dynamically inject if not in HTML
    if (!btn) {
      btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'back-to-top-btn';
      btn.id = 'btn-back-to-top';
      btn.setAttribute('aria-label', 'Back to top');
      btn.setAttribute('title', 'Back to top');
      btn.innerHTML = `
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <line x1="12" y1="19" x2="12" y2="5"></line>
          <polyline points="5 12 12 5 19 12"></polyline>
        </svg>
      `;
      document.body.appendChild(btn);
    }

    const scrollThreshold = 280;
    let ticking = false;

    function checkScroll() {
      const scrollY = window.pageYOffset || document.documentElement.scrollTop || 0;
      if (scrollY > scrollThreshold) {
        btn.classList.add('is-visible');
      } else {
        btn.classList.remove('is-visible');
      }
      ticking = false;
    }

    window.addEventListener('scroll', () => {
      if (!ticking) {
        window.requestAnimationFrame(checkScroll);
        ticking = true;
      }
    }, { passive: true });

    // Initial check on load
    checkScroll();

    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const prefersReducedMotion = window.matchMedia &&
        window.matchMedia('(prefers-reduced-motion: reduce)').matches;

      window.scrollTo({
        top: 0,
        behavior: prefersReducedMotion ? 'auto' : 'smooth'
      });

      // Remove focus after click for clean UI
      btn.blur();
    });
  }

  // Expose to window for dynamic page triggers
  window.initScrollReveal = initScrollReveal;
  window.initPageTransitions = initPageTransitions;
  window.initBackToTop = initBackToTop;

})();
