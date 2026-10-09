/**
 * AI Health Risk Prediction System - Frontend Logic (Landing Page)
 * Features: Mobile menu toggle, smooth navigation, scrollspy, and backend API health monitor.
 */

document.addEventListener('DOMContentLoaded', () => {
  initMobileMenu();
  initNavigationIndicator();
  initApiHealthCheck();
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
 * Smooth Animated Active Navigation Indicator & Explicit Ordered Section ScrollSpy
 * Navigation sequence:
 * 01 Home (#home) -> 02 Overview (#overview) -> 03 Capabilities (#features)
 * -> 04 Architecture (#how-it-works) -> 05 Clinical Scope (#about) -> 06 Telemetry (#development-status)
 */
function initNavigationIndicator() {
  const navList = document.querySelector('.nav-list');
  const navLinks = document.querySelectorAll('.nav-menu .nav-link:not(.nav-btn-status)');
  if (!navList || !navLinks.length) return;

  // Exact ordered mapping of sections to nav links
  const ORDERED_SECTIONS = [
    { id: 'home', navId: 'nav-home', mobId: 'mob-nav-home' },
    { id: 'overview', navId: 'nav-overview', mobId: 'mob-nav-overview' },
    { id: 'features', navId: 'nav-features', mobId: 'mob-nav-features' },
    { id: 'how-it-works', navId: 'nav-how-it-works', mobId: 'mob-nav-how-it-works' },
    { id: 'about', navId: 'nav-about', mobId: 'mob-nav-about' },
    { id: 'development-status', navId: 'nav-status', mobId: 'mob-nav-status' }
  ];

  // Locate or create the shared sliding active indicator line
  let indicator = document.getElementById('nav-indicator-slider');
  if (!indicator) {
    indicator = document.createElement('li');
    indicator.className = 'nav-indicator-slider';
    indicator.id = 'nav-indicator-slider';
    indicator.setAttribute('aria-hidden', 'true');
    navList.appendChild(indicator);
  }

  let currentActiveId = 'home';
  let isProgrammaticScroll = false;
  let targetSectionId = null;
  let scrollRafId = null;
  let scrollSafetyTimer = null;

  function getPrefersReducedMotion() {
    return window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }

  function updateIndicator(activeLink, animate = true) {
    if (!activeLink || !navList.contains(activeLink)) {
      indicator.style.opacity = '0';
      return;
    }

    const listRect = navList.getBoundingClientRect();
    const linkRect = activeLink.getBoundingClientRect();

    // Calculate left offset and exact width relative to navList
    const leftOffset = linkRect.left - listRect.left;
    const width = linkRect.width;

    if (!animate || getPrefersReducedMotion()) {
      indicator.style.transition = 'none';
    } else {
      indicator.style.transition = 'transform 300ms cubic-bezier(0.16, 1, 0.3, 1), width 300ms cubic-bezier(0.16, 1, 0.3, 1), opacity 200ms ease';
    }

    indicator.style.transform = `translateX(${leftOffset}px)`;
    indicator.style.width = `${width}px`;
    indicator.style.opacity = '1';
    indicator.classList.add('is-visible');
  }

  function setActiveSection(sectionId, animate = true) {
    if (!sectionId) return;
    const match = ORDERED_SECTIONS.find((item) => item.id === sectionId);
    if (!match) return;

    currentActiveId = sectionId;

    // Update desktop links
    navLinks.forEach((link) => {
      if (link.id === match.navId || link.getAttribute('href') === `#${sectionId}`) {
        link.classList.add('active');
        updateIndicator(link, animate);
      } else {
        link.classList.remove('active');
      }
    });

    // Update mobile links
    const mobileLinks = document.querySelectorAll('.mobile-nav-link');
    mobileLinks.forEach((mobLink) => {
      if (mobLink.id === match.mobId || mobLink.getAttribute('href') === `#${sectionId}`) {
        mobLink.classList.add('active');
      } else {
        mobLink.classList.remove('active');
      }
    });
  }

  // Set initial position on Home
  setActiveSection('home', false);
  requestAnimationFrame(() => {
    const homeLink = document.getElementById('nav-home') || navLinks[0];
    if (homeLink) updateIndicator(homeLink, false);
  });

  // Calculate active section based on deterministic manual scroll position
  function computeActiveSection() {
    const scrollY = window.pageYOffset || document.documentElement.scrollTop || 0;
    const header = document.getElementById('main-header');
    const headerHeight = header ? header.offsetHeight : 64;
    const triggerOffset = headerHeight + 100;

    // 1. Top Edge Case: At or near page top, Home is strictly active
    if (scrollY < 120) {
      return 'home';
    }

    // 2. Bottom Edge Case: Near the very bottom of the page, Telemetry is active
    const maxScroll = Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
    if (scrollY >= maxScroll - 60) {
      return 'development-status';
    }

    // 3. Scan sections in exact order from top to bottom
    let activeId = 'home';
    for (let i = 0; i < ORDERED_SECTIONS.length; i++) {
      const sectionElem = document.getElementById(ORDERED_SECTIONS[i].id);
      if (sectionElem) {
        const top = sectionElem.getBoundingClientRect().top;
        if (top <= triggerOffset) {
          activeId = ORDERED_SECTIONS[i].id;
        }
      }
    }

    return activeId;
  }

  // Manual scroll event handler throttled with requestAnimationFrame
  let isTicking = false;
  function handleScroll() {
    // CRITICAL: When programmatic click navigation is running, scroll-spy is completely locked!
    if (isProgrammaticScroll) return;

    const activeId = computeActiveSection();
    if (activeId !== currentActiveId) {
      setActiveSection(activeId, true);
    }
    isTicking = false;
  }

  window.addEventListener('scroll', () => {
    if (!isTicking && !isProgrammaticScroll) {
      window.requestAnimationFrame(handleScroll);
      isTicking = true;
    }
  }, { passive: true });

  /**
   * Performs ONE direct, smooth, uninterrupted scroll to the target section
   */
  function smoothScrollToSection(sectionId) {
    if (!sectionId) return;
    const targetElement = document.getElementById(sectionId);
    if (!targetElement) return;

    const header = document.getElementById('main-header');
    const headerHeight = header ? header.offsetHeight : 64;
    const maxScroll = Math.max(0, document.documentElement.scrollHeight - window.innerHeight);

    let targetY = 0;
    if (sectionId === 'home') {
      targetY = 0;
    } else {
      const rect = targetElement.getBoundingClientRect();
      targetY = Math.min(Math.max(0, window.pageYOffset + rect.top - (headerHeight - 2)), maxScroll);
    }

    const currentY = window.pageYOffset || document.documentElement.scrollTop || 0;

    // If clicking the current section and already in place, do nothing
    if (Math.abs(currentY - targetY) < 5 && currentActiveId === sectionId) {
      setActiveSection(sectionId, false);
      return;
    }

    // Lock scroll-spy strictly for the duration of this navigation
    isProgrammaticScroll = true;
    targetSectionId = sectionId;
    if (scrollRafId) cancelAnimationFrame(scrollRafId);
    if (scrollSafetyTimer) clearTimeout(scrollSafetyTimer);

    // 1. Instantly move the active indicator to the destination item in ONE direct animation
    setActiveSection(sectionId, true);

    const reduced = getPrefersReducedMotion();

    if (reduced) {
      window.scrollTo({ top: targetY, behavior: 'auto' });
      isProgrammaticScroll = false;
      targetSectionId = null;
      if (history.pushState) history.pushState(null, null, `#${sectionId}`);
      return;
    }

    // 2. Perform ONE direct smooth scroll
    window.scrollTo({
      top: targetY,
      behavior: 'smooth'
    });

    if (history.pushState) {
      history.pushState(null, null, `#${sectionId}`);
    }

    // 3. Monitor arrival using RAF convergence + native scrollend
    let lastY = currentY;
    let samePosFrames = 0;
    const startTime = performance.now();

    function checkArrival() {
      if (!isProgrammaticScroll || targetSectionId !== sectionId) return;

      const nowY = window.pageYOffset || document.documentElement.scrollTop || 0;
      const dist = Math.abs(nowY - targetY);

      if (Math.abs(nowY - lastY) < 1.5) {
        samePosFrames++;
      } else {
        samePosFrames = 0;
      }
      lastY = nowY;

      // Completed when within 4px of target, or settled for 6 consecutive frames, or 1.8s timeout
      if (dist <= 4 || samePosFrames >= 6 || (performance.now() - startTime > 1800)) {
        isProgrammaticScroll = false;
        targetSectionId = null;
        setActiveSection(sectionId, false);
      } else {
        scrollRafId = requestAnimationFrame(checkArrival);
      }
    }

    // Native scrollend listener
    const onScrollEnd = () => {
      if (isProgrammaticScroll && targetSectionId === sectionId) {
        isProgrammaticScroll = false;
        targetSectionId = null;
        if (scrollRafId) cancelAnimationFrame(scrollRafId);
        setActiveSection(sectionId, false);
      }
      window.removeEventListener('scrollend', onScrollEnd);
    };
    window.addEventListener('scrollend', onScrollEnd, { once: true });

    // Start convergence checking after 60ms
    setTimeout(() => {
      if (isProgrammaticScroll && targetSectionId === sectionId) {
        scrollRafId = requestAnimationFrame(checkArrival);
      }
    }, 60);

    // Hard fallback safety timer (2s max)
    scrollSafetyTimer = setTimeout(() => {
      if (isProgrammaticScroll && targetSectionId === sectionId) {
        isProgrammaticScroll = false;
        targetSectionId = null;
        if (scrollRafId) cancelAnimationFrame(scrollRafId);
        setActiveSection(sectionId, false);
      }
    }, 2000);
  }

  // Smooth click navigation for desktop nav links
  navLinks.forEach((link) => {
    link.addEventListener('click', function (e) {
      const targetId = this.getAttribute('href');
      if (!targetId || !targetId.startsWith('#')) return;
      e.preventDefault();
      const sectionId = targetId.substring(1);
      smoothScrollToSection(sectionId);
    });
  });

  // Smooth click navigation for mobile drawer and other page anchor links (e.g. Hero buttons)
  const otherInternalLinks = document.querySelectorAll('a[href^="#"]:not(.nav-menu .nav-link)');
  otherInternalLinks.forEach((link) => {
    link.addEventListener('click', function (e) {
      if (this.id === 'brand-link' || this.classList.contains('nav-brand')) return;
      const targetId = this.getAttribute('href');
      if (!targetId || !targetId.startsWith('#')) return;
      e.preventDefault();
      const sectionId = targetId.substring(1);
      smoothScrollToSection(sectionId);
    });
  });

  // Significant wheel/drag interruption unlock
  window.addEventListener('wheel', (e) => {
    if (isProgrammaticScroll && Math.abs(e.deltaY) > 30) {
      isProgrammaticScroll = false;
      targetSectionId = null;
      if (scrollRafId) cancelAnimationFrame(scrollRafId);
      if (scrollSafetyTimer) clearTimeout(scrollSafetyTimer);
    }
  }, { passive: true });

  window.addEventListener('touchmove', () => {
    if (isProgrammaticScroll) {
      isProgrammaticScroll = false;
      targetSectionId = null;
      if (scrollRafId) cancelAnimationFrame(scrollRafId);
      if (scrollSafetyTimer) clearTimeout(scrollSafetyTimer);
    }
  }, { passive: true });

  // Handle window resize and font load readjustments
  window.addEventListener('resize', () => {
    const active = document.querySelector('.nav-menu .nav-link.active:not(.nav-btn-status)');
    if (active) {
      updateIndicator(active, false);
    }
  }, { passive: true });

  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(() => {
      const active = document.querySelector('.nav-menu .nav-link.active:not(.nav-btn-status)');
      if (active) {
        updateIndicator(active, false);
      }
    });
  }
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

      // Smoothly navigate after the exit transition completes (220ms)
      setTimeout(() => {
        window.location.href = targetUrl;
      }, 220);
    });
  });

  // Handle bfcache / browser back-forward history restoration
  window.addEventListener('pageshow', () => {
    document.body.classList.remove('page-transition-exiting');
    startButtons.forEach((b) => b.classList.remove('btn-navigating'));
    isNavigating = false;
  });
}

