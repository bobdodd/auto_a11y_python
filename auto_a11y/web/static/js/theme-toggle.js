/**
 * Theme toggle: cycles auto -> light -> dark -> auto.
 * Persists preference in localStorage under 'theme-preference'.
 * Announces changes via aria-live region.
 */
(function () {
    'use strict';

    var STORAGE_KEY = 'theme-preference';
    var STATES = ['auto', 'light', 'dark'];
    var LABELS = {
        auto: 'Color theme: automatic. Switch to light.',
        light: 'Color theme: light. Switch to dark.',
        dark: 'Color theme: dark. Switch to automatic.'
    };
    var ANNOUNCEMENTS = {
        auto: 'Color theme changed to automatic.',
        light: 'Color theme changed to light.',
        dark: 'Color theme changed to dark.'
    };

    function getPreference() {
        try {
            return localStorage.getItem(STORAGE_KEY) || 'auto';
        } catch (e) {
            return 'auto';
        }
    }

    function setPreference(pref) {
        try {
            localStorage.setItem(STORAGE_KEY, pref);
        } catch (e) {
            // localStorage unavailable — preference won't persist
        }
    }

    function applyTheme(pref) {
        if (pref === 'light' || pref === 'dark') {
            document.documentElement.setAttribute('data-theme', pref);
        } else {
            document.documentElement.removeAttribute('data-theme');
        }
    }

    function updateButton(btn, pref) {
        btn.setAttribute('aria-label', LABELS[pref]);
        // Update icon visibility
        var icons = btn.querySelectorAll('[data-theme-icon]');
        for (var i = 0; i < icons.length; i++) {
            icons[i].hidden = icons[i].getAttribute('data-theme-icon') !== pref;
        }
    }

    function announce(pref) {
        var region = document.getElementById('theme-announce');
        if (region) {
            region.textContent = ANNOUNCEMENTS[pref];
        }
    }

    function init() {
        var btn = document.getElementById('theme-toggle');
        if (!btn) return;

        var currentPref = getPreference();
        updateButton(btn, currentPref);

        btn.addEventListener('click', function () {
            var current = getPreference();
            var nextIndex = (STATES.indexOf(current) + 1) % STATES.length;
            var next = STATES[nextIndex];

            setPreference(next);
            applyTheme(next);
            updateButton(btn, next);
            announce(next);
        });
    }

    // Run on DOMContentLoaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
