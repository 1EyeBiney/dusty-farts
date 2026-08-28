# Dusty Farts Website — Build Plan (Handoff)

Read CLAUDE.md first, then DESIGN.md. **DESIGN.md is the authoritative
specification** for everything the site is and does — pages, player, voice,
visual design, content pipeline, acceptance criteria. This file remains the
ordered build checklist; where it sketches something DESIGN.md specifies in
full (the player, page content, seeking keys), DESIGN.md wins.

This file is the ordered build plan. Work through the phases;
check with Brian at the two marked confirmation points and before anything
irreversible (repo creation, first push, feed publication).

## Phase 0 — Assemble assets into this folder

1. Create `audio/`, `images/`, `css/`, `js/`, `episodes/` subfolders.
2. Copy the 128kbps MP3s into `audio/`. Nine already exist in
   `../.render/Lower BitRate/` (volumes 1–8 and 14). Re-encode any that are missing
   (9, 10, 11, 12and13, 16, 17 — unless Brian already saved them there from our
   earlier session) from `../.render/` using the ffmpeg line in CLAUDE.md.
   Rename copies to simple web-safe names: `df01.mp3` … `df17.mp3` (`df12-13.mp3`
   for the special). Keep a mapping in data/episodes.json (add a `webFile` field).
3. Copy each episode's compressed JPG art (listed in `data/episodes.json`) into
   `images/`, renamed to match: `df01.jpg` … `df17.jpg`, plus the logo as
   `logo.jpg`. Do not copy the multi-megabyte PNG masters.
4. Extract text from every show notes docx (`../Podcast work/Show Notes/`) with
   python-docx; store per-episode summaries and cast lists into
   `data/episodes.json` (add `summary` and `voices` fields). Keep the writing as-is —
   it's Brian's copy.
5. Run ffprobe on the two audio files with `durationSeconds: null` in
   `data/episodes.json` and fill in exact values; verify byte sizes of every file
   actually placed in `audio/` and update `bytes128k` to match the shipped files.

## Phase 1 — The site (plain static HTML, no framework, no build step)

Pages, all sharing one stylesheet `css/site.css` and one script `js/player.js`:

- `index.html` — Home. Logo image (alt text: describe the Polaroid: John and Fred in
  a red vinyl diner booth under a neon "Polyester Lounge" sign, captioned "Dusty —
  Farts — Don't feed them after noon"), the show description, a "Start with Episode 1"
  call-to-action (the series is one unfolding story), latest episode, and a short
  "How to listen: press H anywhere to open the player" note.
- `episodes.html` — full catalog, newest first, each entry: art thumbnail (meaningful
  alt text), title, episode number, date, duration, one-line summary, link to the
  episode page, and a "Play" button that opens the player at that episode.
- `episodes/dfNN-title-slug.html` — one page per episode: full show notes content
  (summary, Voices You'll Hear, Sound Stage), native `<audio controls>` element with
  the episode file (this is the no-JS/fallback path), download link to the MP3, and
  prev/next episode links.
- `maple-grove.html` — "Meet Maple Grove": the cast (John "Dusty", Fred "Farts",
  Hope the narrator, Aria, Doctor Bobby, Doctor Fritz, Curtis, Lyle, Suzy and Umie,
  Grady…) drawn from the character sheet docx files in the parent folder, plus the
  recurring locations (Polyester Lounge, Jiffy Lube, Doctor Bobby's Blood Bus,
  Maple Gump Park, Menards, the YMCA). Keep it spoiler-light.
- `about.html` — Brian's story: written, scored, and produced entirely non-visually
  using a screen reader, Reaper, ElevenLabs, Suno, and ChatGPT; link to
  github.com/1eyebiney and to First Aid for the Blind if Brian wants (ask him).
- `feed.xml` — see Phase 2.

### The player (js/player.js) — spec

Modeled on Brian's accessible-bible.org player. Behavior:

- Pressing `H` anywhere (except inside form fields) opens the player as a modal
  dialog (`role="dialog"`, `aria-modal="true"`, labeled "Dusty Farts player",
  focus moved into it, focus trapped, restored on close).
- Inside the player: `Space` play/pause, `Left`/`Right` seek −/+10 seconds,
  `Up`/`Down` previous/next episode, `Escape` closes. `Home` restarts the episode.
- All controls are also real buttons (Play/Pause, Back 10, Forward 10, Previous,
  Next, Close) so the keyboard model is discoverable; each has an accessible name.
- A live region (`aria-live="polite"`) announces state changes: "Playing: Episode 4,
  Nut Jobs", "Paused", "Moved to 12 minutes 30 seconds of 19 minutes".
- Position and episode remembered in a JS variable and localStorage
  (localStorage works on GitHub Pages), so returning listeners resume.
- When an episode ends, auto-advance to the next (announce it) — the show is a
  continuous story.
- Progress: a `<input type="range">` slider bound to currentTime, labeled, operable
  by arrow keys when focused; time shown as text ("12:30 / 19:57"), not only color.
- The key handler must ignore keystrokes with modifiers and anything typed into
  inputs, and must not conflict with NVDA browse-mode single-letter navigation more
  than necessary: document clearly that H is the hotkey and that NVDA users in
  browse mode should use focus mode or the on-page "Open player" button
  (also provide that visible button in the header of every page).

### Accessibility checklist (acceptance criteria)

- Single `h1` per page; heading levels never skip.
- Landmarks: `header`, `nav` (labeled), `main`, `footer`.
- Skip link as first focusable element.
- All images: meaningful alt text describing the scene (Brian will listen to these;
  write them like miniature scene descriptions, not filenames).
- Contrast at least WCAG AA on the cream/brown palette; visible focus outline
  everywhere.
- Every page fully navigable and operable with keyboard only; test tab order.
- `<html lang="en">`, page titles unique ("Episode 4: Nut Jobs — Dusty Farts").
- Site works with JavaScript disabled (native audio elements on episode pages).

## Phase 2 — RSS feed (`feed.xml`)

RSS 2.0 with iTunes namespace, generated from `data/episodes.json` (write a small
Python generator script `tools/make_feed.py` into the repo so regenerating is one
command). Channel: title Dusty Farts; link = site URL; language en-us;
`itunes:author` Brian Clark; `itunes:owner` with the email from episodes.json;
`itunes:image` = absolute URL of `images/logo.jpg`; `itunes:category` Fiction →
Comedy Fiction; `itunes:explicit` false; description from episodes.json; episodes as
items newest-first with: title ("Episode 4: Nut Jobs"; the special titled as parts 12
and 13), enclosure (absolute URL, exact byte length, `audio/mpeg`), `guid` (the
episode's absolute URL, isPermaLink true), `pubDate` (RFC 2822, from releaseDate, use
12:00:00 -0500), `itunes:duration` (seconds), `itunes:episode` number,
`itunes:image` per-episode art, description from the episode summary.

Dates and feed settings are CONFIRMED by Brian (2026-08-28); build the feed from
episodes.json as-is.

Validate with https://podba.se/validate/ or https://castfeedvalidator.com/ after the
site is live. Then give Brian the submission links (he submits himself):
Apple Podcasts Connect (podcastsconnect.apple.com) and Spotify for Creators
(creators.spotify.com); both just need the feed URL.

## Phase 3 — Git and GitHub Pages

Repo name CONFIRMED: `dusty-farts` (no re-ask needed).

1. `git init` in THIS folder only. `.gitignore`: `Thumbs.db`, `desktop.ini`, `*.tmp`,
   any scratch dirs.
2. Verify with `git status` that nothing outside this folder is visible before the
   first add.
3. `gh auth status` (run `gh auth login` with Brian if needed — device-code flow is
   screen-reader friendly). Then `gh repo create dusty-farts --public --source=. --push`.
4. Enable Pages from the main branch root (`gh api` or walk Brian through Settings →
   Pages). Site lands at https://1eyebiney.github.io/dusty-farts/.
5. Replace `siteUrlPlaceholder` usages with the real URL, regenerate feed.xml,
   commit, push.
6. Add the feed URL to the site header as a "Subscribe" link (`<link rel="alternate"
   type="application/rss+xml">` in every head, plus a visible Subscribe page/section
   explaining podcast apps).

## Phase 4 — Verification (do not skip)

- Keyboard-only pass over every page: tab order, skip link, player hotkeys,
  focus trap and restore.
- Have Brian do an NVDA pass; fix what he flags.
- Check every audio file plays on the live site (spot-check first/last seconds).
- Feed through a validator; fix until clean.
- Lighthouse accessibility run; investigate anything under ~100.
- `git status` one final time to prove no parent-folder files ever entered the repo.

## Out of scope for now (decided)

Chatty Tarts (ep 15) section, episode 18, YouTube/MP4 embeds, custom domain
(revisit later — Pages supports adding one without breaking existing URLs; the feed
URL would change, so if Brian is leaning toward a domain, decide BEFORE submitting
the feed to directories).
