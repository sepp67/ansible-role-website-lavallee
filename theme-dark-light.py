#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
theme-dark-light.py

Met le site Hugo lavallee.tech dans l'etat suivant, quel que soit son
etat actuel :
  - retire toute trace du mode "redshift" (calque rouge + slider), s'il
    a ete applique precedemment ;
  - garantit la presence du selecteur de theme Sobre (dark) / Clair (light) ;
  - corrige le contraste du survol des boutons secondaires (GitHub,
    "Lire l'article", ...) avec la palette accent.

Ce script fonctionne quel que soit le point de depart :
  - repo vierge (jamais touche) ;
  - repo sur lequel l'ancienne version "sobre / clair / redshift" a ete
    appliquee ;
  - repo deja en dark/light (execution precedente de ce script ou de
    add-theme-switcher.py).
Il est idempotent : relancez-le autant de fois que necessaire.

Usage :
    cd website-lavallee/          # racine du repo (ou se trouve config.yaml)
    python3 theme-dark-light.py

ATTENTION : static/js/theme-switcher.js et layouts/partials/theme-switch.html
sont entierement generes/geres par ce script. S'ils existent deja avec un
contenu different de la version attendue, ils sont resynchronises (et
l'ancienne version est sauvegardee en .bak). Ne les modifiez pas a la main
si vous comptez relancer ce script plus tard.

Apres execution :
    git diff
    hugo server --buildDrafts
"""

import os
import sys

ROOT = os.getcwd()


def fail(msg):
    print("✗ {}".format(msg))
    sys.exit(1)


def ok(msg):
    print("✓ {}".format(msg))


def skip(msg):
    print("· {}".format(msg))


def warn(msg):
    print("⚠ {}".format(msg))


def check_repo_root():
    if not os.path.isfile(os.path.join(ROOT, "config.yaml")) or not os.path.isdir(
        os.path.join(ROOT, "layouts")
    ):
        fail(
            "config.yaml ou layouts/ introuvable ici.\n"
            "  Lancez ce script depuis la racine du repo website-lavallee."
        )


def read(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write(path, content):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def backup(path):
    bak = path + ".bak"
    if not os.path.exists(bak):
        with open(path, "r", encoding="utf-8") as src, open(
            bak, "w", encoding="utf-8"
        ) as dst:
            dst.write(src.read())


def sync_file(rel_path, content, label):
    """Fichier entierement gere par ce script : on garantit le contenu
    final exact, en sauvegardant l'ancienne version si elle differe."""
    path = os.path.join(ROOT, rel_path)
    if not os.path.exists(path):
        write(path, content)
        ok("Créé {} ({}).".format(rel_path, label))
        return
    existing = read(path)
    if existing.strip() == content.strip():
        skip("{} déjà à jour.".format(rel_path))
        return
    backup(path)
    write(path, content)
    ok("{} resynchronisé ({}) — ancienne version sauvegardée en .bak.".format(
        rel_path, label
    ))


def patch_in_place(rel_path, anchor_old, anchor_new, already_marker, label):
    path = os.path.join(ROOT, rel_path)
    if not os.path.isfile(path):
        warn("{} introuvable, ignoré.".format(rel_path))
        return
    content = read(path)
    if already_marker in content:
        skip("{} : {} déjà présent, rien à faire.".format(rel_path, label))
        return
    if anchor_old not in content:
        warn(
            "{} : ancrage attendu introuvable pour « {} ».\n"
            "  Vérifiez ce fichier manuellement.".format(rel_path, label)
        )
        return
    backup(path)
    content = content.replace(anchor_old, anchor_new, 1)
    write(path, content)
    ok("{} : {} ajouté.".format(rel_path, label))


def remove_if_present(rel_path, old_text, new_text, label):
    """Retire (ou remplace) un bloc s'il est present. Ne fait rien et ne
    previent pas si absent (etat deja propre)."""
    path = os.path.join(ROOT, rel_path)
    if not os.path.isfile(path):
        return
    content = read(path)
    if old_text not in content:
        skip("{} : {} absent, rien à nettoyer.".format(rel_path, label))
        return
    backup(path)
    content = content.replace(old_text, new_text)
    write(path, content)
    ok("{} : {} retiré.".format(rel_path, label))


def append_once(rel_path, marker, block):
    path = os.path.join(ROOT, rel_path)
    if not os.path.isfile(path):
        warn("{} introuvable, ignoré.".format(rel_path))
        return
    content = read(path)
    if marker in content:
        skip("{} : bloc déjà présent, rien à faire.".format(rel_path))
        return
    backup(path)
    with open(path, "a", encoding="utf-8") as f:
        f.write(block)
    ok("{} : bloc ajouté.".format(rel_path))


def ensure_anti_fouc(rel_path, head_anchor_old):
    path = os.path.join(ROOT, rel_path)
    if not os.path.isfile(path):
        warn("{} introuvable, ignoré.".format(rel_path))
        return
    content = read(path)

    if "lavallee-redshift-intensity" in content and FULL_FOUC_SCRIPT in content:
        backup(path)
        content = content.replace(FULL_FOUC_SCRIPT, SIMPLE_FOUC_SCRIPT)
        write(path, content)
        ok("{} : script anti-flash simplifié (redshift retiré).".format(rel_path))
        return

    if "lavallee-theme" in content:
        skip("{} : script anti-flash déjà en place.".format(rel_path))
        return

    if head_anchor_old not in content:
        warn(
            "{} : ancrage introuvable pour le script anti-flash.\n"
            "  Vérifiez ce fichier manuellement.".format(rel_path)
        )
        return

    backup(path)
    content = content.replace(
        head_anchor_old, head_anchor_old + SIMPLE_FOUC_SCRIPT, 1
    )
    write(path, content)
    ok("{} : script anti-flash ajouté.".format(rel_path))


def ensure_theme_switch_yaml(rel_path, language_switch_anchor, full_old_block, simplified_block, lang_label):
    path = os.path.join(ROOT, rel_path)
    if not os.path.isfile(path):
        warn("{} introuvable, ignoré.".format(rel_path))
        return
    content = read(path)

    if full_old_block in content:
        backup(path)
        content = content.replace(full_old_block, simplified_block)
        write(path, content)
        ok("{} : libellés {} nettoyés (redshift retiré).".format(rel_path, lang_label))
        return

    if "theme_switch:" in content:
        skip("{} : libellés {} déjà à jour.".format(rel_path, lang_label))
        return

    if language_switch_anchor not in content:
        warn(
            "{} : ancrage introuvable pour les libellés {}.\n"
            "  Vérifiez ce fichier manuellement.".format(rel_path, lang_label)
        )
        return

    backup(path)
    content = content.replace(
        language_switch_anchor, language_switch_anchor + simplified_block, 1
    )
    write(path, content)
    ok("{} : libellés {} ajoutés.".format(rel_path, lang_label))


# ---------------------------------------------------------------------------
# Contenu canonique final (dark / light uniquement)
# ---------------------------------------------------------------------------

THEME_JS = """/* =========================================================
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
"""

THEME_PARTIAL = """{{ $home := index site.Data (printf "home.%s" .Site.Language.Lang) }}
{{ if not $home }}{{ $home = index site.Data "home.en" }}{{ end }}
<div class="theme-switch" role="group" aria-label="{{ $home.theme_switch.aria_label }}">
  <button type="button" class="theme-switch__btn" data-theme-btn="sobre" aria-pressed="true">
    {{ $home.theme_switch.sober }}
  </button>
  <button type="button" class="theme-switch__btn" data-theme-btn="light" aria-pressed="false">
    {{ $home.theme_switch.light }}
  </button>
</div>
"""

FULL_FOUC_SCRIPT = (
    "\n  <script>\n"
    "    (function () {\n"
    "      try {\n"
    "        var t = localStorage.getItem('lavallee-theme') || 'sobre';\n"
    "        var i = parseFloat(localStorage.getItem('lavallee-redshift-intensity'));\n"
    "        document.documentElement.setAttribute('data-theme', t);\n"
    "        if (!isNaN(i)) document.documentElement.style.setProperty('--redshift-intensity', i);\n"
    "      } catch (e) {}\n"
    "    })();\n"
    "  </script>\n"
)

SIMPLE_FOUC_SCRIPT = (
    "\n  <script>\n"
    "    (function () {\n"
    "      try {\n"
    "        var t = localStorage.getItem('lavallee-theme') || 'sobre';\n"
    "        document.documentElement.setAttribute('data-theme', t);\n"
    "      } catch (e) {}\n"
    "    })();\n"
    "  </script>\n"
)

CSS_LIGHT_THEME_BLOCK = """

/* === Theme clair === */
:root[data-theme="light"] {
  --bg: #f7f5f1;
  --bg-soft: #ffffff;
  --panel: #ffffff;
  --panel-light: #f1efe8;
  --panel-strong: #ffffff;

  --text: #1a1a1a;
  --muted: #5b554c;

  --border: rgba(20, 18, 16, .16);
  --border-soft: rgba(20, 18, 16, .09);

  --shadow: 0 18px 50px rgba(0, 0, 0, .08);
}

:root[data-theme="light"] header {
  background: rgba(255, 255, 255, .88);
}

:root[data-theme="light"] ::selection {
  background: #bcd9ff;
  color: #1a1a1a;
}

/* =========================================================
   Widget de selection de theme (sobre / clair)
   ========================================================= */
.theme-switch {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--muted);
  font-size: .85rem;
}

.theme-switch__btn {
  background: transparent;
  border: 1px solid transparent;
  color: var(--muted);
  padding: 5px 10px;
  border-radius: 999px;
  font-size: .85rem;
  font-family: inherit;
  cursor: pointer;
  transition: color .15s ease, border-color .15s ease, background .15s ease;
}

.theme-switch__btn:hover {
  color: var(--text);
  border-color: var(--border-soft);
  background: var(--panel-light);
}

.theme-switch__btn[aria-pressed="true"] {
  color: var(--text);
  border-color: var(--border-soft);
  background: var(--panel-light);
}
"""

BUTTON_HOVER_LIGHT_CSS = """
:root[data-theme="light"] .button:hover {
  background: rgba(233, 84, 32, .14);
}
"""

# --- segments redshift a retirer du CSS, tels que livres precedemment ---
REDSHIFT_OVERLAY_CSS = (
    "/* =========================================================\n"
    "   Redshift : calque rouge dont l'intensité est réglable\n"
    "   ========================================================= */\n"
    "#redshift-overlay {\n"
    "  position: fixed;\n"
    "  inset: 0;\n"
    "  background-color: #ff0000;\n"
    "  opacity: 0;\n"
    "  mix-blend-mode: multiply;\n"
    "  pointer-events: none;\n"
    "  z-index: 9999;\n"
    "  transition: opacity .15s ease;\n"
    "}\n"
    "\n"
    ':root[data-theme="redshift"] #redshift-overlay {\n'
    "  opacity: var(--redshift-intensity, .15);\n"
    "}\n"
    "\n"
)

REDSHIFT_SLIDER_TAIL_CSS = (
    ".theme-switch__slider {\n"
    "  display: none;\n"
    "  align-items: center;\n"
    "  margin-left: 2px;\n"
    "}\n"
    "\n"
    ':root[data-theme="redshift"] .theme-switch__slider {\n'
    "  display: inline-flex;\n"
    "}\n"
    "\n"
    '.theme-switch__slider input[type="range"] {\n'
    "  width: 90px;\n"
    "  accent-color: var(--accent);\n"
    "  cursor: pointer;\n"
    "}\n"
    "\n"
    "@media (max-width: 900px) {\n"
    '  .theme-switch__slider input[type="range"] {\n'
    "    width: 60px;\n"
    "  }\n"
    "}"
)


def main():
    check_repo_root()
    print("Nettoyage redshift + mise en place du theme sobre/clair...\n")

    # --- 1. fichiers entierement geres : on resynchronise systematiquement ---
    sync_file("static/js/theme-switcher.js", THEME_JS, "sobre/clair uniquement")
    sync_file(
        "layouts/partials/theme-switch.html",
        THEME_PARTIAL,
        "sobre/clair uniquement",
    )

    # --- 2. nettoyage du CSS (retire les blocs redshift s'ils existent) ---
    remove_if_present(
        "static/css/style.css", REDSHIFT_OVERLAY_CSS, "", "calque #redshift-overlay"
    )
    remove_if_present(
        "static/css/style.css",
        "(sobre / clair / redshift)",
        "(sobre / clair)",
        "mention redshift dans un commentaire",
    )
    remove_if_present(
        "static/css/style.css", REDSHIFT_SLIDER_TAIL_CSS, "", "slider redshift"
    )

    # --- 3. garantie du theme clair + widget (ajoute si absent) ---
    append_once(
        "static/css/style.css", '[data-theme="light"]', CSS_LIGHT_THEME_BLOCK
    )

    # --- 4. correctif du survol des boutons secondaires (palette accent) ---
    patch_in_place(
        "static/css/style.css",
        anchor_old=(
            "    .button:hover {\n"
            "      transform: translateY(-1px);\n"
            "      background: #2a2e30;\n"
            "      border-color: var(--accent);\n"
            "      color: var(--text);\n"
            "    }\n"
        ),
        anchor_new=(
            "    .button:hover {\n"
            "      transform: translateY(-1px);\n"
            "      background: rgba(233, 84, 32, .22);\n"
            "      border-color: var(--accent);\n"
            "      color: var(--text);\n"
            "    }\n"
        ),
        already_marker="rgba(233, 84, 32, .22)",
        label="correction du survol des boutons (palette accent, sobre)",
    )
    append_once(
        "static/css/style.css",
        '[data-theme="light"] .button:hover',
        BUTTON_HOVER_LIGHT_CSS,
    )

    # --- 5. layouts/_default/baseof.html -----------------------------------
    ensure_anti_fouc(
        "layouts/_default/baseof.html",
        head_anchor_old=(
            '  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
        ),
    )
    patch_in_place(
        "layouts/_default/baseof.html",
        anchor_old=(
            "      </div>\n"
            "\n"
            '      <a class="button" href="{{ .Site.Params.github }}" target="_blank" rel="noreferrer">GitHub</a>\n'
        ),
        anchor_new=(
            "      </div>\n"
            "\n"
            '      {{ partial "theme-switch.html" . }}\n'
            "\n"
            '      <a class="button" href="{{ .Site.Params.github }}" target="_blank" rel="noreferrer">GitHub</a>\n'
        ),
        already_marker='partial "theme-switch.html"',
        label="widget theme-switch (nav)",
    )
    patch_in_place(
        "layouts/_default/baseof.html",
        anchor_old="  </footer>\n</body>",
        anchor_new=(
            '  </footer>\n\n  <script src="/js/theme-switcher.js" defer></script>\n</body>'
        ),
        already_marker="theme-switcher.js",
        label="script JS (avant </body>)",
    )

    # --- 6. layouts/index.html (page d'accueil, template autonome) --------
    ensure_anti_fouc(
        "layouts/index.html",
        head_anchor_old=(
            '  <meta name="viewport" content="width=device-width, initial-scale=1">\n'
        ),
    )
    patch_in_place(
        "layouts/index.html",
        anchor_old=(
            "      </div>\n"
            "\n"
            '      <a class="button" href="{{ .Site.Params.github }}" target="_blank" rel="noreferrer">GitHub</a>\n'
        ),
        anchor_new=(
            "      </div>\n"
            "\n"
            '      {{ partial "theme-switch.html" . }}\n'
            "\n"
            '      <a class="button" href="{{ .Site.Params.github }}" target="_blank" rel="noreferrer">GitHub</a>\n'
        ),
        already_marker='partial "theme-switch.html"',
        label="widget theme-switch (nav)",
    )
    patch_in_place(
        "layouts/index.html",
        anchor_old="  </footer>\n</body>",
        anchor_new=(
            '  </footer>\n\n  <script src="/js/theme-switcher.js" defer></script>\n</body>'
        ),
        already_marker="theme-switcher.js",
        label="script JS (avant </body>)",
    )

    # --- 7. libelles localises (nettoyes ou ajoutes selon l'etat) ---------
    ensure_theme_switch_yaml(
        "data/home.fr.yaml",
        language_switch_anchor="language_switch:\n  aria_label: Sélecteur de langue\n",
        full_old_block=(
            "theme_switch:\n"
            "  aria_label: Sélecteur de thème\n"
            "  sober: Sobre\n"
            "  light: Clair\n"
            "  redshift: Redshift\n"
            "  intensity_label: Intensité du rouge\n"
        ),
        simplified_block=(
            "theme_switch:\n"
            "  aria_label: Sélecteur de thème\n"
            "  sober: Sobre\n"
            "  light: Clair\n"
        ),
        lang_label="FR",
    )
    ensure_theme_switch_yaml(
        "data/home.en.yaml",
        language_switch_anchor="language_switch:\n  aria_label: Language switcher\n",
        full_old_block=(
            "theme_switch:\n"
            "  aria_label: Theme switcher\n"
            "  sober: Dark\n"
            "  light: Light\n"
            "  redshift: Redshift\n"
            "  intensity_label: Red intensity\n"
        ),
        simplified_block=(
            "theme_switch:\n"
            "  aria_label: Theme switcher\n"
            "  sober: Dark\n"
            "  light: Light\n"
        ),
        lang_label="EN",
    )
    ensure_theme_switch_yaml(
        "data/home.de.yaml",
        language_switch_anchor="language_switch:\n  aria_label: Sprachauswahl\n",
        full_old_block=(
            "theme_switch:\n"
            "  aria_label: Themenauswahl\n"
            "  sober: Dunkel\n"
            "  light: Hell\n"
            "  redshift: Redshift\n"
            "  intensity_label: Rotintensität\n"
        ),
        simplified_block=(
            "theme_switch:\n"
            "  aria_label: Themenauswahl\n"
            "  sober: Dunkel\n"
            "  light: Hell\n"
        ),
        lang_label="DE",
    )

    print(
        "\nTermine. Verifiez avec `git diff`, testez avec "
        "`hugo server --buildDrafts`.\n"
        "Des fichiers .bak ont ete crees a cote de chaque fichier modifie ;\n"
        "vous pouvez les supprimer une fois le resultat valide, ou faire\n"
        "`git checkout -- .` (+ `git clean -fd` pour les nouveaux fichiers)\n"
        "pour tout annuler avant de relancer."
    )


if __name__ == "__main__":
    main()
