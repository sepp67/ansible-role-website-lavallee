/* =========================================================
   lavallee.tech — sélecteur de thème (sobre / clair)
   ========================================================= */
(function () {
  "use strict";

  var THEME_KEY = "lavallee-theme";
  var DEFAULT_THEME = "sobre";

  var root = document.documentElement;

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    var buttons = document.querySelectorAll("[data-theme-btn]");
    for (var i = 0; i < buttons.length; i++) {
      var btn = buttons[i];
      btn.setAttribute(
        "aria-pressed",
        btn.getAttribute("data-theme-btn") === theme ? "true" : "false"
      );
    }
  }

  function init() {
    var savedTheme = localStorage.getItem(THEME_KEY) || DEFAULT_THEME;
    applyTheme(savedTheme);

    var buttons = document.querySelectorAll("[data-theme-btn]");
    for (var i = 0; i < buttons.length; i++) {
      buttons[i].addEventListener("click", function (e) {
        var theme = e.currentTarget.getAttribute("data-theme-btn");
        applyTheme(theme);
        try {
          localStorage.setItem(THEME_KEY, theme);
        } catch (err) {
          /* localStorage indisponible (navigation privee, etc.) */
        }
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
