# Dusty Farts — Website Design Document

**Status: authoritative.** This document defines what the site is and exactly how it
behaves. It was shaped with Brian in conversation and supersedes the sketch-level
parts of HANDOFF.md; HANDOFF.md remains the build-order checklist and its Phase 0 /
Phase 3 mechanics still apply. Where the two disagree, DESIGN.md wins.
CLAUDE.md's hard rules (git scope, 128k-only audio, accessibility as acceptance
criterion) apply to everything here.

---

## 1. Vision

A small-town website for a small-town show. The site is narrated by Hope — the
show's omniscient, dry-witted narrator — as if Maple Grove commissioned her to give
visitors the tour. It is audio-first, keyboard-first, and screen-reader-native,
because its creator is, and because its audience includes blind listeners who
deserve a site that treats them as the primary customer rather than an afterthought.

Design promise, in one line: **the bones stay honest, the voice stays Hope's.**
Structure (headings, nav labels, buttons, announcements) always says literally what
it is. Prose (welcomes, descriptions, empty corners, error pages) belongs to Hope.
A visitor with NVDA always knows where they are; they're just being told about it
by a narrator with opinions.

## 2. Audience and goals

Primary: comedy podcast listeners — family, friends, and strangers alike. The show
leads; jokes come first. Secondary: people discovering that the entire show is
written, scored, and engineered non-visually by a blind producer — the About page
tells that story properly, and home mentions it in one proud line. The site also
quietly serves as a demonstration piece for Brian's screen reader students.

Goals, in order: (1) get a first-time visitor to press play on Episode 1 within a
minute; (2) let a returning listener resume exactly where they left off, keyboard
only; (3) make subscribing in a podcast app one obvious step; (4) tell Brian's
story well.

## 3. Voice rules

- Hope's register: warm, conspiratorial, slightly weary, fond of her subjects.
  Reference material: Show Notes docx files and Hope's narration in the scripts.
- Functional text is exempt from bits. Nav items, button labels, form labels,
  headings' leading words, player announcements: literal, short, predictable.
- The flavor pattern for page headings is *literal title + Hope subtitle*:
  - "Episodes — Hope's complete record of grievances."
  - "Meet Maple Grove — the locals, catalogued for your protection."
  - "About — the man behind the coffee counter."
  - "Subscribe — never miss a refill."
- Alt text is descriptive first, funny second, and never *only* funny.
- The 404 page is in-world: Hope reporting that Fred wandered off with this page,
  with a link home and a link to Episodes. (Bones honest: `<h1>` = "Page not found",
  Hope's prose below it.)

## 4. Information architecture

Six destinations in the nav, in this order, identical on every page:

1. **Home** — `index.html`
2. **Episodes** — `episodes.html` (catalog) plus one page per episode at
   `episodes/df04-nut-jobs.html` (pattern: `df` + zero-padded number + slug;
   the special is `df12-13-booth-or-treat.html`)
3. **Meet Maple Grove** — `maple-grove.html`
4. **Jingle Jukebox** — `jukebox.html`
5. **About** — `about.html`
6. **Subscribe** — `subscribe.html`

Plus `feed.xml` (RSS), `404.html`, and `data/` (episodes.json, chapters, transcripts).

## 5. Page specifications

### 5.0 The wayfinding contract (every page, no exceptions)

Screen reader users navigate by structure and are rightly literal about it.
These guarantees hold on every page of the site so the mental map, once
learned, never breaks:

1. Exactly one `h1` per page, and it is the page's name.
2. The first two focusable elements are always, in this order:
   "Skip to main content" then "Jump to player" (both links).
3. One `nav` landmark labeled "Site", always the same six links in the same
   order: Home, Episodes, Meet Maple Grove, Jingle Jukebox, About, Subscribe.
4. One `main` landmark containing everything unique to the page.
5. The player is always the **last element in the DOM** — the end of the
   reading order on every page — and is a `region` landmark labeled
   "Dusty Farts player" whose first child is a heading, `h2` "Player", that is
   ALWAYS present in the DOM (visually hidden while the panel is collapsed to
   the bar). Consequence, worth stating because it's the site's best
   wayfinding trick: **pressing the headings key until you hear "Player"
   reaches the player in any screen reader** — so the letter H gets everyone
   to the player: sighted users as a hotkey, Browse Mode users as heading
   navigation. Hope says so in her welcome.
6. Heading levels never skip; every section of a page sits under an `h2`.
7. These structural names are exempt from in-world flavor (per section 3):
   "Player" is named "Player", not "The Booth".
8. Every page's footer carries the line: "Keyboard shortcuts: press ?
   (question mark) any time — it pauses the audio and lists every key." The
   promise Hope makes in audio must always also exist in text.

   **Status (2026-08-28):** removed from the footer at Brian's request — `?`
   only actually works once a screen reader is in focus mode (a control has
   focus), so "any time" was inaccurate and read as confusing from Browse
   Mode. The full shortcut list, including `?`, is still documented on the
   Subscribe page and inside the player's own "Keyboard shortcuts" panel.

### 5.1 Home

Exact reading order (DOM order — this is the spec, not a suggestion):

1. "Skip to main content" link, then "Jump to player" link (the contract).
2. Header with site name and the "Site" nav.
3. `main`, containing in order:
   a. `h1` "Dusty Farts" + tagline ("Two old friends, one booth, and enough
      coffee to fuel a small-town power grid.").
   b. The logo Polaroid (alt text describes the scene: John and Fred in a red
      vinyl diner booth beneath a neon Polyester Lounge sign, handwritten
      caption "Dusty — Farts — don't feed them after noon").
   c. `h2` "Welcome" → **button labeled "Play Hope's welcome (54 seconds)"**
      (adjust the number to the real clip length; the duration lives in the
      label so nobody presses play blind) → the same welcome as on-page text,
      two paragraphs in Hope's voice — the audio and the text say
      substantially the same thing, so deaf visitors and skimmers lose
      nothing.
   d. `h2` "Start listening" → **"Start with Episode 1"** primary action with
      one Hope line saying this is one unfolding story, not a pile of
      episodes → "Latest episode" card with its play button.
   e. `h2` "How to listen" → the three doors, stated literally, each line
      opening with its audience: "Keyboard: press H to open the player.
      Mouse: any play button, or the player bar at the bottom of the page.
      Screen reader: the player is the last region on every page, under the
      heading named 'Player' — press your headings key until you hear it, or
      use the 'Jump to player' link at the top of the page. And any time:
      press ? (question mark) to pause the audio and see every keyboard
      shortcut." Link to the
      fuller per-browser guide on the Subscribe page.
   f. `h2` "About the making" → the one-line craft note ("Written, scored,
      and produced entirely by ear — no screens were consulted in the making
      of this town.") linking to About.
4. Footer, then the player region — always last (the contract).

The welcome button plays a 30–60s audio clip recorded by Brian with the
ElevenLabs Hope voice (draft script in Appendix A — Brian approves/rewrites,
then records). Never autoplays. Implemented as a regular player invocation so
all player keys and announcements work during it. File:
`audio/hope-welcome.mp3` (128k, mono is fine). Until the file exists, the
button is simply absent (feature-flagged by its presence in episodes.json) and
the text welcome stands alone.

### 5.2 Episodes (catalog)

`h1`: "Episodes" + Hope subtitle. One list, newest first, each item an `article`
with: `h2` ("Episode 4: Nut Jobs"), art thumbnail (scene-describing alt), release
date, duration ("20 min"), chapter count, one-line Hope-voiced summary (adapted
from show notes), a **Play** button (opens the player at that episode) and a
**Details** link (to the episode page). A note at the top, in Hope's voice,
recommending newcomers start at Episode 1 — with a link.

### 5.3 Episode page

`h1`: "Episode 4: Nut Jobs" + date/duration line. Then in order: cover art
(scene alt text), **Play in the site player** button, native
`<audio controls preload="none">` element (the no-JavaScript path — with JS active,
hide it and rely on the player), **Download MP3** link with size ("18 MB"),
chapter list (each chapter a button: jumps the player to that chapter),
show notes content (Summary, Voices You'll Hear, Sound Stage — Brian's existing
copy from the show notes docx), then **Transcript** in a `<details>` element
(collapsed by default; `<summary>Transcript</summary>`), then previous/next
episode links.

Transcripts: adapted from `../Scripts/` per episode. Cleanup rules: keep speaker
names as `<strong>` labels; keep sound cues as bracketed stage directions
("[The Jiffy Lube door jingles]"); strip production notes, alternate takes,
engineering remarks, and anything not heard in the final audio; spot-check against
the audio where the script clearly diverged. Chapters from the audio become `h3`
subheadings inside the transcript where they align.

### 5.4 Meet Maple Grove

`h1` + Hope subtitle. Two `h2` sections: **The Locals** and **The Landmarks**.
Each local gets an `h3` and a short Hope-voiced portrait drawn from the character
sheet docx files: John "Dusty", Fred "Farts", Hope herself (writes her own entry,
naturally reluctant), Aria, Doctor Bobby, Doctor Fritz (Freudy), Curtis, Lyle,
Pearlie Fae, Grady, Suzy and Umie. Landmarks: the Polyester Lounge, the Jiffy
Lube, Doctor Bobby's Blood Bus, Maple Gump Park, Menards, the Maple Grove YMCA.
Spoiler-light: describe who people are, not what happens to them. Where an
episode introduced someone, link it ("first spotted in Episode 5").

### 5.5 Jingle Jukebox

`h1`: "Jingle Jukebox" + Hope subtitle ("all six jingles, plus the versions the
committee rejected."). Built from Episode 10's chapter cue points — each of the
nine chapters ("Original Jingle", "Jingle 1" … "Jingle 6, alternate version") is a
row with a play button that plays exactly that segment of `df10.mp3` (seek to
chapter start, pause at chapter end) through the site player, announced as
"Playing: Jingle 3, from the Jingle Jamboree." Also include the Holiday Theme and
New Year Jingle as entries pointing at the opening chapters of episodes 12/13 and
17 if their chapter data confirms clean boundaries (build-time check; drop
gracefully if not).

### 5.6 About

Brian's story, told properly and warmly, in third-person-Hope for flavor but
letting the facts lead: blind since 2014, former IT manager, teaches blind
students technology and screen readers; wrote, scored, engineered, and produced
every episode non-visually with Reaper, a screen reader, ElevenLabs, Suno, and
ChatGPT; started the show to make his family laugh. Link to
github.com/1eyebiney. (Ask Brian during build whether to link First Aid for the
Blind.) End with the show's credit line: "Written, scored, and produced by Brian
Clark — who had a screen reader, a microphone, and just enough diner-grade coffee
to pull this off."

### 5.7 Subscribe

Explains, plainly: the site player (press H; press ? any time to pause and
list every keyboard shortcut), the RSS feed URL in a copyable
read-only text field with a Copy button, and — once the feed is listed —
Apple Podcasts and Spotify links. Short Hope bit at the bottom. Also linked from
every page head via `<link rel="alternate" type="application/rss+xml">`.

## 6. The player — full specification

### 6.1 Architecture

One persistent player, continuous playback while browsing. Implementation:
a shared page shell where in-site navigation intercepts link clicks, fetches the
next page, swaps `<main>`, updates `document.title` and the History API, moves
focus to the new `h1` (tabindex="-1"), and announces the new page title through
the player's live region. The `<audio>` element lives outside `<main>` and is
never replaced. Full page loads must still work (progressive enhancement):
every page is a complete document; the swap layer is an optimization. No
framework; vanilla JS; target under ~300 lines for the swap layer.

### 6.2 Interaction model — no keyboard takeover, three doors in

**Hard rule: the site never takes over the keyboard.** No `role="application"`,
no page-wide focus trap, no key hijacking. (accessible-bible.org traps focus to
make single-letter keys work; that trade is wrong for a public website — it
steals quick-nav from Browse Mode users and forces mouse users onto the
keyboard.) In Browse Mode (NVDA browse mode / JAWS virtual cursor), single
letters belong to the screen reader — `H` is "next heading" and the page never
sees it. The design accepts this and gives each kind of user their own door:

- **Mouse users:** the player is a persistent, **non-modal panel** — a compact
  bar fixed at the bottom of every page (episode title, play/pause, position,
  "Expand player" button) that expands in place into the full player. Nothing
  overlays the page, nothing traps, clicking elsewhere never pauses playback.
- **Sighted keyboard users:** `H` toggles (expands + focuses / collapses) the
  player from anywhere; the full key map below is active whenever focus is
  inside the panel; `Tab` walks in and out freely; `Escape` collapses the panel
  and returns focus to where it was. When collapsed mid-playback, the bar
  remains.
- **Browse Mode screen reader users:** three honest paths, no mode-fighting.
  (1) The panel is a labeled `region` landmark with its own (visually hidden)
  heading, "Player" — so landmark quick-nav and, fittingly, the screen reader's
  own `H` key find it. (2) A **"Jump to player"** link sits immediately after
  the skip link on every page. (3) All controls are real buttons and native
  widgets, so arrowing onto them and pressing Enter just works; NVDA and JAWS
  switch to focus mode naturally on the slider and inputs, and the moment the
  user is in focus mode inside the panel, the exact same key map as everyone
  else applies. Additionally, the play/pause button carries
  `accesskey="p"` — modifier-based access keys (Alt+Shift+P in Firefox/NVDA
  setups, Alt+P in Chrome on Windows) pass through Browse Mode, giving
  play/pause from anywhere without leaving the virtual cursor. The Subscribe
  page's "How to listen" section documents all three doors per browser, and the
  panel's shortcuts disclosure repeats it.

Hardware media keys and phone lock screens work through the Media Session API
regardless of focus or mode (see 6.5).

**Status (2026-08-28):** a same-day attempt to move focus into the panel
automatically whenever a Play button was pressed (redirecting to the seek
slider, on the theory that a native form control triggers NVDA/JAWS's
automatic focus-mode switch) was built, then reverted after Brian tested it
live and found several controls not behaving as expected. On reflection,
Brian doesn't want focus moved at all: pressing any Play button anywhere on
the site (catalog, episode page, home, chapters, jukebox) starts or pauses
that audio and updates the player bar in place, full stop — it never moves
keyboard focus, whether the click came from a mouse, a keyboard Enter, or a
screen reader activating the button from Browse Mode. The three doors above
are otherwise unchanged and untouched; only `H` and the bar's "Expand player"
button move focus into the panel, exactly as this section already specified.

### 6.3 Keyboard map

Global, on every page (ignored when focus is in an input/textarea/select or when
a modifier is held):

- `H` — expand and focus the player panel (or collapse it if it has focus).
- `?` (Shift+/) — pause playback if playing, expand the player if collapsed,
  and open the **keyboard shortcuts list**, focusing its heading. `?` or
  `Escape` closes the list and returns focus to wherever it was. Playback
  does NOT auto-resume on close — the announcement says "Paused. Press Space
  to resume." (Hope promises this key in her recorded welcome; it is
  load-bearing.)

While focus is anywhere inside the player panel (`role="region"`, labeled
"Dusty Farts player" — NOT a modal, no focus trap):

- `Space` — play/pause.
- `Left` / `Right` — back / forward 10 seconds.
- `Shift+Left` / `Shift+Right` — back / forward 1 minute.
- `Ctrl+Left` / `Ctrl+Right` — back / forward 5 minutes.
- `Page Up` / `Page Down` — previous / next chapter (announced with title).
- `C` — reveal and focus the chapter list: a plain list of real buttons (one per
  chapter, labeled "Play chapter 3: Tales of Texting, 7 minutes 0 seconds"), NOT
  an ARIA listbox — plain buttons read naturally in Browse Mode too. Pressing a
  chapter's button plays it in place, closes the list, and never moves focus
  (status, 2026-08-28: focus previously jumped to the panel's play button on
  activation; per Brian, no player control should ever move focus). Pressing
  the same chapter's button again while it's playing pauses it instead of
  restarting it, and its label flips to "Pause chapter 3: ..." while it's the
  one playing — the same toggle-in-place behavior described in the status
  note after 6.2, extended here and to the Jingle Jukebox (5.5) so every Play
  control on the site behaves identically. The list is also always reachable
  by Tab and by the virtual cursor via its own disclosure button ("Chapters").
- `Up` / `Down` — previous / next episode (announced; playback starts at the
  episode's resume point if one exists, else the top). Exception: while focus
  is on the seek slider specifically, Up/Down are left alone entirely (status,
  2026-08-28) — a native `<input type="range">` already treats them as its own
  step keys, and NVDA was reported stealing that behavior for episode
  switching before this carve-out. Left/Right still seek 10 seconds there, as
  everywhere else in the panel.
- `Home` — restart the current episode.
- `?` — same as the global `?`: pause and open the shortcuts list.
- `Escape` — collapse the panel to the bar and return focus to where it was
  (playback continues; if the shortcuts list is open, Escape closes the list
  first).

Every key action is mirrored by a visible, focusable, labeled button in the
panel, in this order (status, 2026-08-28 — reordered at Brian's request for a
more logical screen-reader navigation sequence; wording and set unchanged):
Back 1 min, Back 10, Play/Pause (`accesskey="p"`), Forward 10, Forward 1 min,
Previous chapter, Next chapter, Chapters, Previous episode, Next episode,
Collapse. A `<input type="range">` progress slider (labeled
"Seek") is keyboard-operable and announces its value as time. Position shown as
text: "12:30 / 19:57". A visible "Keyboard shortcuts" disclosure inside the
panel documents the map and the three Browse Mode doors from 6.2.

### 6.4 Announcements (aria-live="polite", one region, rate-limited)

- Play: "Playing: Episode 4, Nut Jobs." Pause: "Paused at 12 minutes 30 seconds."
- Seek (all sizes): "12 minutes 40 seconds of 19 minutes 57 seconds."
- Chapter jump: "Chapter 3: Tales of Texting."
- Episode switch: "Episode 5: Blood Brothers. Press play to start it." (changed
  2026-08-28 from "Press Space to play" — the old wording was wrong on touch
  devices with no physical Space key; "press play" names the action instead of
  a key, and is accurate on desktop, mobile, and any assistive tech.)
- Episode end: "End of Episode 4. Next up: Episode 5, Blood Brothers." then
  auto-advance and play (the show is continuous; this is the default, with a
  player setting to turn auto-advance off, persisted in localStorage).

### 6.4a Starting playback (iOS constraint — do not undo this)

iOS Safari only permits `audio.play()` while the user's tap is still being
handled. Two rules follow, and breaking either makes the site silent on iPhone
while desktop Chrome keeps working (Chrome allows a later `play()` based on
prior engagement, which is why this hid for so long):

1. **Never defer `play()` behind an event or promise.** Until 2026-08-29
   `loadEpisode()` waited for `loadedmetadata` before playing. With
   `preload="none"` the element's `readyState` was always 0 at that point, so
   *every* play was deferred and iOS blocked *every* one — and the empty
   `.catch()` on each call meant it failed with no sound and no message. Play
   now starts synchronously; the start offset is applied afterwards (seek
   first, then play, whenever metadata is already available).
2. **Keep the path from tap to `play()` synchronous.** Public entry points use
   `withEpisodes()`, which runs its callback immediately when episode data is
   already cached (the normal case — `init()` fetches it on page load) and only
   falls back to a promise if a tap beats that fetch. A plain
   `fetchEpisodes().then()` on the tap path ends the gesture window even when
   the promise is already resolved.

Supporting these: `preload="metadata"` (with `"none"`, iOS would not load
metadata until a gesture-initiated play, while the play waited on metadata — a
deadlock); a silent-data-URI play/pause primed on the first interaction, so
playback the site starts later on its own (auto-advance, end of a jukebox
range, Media Session buttons) is still permitted; and `handlePlayError()`,
which announces a blocked play instead of swallowing it. `AbortError` stays
silent — it is the normal result of a new `load()` interrupting a play in
flight when switching episodes or jukebox tracks.

Related: `current` (what the bar is labelled with) and `loadedSlug` (what the
audio element actually has loaded) are separate. `init()` restores `current`
from localStorage without loading audio, so the "already playing this one"
check must consult `loadedSlug`; otherwise the first click after a reload calls
`play()` on an element with no source and silently does nothing.

### 6.5 State and media integration

- Resume: per-episode positions and the current episode id in localStorage;
  wrapped in try/catch; the site must work fully when storage is unavailable.
- Positions save on pause, on seek, every ~15s while playing, and on
  `visibilitychange`/`pagehide`.
- Media Session API: title, artist "Dusty Farts", per-episode artwork; hardware
  play/pause/seek/next-track/previous-track mapped to the same actions — so OS
  media keys and phone lock screens work.
- Chapters ship as build-time-extracted JSON (see 8.2); the player never parses
  ID3 in the browser.

## 7. Visual design — "the shoebox of photographs"

Brian is a former graphic designer; this section is specified in words precise
enough that he retains art direction without sight, and Sonnet implements
without inventing. The organizing idea: **the Polaroid is the design system.**
The logo photograph — two old men in a red vinyl booth, aged instant-film
warmth, handwritten caption — is not just artwork; its language (instant film,
handwriting, diner materials, one neon glow) generates every visual decision
on the site. The site should read as a shoebox of found photographs from
Maple Grove, not as produced media.

### 7.1 The Polaroid frame system

Every content image on the site is presented as a Polaroid:

- White frame (#FBF7EE — slightly warm white), classic proportions: side and
  top borders ~5% of image width; bottom border ~18% (the "fat" margin).
- Soft drop shadow (offset ~2px/4px, blur ~12px, warm dark brown at ~25%
  opacity — never pure black).
- Each Polaroid is rotated slightly: a deterministic pseudo-random rotation
  between −2.5° and +2.5° derived from the episode number (deterministic so
  it doesn't shift between visits; nth-child rotation classes are fine).
- Two strips of "masking tape" hold the top corners: small semi-transparent
  parallelograms (tiny inline SVG or CSS), cream-yellow (#E8DFC0 at ~75%).
- The fat bottom margin carries a handwritten caption in the script face
  (7.4): episode number and a short Hope-style line (e.g., "Ep. 4 — the
  squirrels were armed."). Captions are decorative duplicates
  (`aria-hidden="true"`); the accessible name of the image is its alt text,
  and all real information also exists as honest text.
- The photo itself gets a subtle instant-film treatment in CSS: slight
  desaturation (~92%), slight warm sepia tint, and a faint inner vignette.
  Cheap, uniform, and it visually unifies art that came from different
  generations of the show.

### 7.2 Palette (CSS custom properties, defined once)

Light ("daytime at the Lounge"):

- `--paper` #F2E8D5 (cream page background)
- `--ink` #3B2E25 (deep brown text)
- `--frame` #FBF7EE (Polaroid white)
- `--vinyl` #7E3B32 (booth burgundy — primary buttons, piping, links)
- `--teal` #5F7A72 (muted teal — secondary accents, visited/secondary UI)
- `--neon` #E2543E (red-orange — masthead neon + the playing indicator ONLY)
- `--wood-dark` #4A3527, `--wood-light` #6B4E36 (wood-grain gradient stops)
- `--tape` #E8DFC0

Dark ("after hours at the Lounge"): `--paper` #2A211B, `--ink` #EFE6D4,
Polaroid frames STAY light (#FBF7EE) — white-framed photos floating on a dark
room is the best moment of dark mode; `--vinyl` lightens to #A85B4F,
`--teal` to #7E9B92; the neon glows brighter (larger text-shadow radius).
All pairs must hold WCAG AA; verify derived shades at build time.

### 7.3 Signature moments (one per region of the page, and no more)

- **Masthead neon:** the site name "Dusty Farts" set in neon-script style —
  the script display face in `--neon` with a layered CSS text-shadow glow
  (two shadows: tight bright, wide soft) on the wood-paneled header strip.
  Static. (If `prefers-reduced-motion: no-preference`, one subtle flicker
  animation on first load only, under 1.5s, is permitted; never looping.)
- **Wood paneling:** header and footer are horizontal strips of dark wood
  grain (CSS gradient noise or a tiny tiling SVG, ≤2KB) — the diner
  wainscoting. Nav links sit on it like a letterboard menu: cream text,
  generous spacing.
- **Vinyl piping:** the section-divider motif — a 3px `--vinyl` rounded rule
  with a faint stitch pattern (dashed lighter line overlaid). Also the top
  edge of the player bar, so the player reads as booth upholstery.
- **The player bar as diner counter:** wood-grain face, cream buttons with
  pressed-in shadows (inset on :active) like tactile radio buttons, the
  neon dot as the playing indicator (steady when playing, dim when paused;
  never blinking).
- **Jingle Jukebox:** styled as a booth-side Seeburg Wall-O-Matic: each
  jingle is a flip-card-style track label (cream card, thin red rule top and
  bottom, track number in a circle) with one round mechanical play button.
  This page may lean harder into costume because it is a toy by nature.
- **Date stamps:** episode dates rendered like photo-processing stamps —
  small caps, letterspaced, in `--teal` (e.g., "AUG 15 2025") beside each
  Polaroid. Plain text, styled; screen readers just hear the date.
- **Coffee rings:** at most ONE faint coffee-ring stain per page (inline
  SVG circle-arc, `--ink` at ~6% opacity, aria-hidden), tucked behind a
  corner of `main`. The 404 page may have three; Fred was there.

### 7.4 Typography

- Display: **Fraunces** (or closest free equivalent) — the warm soft serif
  for h1/h2, echoing the cream serif on the covers. Self-hosted woff2.
- Script/handwriting: **Caveat** (or similar free casual script) — Polaroid
  captions and the neon masthead ONLY. Never for body or UI text.
- Body/UI: a high-readability face (system stack or self-hosted Source
  Serif/Sans), 18px+ base, 1.6 line-height, ~70ch measure.
- No external font CDNs at runtime; all fonts are files in the repo.

### 7.5 Restraint rules (the taste budget — build gate)

1. Per view: at most ONE ambient texture (paper speckle) + ONE signature
   moment beyond the persistent header/player treatments.
2. Neon appears in exactly two places sitewide: masthead, playing indicator.
3. Body text always sits on flat `--paper`/`--ink` — never on texture, wood,
   or photos.
4. Decorative elements are `aria-hidden="true"`, never focusable, never
   carry information, and never intercept clicks (pointer-events: none).
5. Focus outlines must remain visible on every treatment: 3px solid outline
   + 2px offset halo in the opposite-contrast color so it survives wood and
   vinyl backgrounds.
6. Total weight of all decorative assets (textures, tape, rings, wood):
   under 15KB combined, inline SVG or CSS only. No raster texture files.
7. `prefers-reduced-motion: reduce` disables the flicker and any transition
   longer than 150ms. Nothing ever loops or auto-animates.

### 7.6 Layout

Single column, max-width ~70ch for prose; the episode catalog is the "photo
wall": a responsive grid of Polaroid cards (1-up narrow, 2-up ~600px+,
3-up ~900px+), each card = Polaroid + date stamp + title + one-liner + Play
and Details. Fully responsive, no horizontal scrolling; the player bar never
obscures focused content (`scroll-padding-bottom` ≥ bar height + 16px).

### 7.7 Decorative assets to produce (build task, all as code)

Tiling wood-grain SVG (≤2KB), paper-speckle SVG (≤1KB), tape-strip SVG,
coffee-ring SVG, stitch-pattern divider, neon glow shadow recipe, film
treatment filter recipe. All authored as inline SVG/CSS in the stylesheet —
reviewable as text, which keeps them auditable by Brian with a screen reader.

## 8. Content pipeline

### 8.1 episodes.json extensions

`data/episodes.json` gains per episode: `webFile` ("audio/df04.mp3"),
`slug` ("df04-nut-jobs"), `summary` (Hope-voiced one-liner), `notesHtml` fields or
sidecar files for the show-notes sections, `artWeb` ("images/df04.jpg"),
`artAlt` (scene description), `chapters` (from 8.2), `transcript`
("data/transcripts/df04.html"). Show-level: `hopeWelcome`
("audio/hope-welcome.mp3", optional).

### 8.2 Chapter extraction (build step, run locally)

For every shipped MP3:
`ffprobe -v error -show_chapters -of json audio/dfNN.mp3` → normalize to
`[{"title": "Tales of Texting", "start": 420.181, "end": 600.0}]` (strip the
leading "N " numbering from titles; keep order) → embed into episodes.json.
Volumes 1 and 2 may lack chapters — the player must handle an episode with an
empty chapter list (chapter keys announce "No chapters in this episode").
Also verify: episode 10's chapters start at 213s (the jingles); the Jukebox uses
them as-is.

### 8.3 Transcripts

One HTML fragment per episode in `data/transcripts/`, produced by the cleanup
pass over `../Scripts/` per the rules in 5.3. These are hand-reviewed content,
not throwaway generation: Sonnet drafts, Brian spot-listens where unsure.

## 9. RSS feed

As specified in HANDOFF.md Phase 2 (RSS 2.0 + iTunes tags, generator script in
`tools/make_feed.py`), with one addition: Podcasting 2.0 chapters. For each
episode also emit `data/chapters/dfNN.json` in the podcast-namespace JSON chapters
format and reference it from the feed item as
`<podcast:chapters url="…" type="application/json+chapters"/>` (declare the
`podcast` namespace). Apple/Spotify ignore it harmlessly; chapter-aware apps get
real chapters. Feed items link to episode pages; `itunes:explicit` false;
dates per episodes.json after Brian confirms the table.

## 10. Accessibility acceptance criteria (build gate)

Everything in HANDOFF.md Phase 4, plus: **no keyboard takeover anywhere** —
verify no `role="application"`, no focus trap, and that Browse Mode quick-nav
(H for headings, B for buttons, D/R for landmarks) works normally on every page
with the player present; player fully operable three ways: (a) mouse only,
(b) keyboard only via H and the key map, (c) Browse Mode only via the
jump-to-player link, landmark, and real buttons — each tested end to end;
access key on play/pause verified in Chrome and Firefox with NVDA running;
`?` verified to pause, open the shortcuts list, close cleanly, and never
auto-resume — tested as sighted-keyboard global key and from focus mode
inside the panel; the footer shortcuts line present on every page;
every announcement in 6.4 verified with NVDA;
transcripts reachable and readable in browse mode; the fetch-swap navigation
moves focus to the new `h1` and announces the page (test back/forward buttons
too); site fully usable with JavaScript disabled (native audio, full page
loads); dark mode contrast re-checked; player bar does not trap or obscure
focus; `prefers-reduced-motion` honored.

## 11. Decisions resolved (2026-08-28) and the one open item

1. Repo name: **dusty-farts** — confirmed. Site: https://1eyebiney.github.io/dusty-farts/
2. Custom domain: **none** — ship on the GitHub URL and submit the feed there.
3. Release dates: **confirmed by Brian** — use episodes.json as-is.
4. About links to First Aid for the Blind: **yes** — get the exact URL from
   Brian during the build (do not guess it), alongside github.com/1eyebiney.
5. Hope welcome recording: Brian is recording it (script in Appendix A). When
   `audio/hope-welcome.mp3` exists, enable the welcome button; re-encode to
   128k if his export differs.

Remaining question budget for the build: the FAFTB URL, transcript
spot-checks, and anything this document genuinely does not answer. Everything
above is settled.

## Appendix A — Hope's welcome, FINAL (Brian's recorded text, verbatim)

This is the script as Brian edited and recorded it. It is canonical: every
navigational fact Hope states is guaranteed by the wayfinding contract (5.0)
and the `?` shortcuts key (6.3). If any label, key, or structure changes, the
recording must be redone — Hope never gives stale directions. Ellipses are
Brian's pacing marks for the ElevenLabs read.

> Oh. Hello. You found it.
> Welcome to the official home of Dusty Farts — and no, that name was not my
> idea. ...
> I'm Hope. I narrate the ongoing situation that is John and Fred: two old
> friends, one rescued diner booth, and opinions nobody ordered. ... ...
> Now, directions, because I'm told people get lost around here, and I refuse
> to be blamed for it....
> The episode player lives at the very end of every page, in its own little
> area, under a heading named "Player." ...
> If you're running a screen reader, press H, your headings key, until you
> hear "Player," and you're there. ...
> When the audio is playing, Space bar plays and pauses while the arrow keys
> move you forward or back a little.
> Question mark pauses audio and brings up a list of keyboard shortcuts. ...
> If you're new, start with Episode One. ...
> This is a story, not a pile of episodes, and things in Maple Grove have a
> way of... escalating. ...
> The coffee's burnt, the booth is cracked, and the boys are already arguing.
> ... ...
> Come on in!

---

*This document was designed collaboratively with Brian (Fable session, August
2026). Build questions that this document doesn't answer: prefer asking Brian
over inventing, and prefer the simpler implementation over the cleverer one.*
