/*
 * Dusty Farts page shell: intercepts in-site navigation, swaps <main>,
 * updates the title/History, moves focus to the new h1, and announces the
 * new page through the player's live region. Progressive enhancement only:
 * every page is a complete document and works with JS disabled. See
 * DESIGN.md 6.1. Kept under ~300 lines by design.
 */
(function () {
  "use strict";

  function isInternalNavLink(a) {
    if (!a || a.tagName !== "A") return false;
    if (a.hasAttribute("download")) return false;
    if (a.target && a.target !== "" && a.target !== "_self") return false;
    if (a.origin !== location.origin) return false;
    if (!/\.html$/.test(a.pathname) && a.pathname !== "/" && !a.pathname.endsWith("/")) return false;
    if (a.pathname === location.pathname && a.hash) return false; // in-page anchor
    return true;
  }

  function swapTo(url, addHistory, sourceLinkText) {
    fetch(url, { credentials: "same-origin" })
      .then(function (r) {
        if (!r.ok) throw new Error("bad response");
        return r.text();
      })
      .then(function (html) {
        var doc = new DOMParser().parseFromString(html, "text/html");
        var newMain = doc.querySelector("main");
        var oldMain = document.querySelector("main");
        if (!newMain || !oldMain) throw new Error("no main");

        oldMain.replaceWith(newMain);
        document.title = doc.title;

        var newNav = doc.querySelector("nav.site-nav");
        var oldNav = document.querySelector("nav.site-nav");
        if (newNav && oldNav) oldNav.innerHTML = newNav.innerHTML;

        if (addHistory) {
          history.pushState({ dfSwap: true }, doc.title, url);
        }

        var h1 = newMain.querySelector("h1");
        if (h1) {
          if (!h1.hasAttribute("tabindex")) h1.setAttribute("tabindex", "-1");
          h1.focus();
        }
        window.scrollTo(0, 0);

        if (window.DustyPlayer && window.DustyPlayer.announce) {
          window.DustyPlayer.announce(doc.title + ".");
        }
      })
      .catch(function () {
        location.href = url;
      });
  }

  document.addEventListener("click", function (e) {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    var a = e.target.closest("a");
    if (!isInternalNavLink(a)) return;
    e.preventDefault();
    swapTo(a.href, true);
  });

  window.addEventListener("popstate", function () {
    swapTo(location.href, false);
  });
})();
