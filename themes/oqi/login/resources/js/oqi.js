/* Presentation only. Authentication, URLs, validation and form submission remain native. */
(function () {
  'use strict';
  document.addEventListener('DOMContentLoaded', function () {
    var root = document.documentElement;
    var toggle = document.getElementById('oqi-theme-toggle');
    if (toggle) {
      try { root.classList.toggle('oqi-dark', localStorage.getItem('oqi-appearance') === 'dark'); } catch (_) {}
      toggle.hidden = false;
      toggle.setAttribute('aria-pressed', String(root.classList.contains('oqi-dark')));
      toggle.addEventListener('click', function () {
        var dark = root.classList.toggle('oqi-dark');
        toggle.setAttribute('aria-pressed', String(dark));
        try { localStorage.setItem('oqi-appearance', dark ? 'dark' : 'light'); } catch (_) {}
      });
    }
    document.querySelectorAll('input[type="password"]').forEach(function (input) {
      if (input.hidden || input.style.display === 'none' || window.getComputedStyle(input).display === 'none') return;
      var wrap = document.createElement('div');
      wrap.className = 'oqi-password-wrap';
      input.parentNode.insertBefore(wrap, input);
      wrap.appendChild(input);
      var button = document.createElement('button');
      button.type = 'button';
      button.className = 'oqi-password-toggle';
      button.setAttribute('aria-label', document.body.dataset.oqiShowPassword);
      button.setAttribute('aria-pressed', 'false');
      button.setAttribute('aria-controls', input.id);
      button.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z"/><circle cx="12" cy="12" r="2.5"/></svg>';
      button.addEventListener('click', function () {
        var show = input.type === 'password';
        input.type = show ? 'text' : 'password';
        button.setAttribute('aria-pressed', String(show));
        button.setAttribute('aria-label', show ? document.body.dataset.oqiHidePassword : document.body.dataset.oqiShowPassword);
      });
      wrap.appendChild(button);
    });
    // The inherited selector uses clickable cards. Preserve its native click handler,
    // while making the same action available from the keyboard.
    document.querySelectorAll('.select-auth-box-parent[onclick]').forEach(function (card) {
      card.tabIndex = 0;
      card.setAttribute('role', 'button');
      card.addEventListener('keydown', function (event) {
        if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); card.click(); }
      });
    });
  });
})();
