/**
 * I-HEART: Intelligent Health Evaluation And Risk Tracking
 * Theme Management Module (Light / Dark Mode)
 * 
 * Features:
 * - I-HEART branding acts as the Light/Dark mode switcher
 * - Prevents page refresh, URL change, navigation, and state reset
 * - LocalStorage preference persistence ('iheart_theme')
 * - Default: 'dark' mode
 * - Fast zero-flash synchronization
 * - Accessible state management (aria-label, title, aria-pressed, keyboard triggers)
 * - Cross-tab synchronization via storage events
 */

(function () {
  'use strict';

  var THEME_KEY = 'iheart_theme';
  var DARK_THEME = 'dark';
  var LIGHT_THEME = 'light';

  /**
   * Retrieves the current stored theme or defaults to 'dark'
   */
  function getPreferredTheme() {
    try {
      var saved = localStorage.getItem(THEME_KEY);
      if (saved === LIGHT_THEME || saved === DARK_THEME) {
        return saved;
      }
    } catch (e) {
      console.warn('localStorage not accessible for theme persistence:', e);
    }
    return DARK_THEME;
  }

  /**
   * Applies the theme to the <html> document root and updates the brand switcher accessibility attributes
   */
  function applyTheme(theme) {
    var validTheme = theme === LIGHT_THEME ? LIGHT_THEME : DARK_THEME;
    document.documentElement.setAttribute('data-theme', validTheme);

    try {
      localStorage.setItem(THEME_KEY, validTheme);
    } catch (e) {
      // Ignore storage errors in restricted iframe/browser modes
    }

    updateBrandSwitcher(validTheme);
  }

  /**
   * Updates I-HEART brand element aria-labels and states for screen readers
   */
  function updateBrandSwitcher(currentTheme) {
    var brandLinks = document.querySelectorAll('.nav-brand, #brand-link');
    var isLight = currentTheme === LIGHT_THEME;
    var nextLabel = isLight ? 'Switch to dark mode' : 'Switch to light mode';

    brandLinks.forEach(function (el) {
      el.setAttribute('aria-label', nextLabel);
      el.setAttribute('title', nextLabel);
      el.setAttribute('aria-pressed', isLight ? 'true' : 'false');
      el.setAttribute('role', 'button');
      el.setAttribute('tabindex', '0');
    });
  }

  /**
   * Toggles between dark and light themes
   */
  function toggleTheme() {
    var current = document.documentElement.getAttribute('data-theme') || DARK_THEME;
    var next = current === DARK_THEME ? LIGHT_THEME : DARK_THEME;
    applyTheme(next);
  }

  /**
   * Click handler for the I-HEART brand switcher
   * CRITICAL: Completely prevents page navigation, refresh, URL change, or hash jump
   */
  function handleBrandClick(e) {
    if (e) {
      if (typeof e.preventDefault === 'function') {
        e.preventDefault();
      }
      if (typeof e.stopPropagation === 'function') {
        e.stopPropagation();
      }
    }
    toggleTheme();
  }

  /**
   * Keyboard handler for the I-HEART brand switcher (Space and Enter support)
   */
  function handleBrandKeydown(e) {
    if (!e) return;
    // Enter (13) and Space (32) activate button
    if (e.key === ' ' || e.key === 'Spacebar' || e.keyCode === 32) {
      if (typeof e.preventDefault === 'function') {
        e.preventDefault();
      }
      if (typeof e.stopPropagation === 'function') {
        e.stopPropagation();
      }
      toggleTheme();
    }
  }

  /**
   * Initializes theme and attaches event listeners to the I-HEART brand switcher
   */
  function initTheme() {
    var currentTheme = getPreferredTheme();
    applyTheme(currentTheme);

    var brandLinks = document.querySelectorAll('.nav-brand, #brand-link');
    brandLinks.forEach(function (el) {
      // Clean previous listeners to prevent duplicate triggers
      el.removeEventListener('click', handleBrandClick);
      el.removeEventListener('keydown', handleBrandKeydown);

      // Attach click and keydown listeners
      el.addEventListener('click', handleBrandClick);
      el.addEventListener('keydown', handleBrandKeydown);
    });

    // Synchronize across multiple browser tabs
    window.addEventListener('storage', function (e) {
      if (e.key === THEME_KEY && e.newValue) {
        applyTheme(e.newValue);
      }
    });
  }

  // Run on DOM ready, or immediately if already parsed
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTheme);
  } else {
    initTheme();
  }

  // Export globally for programmatic control if needed
  window.iheartTheme = {
    get: getPreferredTheme,
    set: applyTheme,
    toggle: toggleTheme
  };
})();
