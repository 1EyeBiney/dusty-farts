# Dusty Farts Website — Project Instructions

## Who you're working with

Brian Clark is the writer, producer, and audio engineer of Dusty Farts, an immersive
comedy fiction podcast set in the small town of Maple Grove. Brian is totally blind
(since 2014), works keyboard-only with the NVDA screen reader, and never uses a mouse.
He is highly technical — former IT manager, teaches screen readers (NVDA and JAWS)
professionally, GitHub username `1EyeBiney`.

Consequences for you:

- Everything you build MUST be fully operable by keyboard alone and correct under a
  screen reader. This is not an enhancement; it is the acceptance criterion.
- When you describe visual output (pages, images, layouts), describe it in words —
  Brian cannot glance at a screenshot.
- Prefer semantic HTML over ARIA bolt-ons. Real `<button>`, real headings in order,
  real landmarks, labeled controls, visible focus indicators.
- Brian reviews changes by listening. Keep diffs and explanations clear and narrated.

## Hard rules

1. **This folder (`website/`) is the entire Git repository.** `git init` here and only
   here. NEVER initialize or add files from the parent `Dusty Farts` folder — it holds
   private working material (scripts, Reaper projects, character sheets, full-quality
   renders, huge MP4s) that must never reach GitHub.
2. **Only 128kbps MP3s go in the repo.** Never copy the full-bitrate renders or
   anything from `.render/MP4/` into this folder. Target repo size ~250MB.
3. Do not modify anything in the parent folder except when asked; treat it as
   read-only source material.
4. The RSS feed sets `itunes:explicit` to false — the show is crude-humor clean, no
   profanity tagging needed.
5. `data/episodes.json` is the single source of truth for episode metadata. Site pages
   and the RSS feed must both be generated from / consistent with it.

## Where source material lives (parent folder, relative to here)

- `../.render/Lower BitRate/` — 128kbps episode MP3s (the web/streaming versions).
  If any episode is missing here, re-encode from the full-quality file in `../.render/`
  with: `ffmpeg -i SRC -codec:a libmp3lame -b:a 128k -ar 44100 -map_metadata 0 -id3v2_version 3 DEST`
- `../.render/` — full-quality MP3s (source of truth for audio; do not commit).
- `../Podcast work/images/` — all cover art. Per-episode compressed JPGs (patterns like
  `NN Title Art (1400 by 1400) at 80.jpg`) plus full PNGs. The show logo is
  `Dusty Farts Logo 1400 by 1400 at 80 percent.jpg` (sepia Polaroid of John and Fred in
  their diner booth).
- `../Podcast work/Show Notes/` — one docx per episode with summary, voice cast, sound
  stage, and credits. Extract text with python-docx or pandoc; this is the source for
  episode page copy and RSS item descriptions.
- `../Podcast work/Facebook Posts/` — promo copy per episode; filenames of the first
  five carry the true 2025 release dates.
- `../Dusty Farts tracker.xlsx` — episode metadata spreadsheet (locations, characters,
  plotlines). Some release dates in it are wrong (say 2026); trust
  `data/episodes.json` instead.
- `../.character sheet *.docx`, `../Grady character sheet.docx`, `../.Running Gags.xlsx`,
  `../.DF pearls of wisdom.docx` — source material for the "Meet Maple Grove"
  characters/world page.
- `../Scripts/` — full episode scripts (context only; never publish scripts).

## Decisions already made with Brian (do not re-ask)

- Hosting: GitHub Pages, public repo github.com/1EyeBiney/dusty-farts (name
  CONFIRMED — do not re-ask). No custom domain; the feed lives on the GitHub URL.
- Site streams and serves ONLY the 128kbps files.
- RSS feed: yes, podcast-standard RSS 2.0 + iTunes tags, not explicit, author Brian
  Clark, contact email 1eyebiney@gmail.com (Brian knows this becomes public).
- Release dates: the dates in `data/episodes.json` are CONFIRMED by Brian — use as-is.
- Episode 15 (Chatty Tarts) and 18 (Goats Revisited): excluded for now.
- MP4 video versions: not published for now (no YouTube yet).
- Canonical audio for the Halloween special is the file containing
  "Booth or Treat - The Maple Grove Spooktacular Special" (not the "A Maple Grove"
  near-duplicate).
- Player interaction model is borrowed from Brian's accessible-bible.org project:
  pressing H opens an in-page media player; see HANDOFF.md for the full spec.

## Local preview

Never preview with a plain static server (`python -m http.server` and
similar) - it doesn't support HTTP Range requests, which the `<audio>`
element needs to seek inside an episode file. Without Range support,
play/pause and switching episodes look fine but every seek-dependent control
(10s/1min buttons, chapter jump, the chapter list, the Jukebox) silently
fails, which cost a long, confusing debugging detour on 2026-08-28 before the
real cause (the server, not the code) was found. Use `tools/serve.py`
instead (`python tools/serve.py`, defaults to port 8000) - it adds real
Range support plus no-cache headers so a reload always reflects what's
actually on disk. There's also a `.claude/launch.json` entry
("dusty-farts-preview") wired to the same script for the preview-server
tool, so a fresh session should be able to start it by name rather than
reaching for `http.server` again.

## Style

- The show's visual identity: muted, faded-1970s Americana photorealism, large cream
  serif lettering (see the logo and episode art). Site design should feel like the
  covers: warm creams and browns, diner vibes, high contrast text, never busy.
- Tone of site copy: the show's own voice — dry, warm, a little absurd. Show notes
  docs are the best reference.
