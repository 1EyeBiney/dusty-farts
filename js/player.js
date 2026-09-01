/*
 * Dusty Farts persistent player. See DESIGN.md section 6 for the full spec.
 * No framework. No keyboard takeover: single letters are only bound on
 * `window` for H and ? (ignored in inputs / with modifiers); the full
 * transport key map only applies while focus is inside the player panel.
 */
(function () {
  "use strict";

  var BASE = window.SITE_BASE || "";
  var STORAGE_KEY = "dustyfarts:player:v1";
  var SETTINGS_KEY = "dustyfarts:settings:v1";

  var episodesData = null; // full data/episodes.json, fetched once
  var episodeOrder = []; // array of episode objects in catalog order
  var byWebSlug = {}; // slug -> episode object (episodes only, not hope-welcome)

  var audio = null;
  var region, bar, panel, barTitle, nowPlayingEl, timeEl, seekEl;
  var liveRegion, chaptersPanel, chaptersList, shortcutsPanel, dot;
  var current = null; // the episode (or pseudo-episode) the UI is showing
  // Which slug is actually loaded into the audio element. `current` alone is
  // not enough: init() restores it from localStorage to label the bar, without
  // loading any audio, so a play() based on `current` would run against an
  // element that has no source. Only loadEpisode() sets this.
  var loadedSlug = null;
  var activeRangeKey = null; // "slug:start" when a specific chapter/jukebox track was explicitly selected
  var lastFocusBeforeExpand = null;
  var announceTimer = null;
  var saveTimer = null;

  function $(id) { return document.getElementById(id); }

  function safeLocalStorage() {
    try {
      var k = "__df_test__";
      window.localStorage.setItem(k, "1");
      window.localStorage.removeItem(k);
      return window.localStorage;
    } catch (e) {
      return null;
    }
  }
  var storage = safeLocalStorage();

  function loadState() {
    if (!storage) return {};
    try { return JSON.parse(storage.getItem(STORAGE_KEY)) || {}; } catch (e) { return {}; }
  }
  function saveState(patch) {
    if (!storage) return;
    try {
      var s = loadState();
      for (var k in patch) s[k] = patch[k];
      storage.setItem(STORAGE_KEY, JSON.stringify(s));
    } catch (e) { /* ignore */ }
  }
  function loadSettings() {
    if (!storage) return { autoAdvance: true };
    try {
      var s = JSON.parse(storage.getItem(SETTINGS_KEY));
      return s || { autoAdvance: true };
    } catch (e) { return { autoAdvance: true }; }
  }
  function saveSettings(s) {
    if (!storage) return;
    try { storage.setItem(SETTINGS_KEY, JSON.stringify(s)); } catch (e) { /* ignore */ }
  }

  function fmtTime(sec) {
    sec = Math.max(0, Math.floor(sec || 0));
    var h = Math.floor(sec / 3600);
    var m = Math.floor((sec % 3600) / 60);
    var s = sec % 60;
    var mm = h > 0 ? String(m).padStart(2, "0") : String(m);
    var ss = String(s).padStart(2, "0");
    return h > 0 ? h + ":" + mm + ":" + ss : mm + ":" + ss;
  }
  function fmtTimeWords(sec) {
    sec = Math.max(0, Math.floor(sec || 0));
    var m = Math.floor(sec / 60);
    var s = sec % 60;
    var parts = [];
    if (m > 0) parts.push(m + " minute" + (m === 1 ? "" : "s"));
    parts.push(s + " second" + (s === 1 ? "" : "s"));
    return parts.join(" ");
  }

  function announce(text) {
    if (!liveRegion) return;
    clearTimeout(announceTimer);
    liveRegion.textContent = "";
    announceTimer = setTimeout(function () {
      liveRegion.textContent = text;
    }, 60);
  }

  function fetchEpisodes() {
    if (episodesData) return Promise.resolve(episodesData);
    return fetch(BASE + "data/episodes.json").then(function (r) { return r.json(); }).then(function (data) {
      episodesData = data;
      episodeOrder = data.episodes.slice().sort(function (a, b) { return a.number - b.number; });
      episodeOrder.forEach(function (ep) { byWebSlug[ep.slug] = ep; });
      return data;
    });
  }

  /*
   * Run `fn` with episode data available, SYNCHRONOUSLY whenever we already
   * have it. This matters on iOS: Safari only allows audio.play() while the
   * user's tap is still being handled, and any .then() hop - even an already
   * resolved promise - ends that window. init() fetches episodes.json on page
   * load, so by the time anyone taps Play the data is virtually always cached
   * and this stays inside the gesture. The async path is only for the rare
   * tap that beats the initial fetch.
   */
  function withEpisodes(fn) {
    if (episodesData) { fn(); return; }
    fetchEpisodes().then(fn);
  }

  /*
   * Every play() rejection used to be swallowed by an empty catch, so a
   * blocked play produced no sound, no message, and no visible change. Say
   * something instead. AbortError is routine - it fires whenever a new
   * load()/src assignment interrupts a play already in flight (switching
   * episodes, jumping between jukebox tracks) - so it stays silent.
   */
  function handlePlayError(err) {
    if (err && (err.name === "AbortError" || err.name === "NotSupportedError")) return;
    updatePlayButtons(false);
    announce("Playback did not start. Press Play to try again.");
  }

  function startPlayback() {
    var p = audio.play();
    if (p && p.catch) p.catch(handlePlayError);
    return p;
  }

  /*
   * iOS ties "this element may play" to the element having been started by a
   * real user gesture at least once. Playback we start later from a timer or
   * event - auto-advance at the end of an episode, the end of a jukebox
   * range, a Media Session control - is not in a gesture, so prime the
   * element on the very first interaction with the page using a short silent
   * clip. No network: the clip is a data URI.
   */
  var audioUnlocked = false;
  var SILENT_WAV = "data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEARKwAAIhYAQACABAAZGF0YQAAAAA=";
  function unlockAudio() {
    if (audioUnlocked || !audio) return;
    audioUnlocked = true;
    // Never disturb a real source that is already loaded or playing.
    if (audio.currentSrc || audio.src) return;
    try {
      audio.src = SILENT_WAV;
      var p = audio.play();
      if (p && p.then) {
        p.then(function () {
          // A real episode may have loaded in between (the same gesture that
          // primed us is often the tap that starts one). Only touch the
          // element if the silent clip is still what's loaded - pausing or
          // clearing here otherwise would kill the episode just started.
          if (audio.src !== SILENT_WAV) return;
          audio.pause();
        }).catch(function () { /* priming is best-effort */ });
      }
    } catch (e) { /* priming is best-effort */ }
    // No cleanup of the src: loadEpisode always assigns a real source before
    // playing, so the leftover data URI is harmless and clearing it risks
    // racing that assignment.
  }

  /*
   * Prime on the first real interaction, whatever form it takes - a tap, a
   * key, or a pointer. `capture: true` so this runs before the click handler
   * that may be about to start a real episode, and `once: true` so it costs
   * nothing afterwards. Touch/pointer/keyboard are all covered because Brian
   * uses the keyboard and phone users tap.
   */
  function wireAudioUnlock() {
    var opts = { once: true, capture: true, passive: true };
    ["pointerdown", "touchstart", "keydown"].forEach(function (evt) {
      document.addEventListener(evt, unlockAudio, opts);
    });
  }

  function hopeWelcomeEpisode() {
    if (!episodesData || !episodesData.show.hopeWelcome) return null;
    return {
      slug: "hope-welcome",
      title: "Hope’s Welcome",
      webFile: episodesData.show.hopeWelcome,
      chapters: [],
      isWelcome: true
    };
  }

  function findEpisode(slug) {
    if (slug === "hope-welcome") return hopeWelcomeEpisode();
    return byWebSlug[slug] || null;
  }

  function episodeLabel(ep) {
    if (ep.isWelcome) return "Hope’s welcome";
    return "Episode " + ep.number + ", " + ep.title;
  }

  /* ---------------- core playback ---------------- */

  function loadEpisode(ep, opts) {
    opts = opts || {};
    current = ep;
    loadedSlug = ep.slug;
    audio.src = BASE + ep.webFile;
    audio.load();
    updateNowPlaying();
    renderChapters();
    updateEpisodeButtons();
    updateRangeButtons();
    if (window.navigator && "mediaSession" in navigator) {
      try {
        navigator.mediaSession.metadata = new MediaMetadata({
          title: ep.isWelcome ? "Hope’s Welcome" : "Episode " + ep.number + ": " + ep.title,
          artist: "Dusty Farts",
          album: "Dusty Farts",
          artwork: ep.artWeb ? [{ src: BASE + ep.artWeb, sizes: "1400x1400", type: "image/jpeg" }] : []
        });
      } catch (e) { /* ignore */ }
    }
    var startAt = 0;
    if (typeof opts.startAt === "number") {
      startAt = opts.startAt;
    } else if (opts.resume) {
      var s = loadState();
      if (s.episodeSlug === ep.slug && typeof s.position === "number") startAt = s.position;
    }

    /*
     * Order matters here, and it is the whole reason mobile was silent.
     * play() MUST be called while the user's tap is still being handled -
     * iOS Safari rejects it otherwise - so we never defer it behind
     * loadedmetadata any more. With preload="none" readyState was always 0
     * at this point, so the old code deferred every single play and iOS
     * blocked every single one, silently.
     *
     * When metadata is already there (a re-play, or preload="metadata" has
     * done its job) we seek first and then play, which is seamless. When it
     * isn't, we play immediately to keep the gesture, and apply the seek as
     * soon as metadata lands - costing at most a brief moment of the opening
     * before it jumps to the requested point.
     */
    var wantsPlay = opts.autoplay !== false;
    if (audio.readyState >= 1) {
      if (startAt > 0) audio.currentTime = startAt;
      if (wantsPlay) startPlayback();
    } else {
      if (wantsPlay) startPlayback();
      if (startAt > 0) {
        audio.addEventListener("loadedmetadata", function () {
          audio.currentTime = startAt;
        }, { once: true });
      }
    }

    saveState({ episodeSlug: ep.slug, position: startAt });
  }

  function updateNowPlaying() {
    if (!current) return;
    var text = current.isWelcome ? "Hope’s Welcome" : "Episode " + current.number + ": " + current.title;
    if (barTitle) barTitle.textContent = text;
    if (nowPlayingEl) nowPlayingEl.textContent = text;
  }

  function playEpisode(slug, opts) {
    withEpisodes(function () {
      var ep = findEpisode(slug);
      if (!ep) return;
      var isSame = current && current.slug === ep.slug && loadedSlug === ep.slug;
      if (!isSame) {
        loadEpisode(ep, opts);
      } else if (opts && opts.startAt !== undefined) {
        audio.currentTime = opts.startAt;
        startPlayback();
      } else {
        startPlayback();
      }
      // Play buttons never move focus - starting audio should never yank a
      // screen reader user away from wherever they activated it (an episode
      // listing row, a chapter, a jukebox track). Only the explicit H key and
      // the bar's "Expand player" button move focus into the panel.
      expand(false);
      // A single, authoritative announce per action - callers that already
      // know a more specific message (a chapter/jingle title) pass it in via
      // opts.announceText. The native "play" event fires asynchronously right
      // after this and would otherwise re-announce the generic episode title;
      // suppress that one occurrence so the specific message isn't clobbered.
      suppressNextPlayAnnounce = true;
      if (opts && opts.announceFull) {
        announce(opts.announceFull);
      } else {
        announce("Playing: " + (opts && opts.announceText ? opts.announceText : episodeLabel(ep)) + ".");
      }
      // Jumping straight from one chapter/track to another while already
      // playing doesn't fire a native "play" event (the element was never
      // actually paused), so the button labels need updating directly here
      // too, not only from wireAudioEvents' play/pause listeners.
      updateEpisodeButtons();
      updateRangeButtons();
    });
  }
  var suppressNextPlayAnnounce = false;
  window.DustyPlayer = window.DustyPlayer || {};
  window.DustyPlayer.play = playEpisode;
  window.DustyPlayer.togglePlayFor = function (slug) {
    withEpisodes(function () {
      if (current && current.slug === slug && !audio.paused) {
        togglePlayPause();
      } else {
        activeRangeKey = null;
        playEpisode(slug, { resume: true });
      }
    });
  };
  window.DustyPlayer.playChapter = function (slug, chapterIndex) {
    withEpisodes(function () {
      var ep = findEpisode(slug);
      if (!ep || !ep.chapters || !ep.chapters[chapterIndex]) return;
      var ch = ep.chapters[chapterIndex];
      activeRangeKey = slug + ":" + ch.start;
      playEpisode(slug, {
        startAt: ch.start,
        announceFull: "Chapter " + (chapterIndex + 1) + ": " + ch.title + "."
      });
    });
  };
  window.DustyPlayer.toggleChapterFor = function (slug, chapterIndex) {
    withEpisodes(function () {
      var ep = findEpisode(slug);
      if (!ep || !ep.chapters || !ep.chapters[chapterIndex]) return;
      var key = slug + ":" + ep.chapters[chapterIndex].start;
      if (current && current.slug === slug && activeRangeKey === key && !audio.paused) {
        togglePlayPause();
      } else {
        window.DustyPlayer.playChapter(slug, chapterIndex);
      }
    });
  };
  window.DustyPlayer.playRange = function (slug, startAt, endAt, label) {
    withEpisodes(function () {
      var ep = findEpisode(slug);
      if (!ep) return;
      pendingRangeEnd = endAt;
      activeRangeKey = slug + ":" + startAt;
      playEpisode(slug, { startAt: startAt, announceText: label });
    });
  };
  window.DustyPlayer.toggleRangeFor = function (slug, startAt, endAt, label) {
    withEpisodes(function () {
      var key = slug + ":" + startAt;
      if (current && current.slug === slug && activeRangeKey === key && !audio.paused) {
        togglePlayPause();
      } else {
        window.DustyPlayer.playRange(slug, startAt, endAt, label);
      }
    });
  };

  var pendingRangeEnd = null;

  function togglePlayPause() {
    if (!current) {
      var first = episodeOrder[0];
      if (first) playEpisode(first.slug, { resume: true });
      return;
    }
    if (audio.paused) {
      startPlayback();
    } else {
      audio.pause();
    }
  }

  function seekBy(delta) {
    if (!current) return;
    audio.currentTime = Math.max(0, Math.min(audio.duration || Infinity, audio.currentTime + delta));
    announce(fmtTimeWords(audio.currentTime) + " of " + fmtTimeWords(audio.duration) + ".");
    persistPosition();
  }

  function restart() {
    if (!current) return;
    activeRangeKey = null;
    audio.currentTime = 0;
    startPlayback();
  }

  function currentChapterIndex() {
    if (!current || !current.chapters || !current.chapters.length) return -1;
    var t = audio.currentTime;
    for (var i = current.chapters.length - 1; i >= 0; i--) {
      if (t >= current.chapters[i].start - 0.25) return i;
    }
    return -1;
  }
  function jumpChapter(dir) {
    if (!current || !current.chapters || !current.chapters.length) {
      announce("No chapters in this episode.");
      return;
    }
    var idx = currentChapterIndex();
    var target = idx + dir;
    if (dir > 0) target = idx + 1;
    if (target < 0) target = 0;
    if (target >= current.chapters.length) target = current.chapters.length - 1;
    var ch = current.chapters[target];
    audio.currentTime = ch.start;
    announce("Chapter " + (target + 1) + ": " + ch.title + ".");
    persistPosition();
  }

  function switchEpisode(dir) {
    if (!episodeOrder.length) return;
    var idx = current && !current.isWelcome ? episodeOrder.findIndex(function (e) { return e.slug === current.slug; }) : -1;
    var target = idx + dir;
    if (target < 0 || target >= episodeOrder.length) return;
    var ep = episodeOrder[target];
    activeRangeKey = null;
    announce("Episode " + ep.number + ": " + ep.title + ". Press play to start it.");
    loadEpisode(ep, { resume: true, autoplay: false });
  }

  function persistPosition() {
    if (!current) return;
    saveState({ episodeSlug: current.slug, position: audio.currentTime });
  }

  /* ---------------- panel expand/collapse ---------------- */

  function expand(focusPanel) {
    if (!region) return;
    if (region.getAttribute("data-expanded") === "true") {
      if (focusPanel !== false) panel.focus();
      return;
    }
    lastFocusBeforeExpand = document.activeElement;
    region.setAttribute("data-expanded", "true");
    if (focusPanel !== false) {
      var h2 = panel.querySelector("h2");
      if (h2) h2.focus();
    }
  }
  function collapse(restoreFocus) {
    if (!region) return;
    closeShortcuts();
    closeChapters();
    region.setAttribute("data-expanded", "false");
    if (restoreFocus !== false && lastFocusBeforeExpand && document.contains(lastFocusBeforeExpand)) {
      lastFocusBeforeExpand.focus();
    }
  }
  function toggleExpand() {
    if (region.getAttribute("data-expanded") === "true") collapse(true);
    else expand(true);
  }

  function openShortcuts() {
    shortcutsPanel.hidden = false;
    var h = shortcutsPanel.querySelector("[tabindex]");
    if (h) h.focus();
  }
  function closeShortcuts() {
    if (shortcutsPanel) shortcutsPanel.hidden = true;
  }
  function openChapters() {
    chaptersPanel.hidden = false;
    var first = chaptersPanel.querySelector("button");
    if (first) first.focus();
  }
  function closeChapters() {
    if (chaptersPanel) chaptersPanel.hidden = true;
  }

  function renderChapters() {
    if (!chaptersList) return;
    chaptersList.innerHTML = "";
    if (!current || !current.chapters || !current.chapters.length) {
      var li = document.createElement("li");
      li.textContent = "No chapters in this episode.";
      chaptersList.appendChild(li);
      return;
    }
    current.chapters.forEach(function (ch, i) {
      var li = document.createElement("li");
      var btn = document.createElement("button");
      btn.type = "button";
      btn.className = "btn btn-quiet";
      btn.setAttribute("data-play-key", current.slug + ":" + ch.start);
      btn.textContent = "Play chapter " + (i + 1) + ": " + ch.title + ", " + fmtTimeWords(ch.end - ch.start) + ".";
      btn.addEventListener("click", function () {
        // Toggles in place: never moves focus, and pressing the already-
        // playing chapter again pauses it instead of restarting it.
        window.DustyPlayer.toggleChapterFor(current.slug, i);
        closeChapters();
      });
      li.appendChild(btn);
      chaptersList.appendChild(li);
    });
  }

  /* ---------------- wiring ---------------- */

  function wireButtons() {
    panel.querySelectorAll("[data-action]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        handleAction(btn.getAttribute("data-action"));
      });
    });
    bar.querySelectorAll("[data-action]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        handleAction(btn.getAttribute("data-action"));
      });
    });
  }

  function handleAction(action) {
    switch (action) {
      case "playpause": togglePlayPause(); break;
      case "back10": seekBy(-10); break;
      case "fwd10": seekBy(10); break;
      case "back60": seekBy(-60); break;
      case "fwd60": seekBy(60); break;
      case "back300": seekBy(-300); break;
      case "fwd300": seekBy(300); break;
      case "prevchapter": jumpChapter(-1); break;
      case "nextchapter": jumpChapter(1); break;
      case "prevepisode": switchEpisode(-1); break;
      case "nextepisode": switchEpisode(1); break;
      case "restart": restart(); break;
      case "chapters": chaptersPanel.hidden ? openChapters() : closeChapters(); break;
      case "shortcuts": shortcutsPanel.hidden ? openShortcuts() : closeShortcuts(); break;
      case "expand": expand(true); break;
      case "collapse": collapse(true); break;
    }
  }

  function wireAudioEvents() {
    audio.addEventListener("play", function () {
      region.setAttribute("data-playing", "true");
      updatePlayButtons(true);
      if (suppressNextPlayAnnounce) {
        suppressNextPlayAnnounce = false;
      } else {
        announce("Playing: " + episodeLabel(current) + ".");
      }
    });
    audio.addEventListener("pause", function () {
      region.setAttribute("data-playing", "false");
      updatePlayButtons(false);
      persistPosition();
      if (!audio.ended) announce("Paused at " + fmtTimeWords(audio.currentTime) + ".");
    });
    audio.addEventListener("timeupdate", function () {
      if (timeEl) timeEl.textContent = fmtTime(audio.currentTime) + " / " + fmtTime(audio.duration || 0);
      if (seekEl && !seekEl.matches(":active")) {
        seekEl.max = String(Math.floor(audio.duration || 0));
        seekEl.value = String(Math.floor(audio.currentTime));
      }
      if (pendingRangeEnd !== null && audio.currentTime >= pendingRangeEnd) {
        audio.pause();
        pendingRangeEnd = null;
      }
      if (!saveTimer) {
        saveTimer = setTimeout(function () { saveTimer = null; persistPosition(); }, 15000);
      }
    });
    audio.addEventListener("ended", function () {
      pendingRangeEnd = null;
      var settings = loadSettings();
      var idx = episodeOrder.findIndex(function (e) { return current && e.slug === current.slug; });
      var next = idx >= 0 ? episodeOrder[idx + 1] : null;
      if (next && settings.autoAdvance !== false) {
        activeRangeKey = null;
        announce("End of " + episodeLabel(current) + ". Next up: Episode " + next.number + ", " + next.title + ".");
        loadEpisode(next, { autoplay: true });
      } else if (next) {
        announce("End of " + episodeLabel(current) + ".");
      } else {
        announce("End of " + episodeLabel(current) + ". That’s the whole story, so far.");
      }
    });
  }

  function updatePlayButtons(playing) {
    var label = playing ? "Pause" : "Play";
    document.querySelectorAll('[data-action="playpause"]').forEach(function (b) {
      b.setAttribute("aria-label", label);
      b.textContent = playing ? "⏸" : "▶"; // pause / play glyphs
    });
    updateEpisodeButtons();
    updateRangeButtons();
  }

  function updateEpisodeButtons() {
    var playing = current && !audio.paused;
    document.querySelectorAll("[data-episode-slug]").forEach(function (b) {
      if (!b.hasAttribute("data-play-label")) {
        b.setAttribute("data-play-label", b.textContent);
      }
      var base = b.getAttribute("data-play-label");
      var isThisOne = playing && b.getAttribute("data-episode-slug") === current.slug;
      b.textContent = isThisOne ? base.replace(/^Play\b/, "Pause") : base;
    });
  }

  // Jukebox tracks and chapter-list items: same idea as updateEpisodeButtons,
  // but keyed on "slug:start" (activeRangeKey) since several buttons can
  // share one episode slug and only the exact clip/chapter that was picked
  // should read "Pause". Handles both label styles in the markup: a plain
  // "Play ..." sentence (chapter buttons) and an icon button with an
  // aria-label (jukebox buttons).
  function updateRangeButtons() {
    var activeKey = current && !audio.paused ? activeRangeKey : null;
    document.querySelectorAll("[data-play-key]").forEach(function (b) {
      var isThisOne = activeKey !== null && b.getAttribute("data-play-key") === activeKey;
      var ariaBase = b.getAttribute("data-play-aria-base");
      if (ariaBase === null && b.hasAttribute("aria-label")) {
        ariaBase = b.getAttribute("aria-label");
        b.setAttribute("data-play-aria-base", ariaBase);
      }
      if (ariaBase !== null) {
        b.setAttribute("aria-label", isThisOne ? ariaBase.replace(/^Play\b/, "Pause") : ariaBase);
      }
      if (!b.hasAttribute("data-play-label")) {
        b.setAttribute("data-play-label", b.textContent);
      }
      var baseText = b.getAttribute("data-play-label");
      if (baseText === "▶" || baseText === "⏸") {
        b.textContent = isThisOne ? "⏸" : "▶";
      } else {
        b.textContent = isThisOne ? baseText.replace(/^Play\b/, "Pause") : baseText;
      }
    });
  }

  function wireSeek() {
    if (!seekEl) return;
    seekEl.addEventListener("input", function () {
      audio.currentTime = Number(seekEl.value);
    });
    seekEl.addEventListener("change", function () {
      announce(fmtTimeWords(audio.currentTime) + " of " + fmtTimeWords(audio.duration) + ".");
      persistPosition();
    });
  }

  function wireAutoAdvanceToggle() {
    var cb = $("player-autoadvance");
    if (!cb) return;
    var settings = loadSettings();
    cb.checked = settings.autoAdvance !== false;
    cb.addEventListener("change", function () {
      saveSettings({ autoAdvance: cb.checked });
    });
  }

  function isTypingTarget(el) {
    if (!el) return false;
    var tag = el.tagName;
    return tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || el.isContentEditable;
  }

  function wireGlobalKeys() {
    window.addEventListener("keydown", function (e) {
      if (e.altKey || e.ctrlKey || e.metaKey) return;
      if (isTypingTarget(e.target)) return;
      if (e.key === "h" || e.key === "H") {
        if (region.getAttribute("data-expanded") === "true" && region.contains(document.activeElement)) {
          collapse(true);
        } else {
          expand(true);
        }
        e.preventDefault();
      } else if (e.key === "?") {
        if (!audio.paused) audio.pause();
        expand(false);
        openShortcuts();
        e.preventDefault();
      }
    });
  }

  function wirePanelKeys() {
    region.addEventListener("keydown", function (e) {
      if (e.altKey || e.metaKey) return;
      if ((e.key === "ArrowLeft" || e.key === "ArrowRight") && e.ctrlKey) {
        seekBy(e.key === "ArrowLeft" ? -300 : 300);
        e.preventDefault();
        return;
      }
      if (e.ctrlKey) return;
      if (isTypingTarget(e.target) && e.target !== seekEl) return;
      // The seek slider is a native <input type="range">: Up/Down are its
      // own built-in step keys (browsers and screen readers both already
      // handle them), so let them through instead of stealing Up/Down for
      // episode switching while focus happens to be on this one control.
      if (e.target === seekEl && (e.key === "ArrowUp" || e.key === "ArrowDown")) return;
      switch (e.key) {
        case " ":
          if (e.target.tagName === "BUTTON") return; // let native activation happen
          togglePlayPause(); e.preventDefault(); break;
        case "ArrowLeft":
          if (e.shiftKey) seekBy(-60); else seekBy(-10);
          e.preventDefault(); break;
        case "ArrowRight":
          if (e.shiftKey) seekBy(60); else seekBy(10);
          e.preventDefault(); break;
        case "PageUp": jumpChapter(-1); e.preventDefault(); break;
        case "PageDown": jumpChapter(1); e.preventDefault(); break;
        case "ArrowUp": switchEpisode(-1); e.preventDefault(); break;
        case "ArrowDown": switchEpisode(1); e.preventDefault(); break;
        case "Home": restart(); e.preventDefault(); break;
        case "c": case "C": openChapters(); e.preventDefault(); break;
        case "?":
          if (!audio.paused) audio.pause();
          openShortcuts();
          e.preventDefault();
          break;
        case "Escape":
          if (!shortcutsPanel.hidden) { closeShortcuts(); }
          else if (!chaptersPanel.hidden) { closeChapters(); }
          else { collapse(true); }
          e.preventDefault();
          break;
      }
    });
  }

  function wireMediaSession() {
    if (!("mediaSession" in navigator)) return;
    try {
      navigator.mediaSession.setActionHandler("play", function () { startPlayback(); });
      navigator.mediaSession.setActionHandler("pause", function () { audio.pause(); });
      navigator.mediaSession.setActionHandler("seekbackward", function () { seekBy(-10); });
      navigator.mediaSession.setActionHandler("seekforward", function () { seekBy(10); });
      navigator.mediaSession.setActionHandler("previoustrack", function () { switchEpisode(-1); });
      navigator.mediaSession.setActionHandler("nexttrack", function () { switchEpisode(1); });
    } catch (e) { /* ignore unsupported actions */ }
  }

  function wireVisibility() {
    document.addEventListener("visibilitychange", persistPosition);
    window.addEventListener("pagehide", persistPosition);
  }

  function init() {
    region = $("df-player");
    if (!region) return;
    bar = $("df-player-bar");
    panel = $("df-player-panel");
    barTitle = $("df-player-bar-title");
    nowPlayingEl = $("df-player-nowplaying");
    timeEl = $("df-player-time");
    seekEl = $("df-player-seek");
    liveRegion = $("df-player-live");
    chaptersPanel = $("df-player-chapters");
    chaptersList = $("df-player-chapters-list");
    shortcutsPanel = $("df-player-shortcuts");
    dot = $("df-player-dot");

    audio = new Audio();
    // "none" prevented metadata from ever loading on iOS until a
    // gesture-initiated play, while the play itself waited on loadedmetadata.
    // "metadata" breaks that deadlock and makes readyState >= 1 the common
    // case, so seeks land before playback starts.
    audio.preload = "metadata";
    audio.setAttribute("playsinline", "");

    wireButtons();
    wireAudioEvents();
    wireSeek();
    wireAutoAdvanceToggle();
    wireGlobalKeys();
    wirePanelKeys();
    wireMediaSession();
    wireVisibility();
    wireAudioUnlock();

    fetchEpisodes().then(function () {
      var s = loadState();
      if (s.episodeSlug) {
        var ep = findEpisode(s.episodeSlug);
        if (ep) {
          current = ep;
          updateNowPlaying();
          renderChapters();
        }
      }
    });

    // expose for the page-swap layer (js/site.js) to re-announce titles etc.
    window.DustyPlayer.announce = announce;
    window.DustyPlayer.isExpanded = function () { return region.getAttribute("data-expanded") === "true"; };
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
