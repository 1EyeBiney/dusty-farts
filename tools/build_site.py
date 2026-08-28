#!/usr/bin/env python3
"""Generate every static HTML page for the Dusty Farts site from
data/episodes.json (+ sidecar show notes / transcripts) and the
hand-authored copy in tools/site_content.py.

This is a build-time generator only - the SHIPPED site is plain static
HTML/CSS/JS with no framework and no build step to view (DESIGN.md 6.1 /
HANDOFF.md Phase 1). Re-run this script whenever episodes.json or the page
templates change: python tools/build_site.py

The generator exists (rather than hand-writing 15+ nearly-identical pages)
so the wayfinding contract in DESIGN.md 5.0 - one h1, skip links, the nav,
the player region as the last element in the DOM - is guaranteed identical
on every page instead of drifting by hand.
"""
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from site_content import CAST, LANDMARKS  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

NAV_ITEMS = [
    ("Home", "index.html"),
    ("Episodes", "episodes.html"),
    ("Meet Maple Grove", "maple-grove.html"),
    ("Jingle Jukebox", "jukebox.html"),
    ("About", "about.html"),
    ("Subscribe", "subscribe.html"),
]

SITE_URL = "https://1eyebiney.github.io/dusty-farts/"


def e(text):
    """Escape text for HTML body context."""
    return html.escape(str(text), quote=False)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def fmt_duration(seconds):
    seconds = int(round(seconds))
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h} hr {m} min"
    return f"{m} min"


MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June", "July",
    "August", "September", "October", "November", "December",
]


def fmt_date(iso):
    # 2025-08-15 -> August 15, 2025 (avoids strftime's non-portable no-pad-day flag)
    import datetime
    d = datetime.date.fromisoformat(iso)
    return f"{MONTH_NAMES[d.month - 1]} {d.day}, {d.year}"


def fmt_duration_words(seconds):
    seconds = int(round(seconds))
    m, s = divmod(seconds, 60)
    parts = []
    if m:
        parts.append(f"{m} minute" + ("" if m == 1 else "s"))
    parts.append(f"{s} second" + ("" if s == 1 else "s"))
    return " ".join(parts)


def fmt_bytes(n):
    mb = n / (1024 * 1024)
    return f"{mb:.0f} MB"


PLAYER_SHORTCUTS = [
    ("H", "Expand and focus the player (or collapse it, from inside)."),
    ("? (question mark)", "Pause, and open or close this shortcuts list."),
    ("Space", "Play or pause."),
    ("Left / Right arrow", "Back or forward 10 seconds."),
    ("Shift + Left / Right", "Back or forward 1 minute."),
    ("Ctrl + Left / Right", "Back or forward 5 minutes."),
    ("Page Up / Page Down", "Previous or next chapter."),
    ("C", "Open the chapter list."),
    ("Up / Down arrow", "Previous or next episode."),
    ("Home", "Restart the current episode."),
    ("Escape", "Collapse the player and return focus to where it was."),
]


def player_region_html():
    shortcuts_dl = "\n".join(
        f"        <dt>{e(k)}</dt>\n        <dd>{e(v)}</dd>" for k, v in PLAYER_SHORTCUTS
    )
    return f"""
  <div class="player-region" id="df-player" data-expanded="false" data-playing="false">
    <div class="player-bar" id="df-player-bar">
      <span class="player-dot" id="df-player-dot" aria-hidden="true"></span>
      <span class="player-bar-title" id="df-player-bar-title">Nothing playing yet</span>
      <div class="player-bar-controls">
        <button type="button" class="player-icon-btn" data-action="playpause" aria-label="Play" accesskey="p">&#9654;</button>
        <button type="button" class="player-icon-btn" data-action="expand" aria-label="Expand player">&#9650;</button>
      </div>
    </div>
    <div class="player-panel" id="df-player-panel" role="region" aria-label="Dusty Farts player">
      <h2 tabindex="-1">Player</h2>
      <p class="player-now-playing" id="df-player-nowplaying">Nothing playing yet</p>
      <p class="player-time"><span id="df-player-time">0:00 / 0:00</span></p>
      <input type="range" class="player-seek" id="df-player-seek" min="0" max="0" value="0" aria-label="Seek">
      <div class="player-transport">
        <button type="button" class="player-icon-btn" data-action="back60">&#8592; 1 min</button>
        <button type="button" class="player-icon-btn" data-action="back10">&#8592; 10s</button>
        <button type="button" class="player-icon-btn" data-action="playpause" aria-label="Play">&#9654; Play</button>
        <button type="button" class="player-icon-btn" data-action="fwd10">10s &#8594;</button>
        <button type="button" class="player-icon-btn" data-action="fwd60">1 min &#8594;</button>
        <button type="button" class="player-icon-btn" data-action="prevchapter">Previous chapter</button>
        <button type="button" class="player-icon-btn" data-action="nextchapter">Next chapter</button>
        <button type="button" class="player-icon-btn" data-action="chapters">Chapters</button>
        <button type="button" class="player-icon-btn" data-action="prevepisode">Previous episode</button>
        <button type="button" class="player-icon-btn" data-action="nextepisode">Next episode</button>
        <button type="button" class="player-icon-btn" data-action="shortcuts">Keyboard shortcuts</button>
        <button type="button" class="player-icon-btn" data-action="collapse">Collapse</button>
      </div>
      <div class="player-settings">
        <input type="checkbox" id="player-autoadvance" checked>
        <label for="player-autoadvance">Auto-advance to next episode</label>
      </div>
      <div class="player-chapters" id="df-player-chapters" hidden>
        <h3 tabindex="-1">Chapters</h3>
        <ul id="df-player-chapters-list"></ul>
      </div>
      <div class="player-shortcuts" id="df-player-shortcuts" hidden>
        <h3 tabindex="-1">Keyboard shortcuts</h3>
        <dl>
{shortcuts_dl}
        </dl>
        <button type="button" class="btn btn-quiet" data-action="shortcuts">Close</button>
      </div>
    </div>
    <div class="player-live-region" id="df-player-live" aria-live="polite" aria-atomic="true"></div>
  </div>""".strip("\n")


def page_shell(*, root, title, description, active_href, main_html, extra_head=""):
    nav_links = []
    for label, href in NAV_ITEMS:
        current = ' aria-current="page"' if href == active_href else ""
        nav_links.append(f'<li><a href="{root}{href}"{current}>{e(label)}</a></li>')
    nav_html = "\n            ".join(nav_links)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<link rel="stylesheet" href="{root}css/site.css">
<link rel="alternate" type="application/rss+xml" title="Dusty Farts" href="{root}feed.xml">
<script>window.SITE_BASE = "{root}";</script>
{extra_head}</head>
<body>
<div class="paper-speckle" aria-hidden="true"></div>
<div class="skip-links">
<a href="#main">Skip to main content</a>
<a href="#df-player">Jump to player</a>
</div>
<header class="site-header">
  <div class="site-header-inner">
    <a class="site-title-link" href="{root}index.html"><p class="site-title">Dusty Farts</p></a>
    <nav class="site-nav" aria-label="Site">
      <ul>
            {nav_html}
      </ul>
    </nav>
  </div>
</header>
<main id="main">
{main_html}
</main>
<footer class="site-footer">
  <div class="site-footer-inner">
    <p>Dusty Farts — an immersive comedy podcast from Maple Grove.</p>
    <p><a href="{root}feed.xml">RSS feed</a> · <a href="https://github.com/1eyebiney">Brian on GitHub</a></p>
  </div>
</footer>
<script src="{root}js/player.js" defer></script>
<script src="{root}js/site.js" defer></script>
{player_region_html()}
</body>
</html>
"""


def polaroid(art_web, alt, caption, tilt_seed, root):
    tilt = tilt_seed % 6
    return (
        f'<div class="polaroid" data-tilt="{tilt}">'
        f'<img src="{root}{art_web}" alt="{e(alt)}" loading="lazy">'
        f'<p class="polaroid-caption" aria-hidden="true">{e(caption)}</p>'
        f"</div>"
    )


# ---------------------------------------------------------------------------
# Page builders
# ---------------------------------------------------------------------------

def build_index(show, episodes, root="", out=None):
    latest = episodes[-1]
    welcome_seconds = 76  # measured: audio/hope-welcome.mp3 is 75.5s
    welcome_btn = ""
    if show.get("hopeWelcome"):
        welcome_btn = (
            f'<button type="button" class="btn" '
            f'onclick="window.DustyPlayer.play(\'hope-welcome\')">'
            f"Play Hope’s welcome (1 minute 16 seconds)</button>"
        )

    main = f"""
<h1>Dusty Farts</h1>
<p class="tagline">Two old friends, one booth, and enough coffee to fuel a small-town power grid.</p>

{polaroid('images/logo.jpg', show['logoAlt'], 'Dusty — Farts', 1, root)}

<h2>Welcome</h2>
{welcome_btn}
<p>Oh. Hello. You found it. Welcome to the official home of Dusty Farts — and no, that name
was not my idea. I’m Hope. I narrate the ongoing situation that is John and Fred: two old
friends, one rescued diner booth, and opinions nobody ordered.</p>
<p>If you’re new, start with Episode One — this is a story, not a pile of episodes, and
things in Maple Grove have a way of escalating. The coffee’s burnt, the booth is cracked,
and the boys are already arguing. Come on in.</p>

<h2>Start listening</h2>
<p>Dusty Farts is one unfolding story, not a shelf of standalone episodes — start at the
beginning and let it run.</p>
<p><a class="btn" href="{root}episodes/{episodes[0]['slug']}.html">Start with Episode 1</a></p>
<h3>Latest episode</h3>
<div class="episode-card">
  {polaroid(latest['artWeb'], latest['artAlt'], f"Ep. {latest['number']} — {latest['summary'][:40]}…", latest['number'], root)}
  <p class="date-stamp">{e(fmt_date(latest['releaseDate']))}</p>
  <h3><a href="{root}episodes/{latest['slug']}.html">Episode {latest['number']}: {e(latest['title'])}</a></h3>
  <p>{e(latest['summary'])}</p>
  <div class="episode-actions">
    <button type="button" class="btn" data-episode-slug="{latest['slug']}" onclick="window.DustyPlayer.togglePlayFor('{latest['slug']}')">Play</button>
    <a class="btn btn-secondary" href="{root}episodes/{latest['slug']}.html">Details</a>
  </div>
</div>

<h2>How to listen</h2>
<p>Keyboard: press H to open the player.</p>
<p>Mouse or touch: any Play button, or the player bar at the bottom of the page.</p>
<p>Screen reader: the player is the last region on every page, under a heading named
“Player.” On a phone, find it with your rotor or swipe navigation. On a desktop, use the
“Jump to player” link right after the skip link, then use the audio control buttons
located in the player region — not the headings key, since that's just normal heading
navigation for you, not anything special. See the
<a href="{root}subscribe.html">Subscribe page</a> for the full shortcut list.</p>

<h2>About the making</h2>
<p>Written, scored, and produced entirely by ear — no screens were consulted in the making
of this town. <a href="{root}about.html">Read the story behind the show</a>.</p>
""".strip("\n")

    html_doc = page_shell(
        root=root,
        title="Dusty Farts — an immersive comedy podcast",
        description=show["description"],
        active_href="index.html",
        main_html=main,
    )
    (ROOT / "index.html").write_text(html_doc, encoding="utf-8")


def build_episodes_catalog(show, episodes, root="", out=None):
    cards = []
    for ep in reversed(episodes):
        caption = f"Ep. {ep['number']} — {ep['title']}"
        cards.append(f"""
  <li class="episode-card">
    {polaroid(ep['artWeb'], ep['artAlt'], caption, ep['number'], root)}
    <p class="date-stamp">{e(fmt_date(ep['releaseDate']))} · {e(fmt_duration(ep['durationSeconds']))}{' · ' + str(len(ep['chapters'])) + ' chapters' if ep['chapters'] else ''}</p>
    <h2><a href="{root}episodes/{ep['slug']}.html">Episode {ep['number']}: {e(ep['title'])}</a></h2>
    <p>{e(ep['summary'])}</p>
    <div class="episode-actions">
      <button type="button" class="btn" data-episode-slug="{ep['slug']}" onclick="window.DustyPlayer.togglePlayFor('{ep['slug']}')">Play</button>
      <a class="btn btn-secondary" href="{root}episodes/{ep['slug']}.html">Details</a>
    </div>
  </li>""")
    main = f"""
<h1>Episodes</h1>
<p class="subtitle">Hope's complete record of grievances.</p>
<p>New around here? Start with <a href="{root}episodes/{episodes[0]['slug']}.html">Episode 1</a> —
Dusty Farts is one continuous story, told in order.</p>
<ul class="episode-grid">{''.join(cards)}
</ul>
""".strip("\n")
    html_doc = page_shell(
        root=root,
        title="Episodes — Dusty Farts",
        description="Every episode of Dusty Farts, newest first.",
        active_href="episodes.html",
        main_html=main,
    )
    (ROOT / "episodes.html").write_text(html_doc, encoding="utf-8")


def build_episode_page(show, episodes, index, root="../"):
    ep = episodes[index]
    prev_ep = episodes[index - 1] if index > 0 else None
    next_ep = episodes[index + 1] if index < len(episodes) - 1 else None

    notes_path = DATA / "shownotes" / ep["webFile"].split("/")[-1].replace(".mp3", ".json")
    notes = load_json(notes_path) if notes_path.exists() else None

    transcript_path = ROOT / ep["transcript"]
    transcript_html = transcript_path.read_text(encoding="utf-8") if transcript_path.exists() else "<p>Transcript coming soon.</p>"
    # strip the leading build-note HTML comment from the public page; it's for reviewers, in the source file
    if transcript_html.lstrip().startswith("<!--"):
        end = transcript_html.find("-->")
        transcript_html = transcript_html[end + 3:].lstrip("\n")

    chapters_html = ""
    if ep["chapters"]:
        items = []
        for i, ch in enumerate(ep["chapters"]):
            dur = fmt_duration_words(ch["end"] - ch["start"])
            items.append(
                f'<li><button type="button" class="btn btn-quiet" '
                f"onclick=\"window.DustyPlayer.playChapter('{ep['slug']}', {i})\">"
                f"Chapter {i + 1}: {e(ch['title'])}, {e(dur)}</button></li>"
            )
        chapters_html = f'<h2>Chapters</h2>\n<ul class="chapter-list">{"".join(items)}</ul>'

    notes_html = ""
    if notes:
        if notes["summary"]:
            notes_html += "<h2>Summary</h2>\n" + "".join(f"<p>{e(p)}</p>" for p in notes["summary"])
        if notes["voices"]:
            items = "".join(f"<li>{e(v)}</li>" for v in notes["voices"])
            notes_html += f"<h2>Voices You’ll Hear</h2>\n<ul>{items}</ul>"
        if notes["soundStage"]:
            items = "".join(f"<li>{e(v)}</li>" for v in notes["soundStage"])
            notes_html += f"<h2>Sound Stage</h2>\n<ul>{items}</ul>"

    pager = '<div class="episode-pager">'
    if prev_ep:
        pager += f'<a href="{e(prev_ep["slug"])}.html">&larr; Episode {prev_ep["number"]}: {e(prev_ep["title"])}</a>'
    else:
        pager += "<span></span>"
    if next_ep:
        pager += f'<a href="{e(next_ep["slug"])}.html">Episode {next_ep["number"]}: {e(next_ep["title"])} &rarr;</a>'
    pager += "</div>"

    main = f"""
<h1>Episode {ep['number']}: {e(ep['title'])}</h1>
<p class="episode-meta">{e(fmt_date(ep['releaseDate']))} · {e(fmt_duration(ep['durationSeconds']))}</p>

{polaroid(ep['artWeb'], ep['artAlt'], f"Ep. {ep['number']} — {ep['title']}", ep['number'], root)}

<p>
  <button type="button" class="btn" data-episode-slug="{ep['slug']}" onclick="window.DustyPlayer.togglePlayFor('{ep['slug']}')">Play in the site player</button>
</p>

<audio controls preload="none" id="fallback-audio">
  <source src="{root}{ep['webFile']}" type="audio/mpeg">
  Your browser does not support the audio element. <a href="{root}{ep['webFile']}">Download the MP3</a> instead.
</audio>
<p><a href="{root}{ep['webFile']}" download>Download MP3</a> ({e(fmt_bytes(ep['bytes128k']))})</p>

{chapters_html}

{notes_html}

<details class="transcript">
<summary>Transcript</summary>
<div class="transcript-body">
{transcript_html}
</div>
</details>

{pager}
""".strip("\n")

    html_doc = page_shell(
        root=root,
        title=f"Episode {ep['number']}: {ep['title']} — Dusty Farts",
        description=ep["summary"],
        active_href="episodes.html",
        main_html=main,
    )
    out_dir = ROOT / "episodes"
    out_dir.mkdir(exist_ok=True)
    (out_dir / f"{ep['slug']}.html").write_text(html_doc, encoding="utf-8")


def build_maple_grove(show, episodes, root=""):
    by_number = {ep["number"]: ep for ep in episodes}
    cast_html = []
    for c in CAST:
        first_ep = by_number[c["first_episode"]]
        cast_html.append(f"""
  <li class="cast-entry">
    <h3>{e(c['name'])}</h3>
    <p>{e(c['bio'])} (First spotted in <a href="{root}episodes/{first_ep['slug']}.html">Episode {c['first_episode']}</a>.)</p>
  </li>""")

    landmark_html = []
    for loc in LANDMARKS:
        landmark_html.append(f"""
  <li class="cast-entry">
    <h3>{e(loc['name'])}</h3>
    <p>{e(loc['blurb'])}</p>
  </li>""")

    main = f"""
<h1>Meet Maple Grove</h1>
<p class="subtitle">The locals, catalogued for your protection.</p>

<h2>The Locals</h2>
<ul class="cast-list">{''.join(cast_html)}
</ul>

<h2>The Landmarks</h2>
<ul class="landmark-list">{''.join(landmark_html)}
</ul>
""".strip("\n")
    html_doc = page_shell(
        root=root,
        title="Meet Maple Grove — Dusty Farts",
        description="The cast and landmarks of Maple Grove, Dusty Farts' hometown.",
        active_href="maple-grove.html",
        main_html=main,
    )
    (ROOT / "maple-grove.html").write_text(html_doc, encoding="utf-8")


def build_jukebox(show, episodes, root=""):
    by_slug = {ep["slug"]: ep for ep in episodes}
    jamboree = next(ep for ep in episodes if ep["number"] == 10)
    ball = next(ep for ep in episodes if ep["number"] == 17)

    tracks = []
    for ch in jamboree["chapters"]:
        tracks.append({"slug": jamboree["slug"], "start": ch["start"], "end": ch["end"], "title": ch["title"]})

    # New Year Jingle: Episode 17's first chapter ("Opening", 0-85.7s) - confirmed
    # by ../Dusty Farts tracker.xlsx (jingle used: "New Year Jingle") and the cover
    # art ("Happy New Year 2026"). The Halloween Theme from Episodes 12/13 is
    # skipped: that episode has no chapter marker for its opening ~4 minutes, so
    # there's no clean boundary to seek to (see data/chapters/df12-13.json).
    if ball["chapters"]:
        ch = ball["chapters"][0]
        tracks.append({"slug": ball["slug"], "start": ch["start"], "end": ch["end"], "title": "New Year Jingle"})

    rows = []
    for i, t in enumerate(tracks):
        label = t["title"]
        rows.append(f"""
  <li class="jukebox-track">
    <span class="track-number" aria-hidden="true">{i + 1}</span>
    <span class="track-name">{e(label)}</span>
    <span class="date-stamp">{e(fmt_duration_words(t['end'] - t['start']))}</span>
    <button type="button" class="btn" aria-label="Play {e(label)}" data-play-key="{t['slug']}:{t['start']}"
      onclick="window.DustyPlayer.toggleRangeFor('{t['slug']}', {t['start']}, {t['end']}, '{e(label)}')">&#9654;</button>
  </li>""")

    main = f"""
<h1>Jingle Jukebox</h1>
<p class="subtitle">All the jingles, plus the versions the committee rejected.</p>
<p>Pulled straight from the <a href="{root}episodes/{jamboree['slug']}.html">Jingle Jamboree</a>
chapter breaks, plus the <a href="{root}episodes/{ball['slug']}.html">New Year's Eve</a> opener.
Press play on any track to hear just that clip through the site player.</p>
<ul class="jukebox-list">{''.join(rows)}
</ul>
""".strip("\n")
    html_doc = page_shell(
        root=root,
        title="Jingle Jukebox — Dusty Farts",
        description="Every Dusty Farts jingle, playable on its own.",
        active_href="jukebox.html",
        main_html=main,
    )
    (ROOT / "jukebox.html").write_text(html_doc, encoding="utf-8")


def build_about(show, root=""):
    faftb = show["aboutLinks"].get("firstAidForTheBlind")
    faftb_line = f'<p><a href="{e(faftb)}">First Aid for the Blind</a>, where Brian teaches screen readers professionally.</p>' if faftb else ""
    main = f"""
<h1>About</h1>
<p class="subtitle">The man behind the coffee counter.</p>

<p>Brian Clark has been blind since 2014. He's a former IT manager who now teaches
screen readers — NVDA and JAWS — professionally, and Dusty Farts is what happens
when that same precision and patience gets pointed at a diner booth instead of a
lesson plan.</p>

<p>Every episode is written, scored, engineered, and produced entirely non-visually:
Reaper for the sound design, a screen reader for everything else, ElevenLabs for the
cast's voices, Suno for the music, and ChatGPT as a writing partner. No screens were
consulted in the making of this town — Brian built it all by ear.</p>

<p>This website was built the same way, one step further removed: Claude — Anthropic's
AI — built the whole thing from Brian's existing scripts, audio, and notes, working
through Claude Desktop and Claude Code. That includes every visual on the site: the
Polaroid photos, the neon masthead, the diner textures, all of it AI-generated at
Brian's direction, with his wife Barb giving the final visual approval on every image.</p>

<p>He started the show to make his family laugh. It's still mostly for them; the rest
of us just get to listen in.</p>

<p><a href="https://github.com/1eyebiney">Brian on GitHub</a></p>
{faftb_line}

<p>Written, scored, and produced by Brian Clark — who had a screen reader, a
microphone, and just enough diner-grade coffee to pull this off.</p>
""".strip("\n")
    html_doc = page_shell(
        root=root,
        title="About — Dusty Farts",
        description="The story behind Dusty Farts and its creator, Brian Clark.",
        active_href="about.html",
        main_html=main,
    )
    (ROOT / "about.html").write_text(html_doc, encoding="utf-8")


def build_subscribe(show, root=""):
    feed_url = SITE_URL + "feed.xml"
    main = f"""
<h1>Subscribe</h1>
<p class="subtitle">Never miss a refill.</p>

<h2>Listen on this site</h2>
<ul>
  <li><strong>Keyboard:</strong> press H from anywhere on the site to expand and focus
    the player; the same key collapses it again once focus is inside. Once inside,
    press ? (question mark) any time to pause and see the full list of keyboard
    shortcuts.</li>
  <li><strong>Mouse or touch:</strong> use any Play button, or the player bar fixed at
    the bottom of the page — tap or click "Expand player" for the full controls.
    Pressing a Play button plays or pauses right where you are; it never moves you
    anywhere else on the page.</li>
  <li><strong>Screen reader on a phone:</strong> find the player with your rotor or
    swipe navigation — it's a labeled region named "Player" at the very end of every
    page.</li>
  <li><strong>Screen reader on a desktop (Browse Mode):</strong> use the "Jump to
    player" link right after the skip link, then use the audio control buttons
    located in the player region — not the headings key, since that's just normal
    heading navigation for you, not anything special. You can arrow onto any button
    in the player, or any Play button anywhere on the site, and activate it directly;
    activating it never moves your position.</li>
</ul>

<h2>RSS feed</h2>
<p>Dusty Farts publishes a standard podcast RSS feed. Paste this URL into any podcast
app:</p>
<div class="feed-url-field">
  <label for="feed-url" class="visually-hidden">Feed URL</label>
  <input type="text" id="feed-url" value="{e(feed_url)}" readonly>
  <button type="button" class="btn" id="copy-feed-btn">Copy</button>
</div>
<p id="copy-feed-status" role="status" class="visually-hidden"></p>
<script>
(function () {{
  var btn = document.getElementById('copy-feed-btn');
  var status = document.getElementById('copy-feed-status');
  if (!btn) return;
  btn.addEventListener('click', function () {{
    var field = document.getElementById('feed-url');
    field.select();
    navigator.clipboard && navigator.clipboard.writeText(field.value).then(function () {{
      status.textContent = 'Feed URL copied.';
    }}).catch(function () {{
      status.textContent = 'Copy failed — select the text and copy it manually.';
    }});
  }});
}})();
</script>

<p>Once the feed is listed, links for Apple Podcasts and Spotify will go here.</p>

<p>Hope's take: the coffee's better in person, but the feed doesn't spill in your bag.</p>
""".strip("\n")
    html_doc = page_shell(
        root=root,
        title="Subscribe — Dusty Farts",
        description="How to listen to Dusty Farts: the site player, RSS feed, and podcast apps.",
        active_href="subscribe.html",
        main_html=main,
    )
    (ROOT / "subscribe.html").write_text(html_doc, encoding="utf-8")


def build_404(show, root=""):
    main = """
<h1>Page not found</h1>
<p>Hope, reporting live: Fred wandered off with this page. He does that. It'll probably
turn up in the same place as the missing booth cushion and John's second-favorite mug.</p>
<p>In the meantime —</p>
<ul>
  <li><a href="index.html">Go home</a></li>
  <li><a href="episodes.html">See the episodes</a></li>
</ul>
""".strip("\n")
    html_doc = page_shell(
        root=root,
        title="Page not found — Dusty Farts",
        description="This page could not be found.",
        active_href="",
        main_html=main,
    )
    (ROOT / "404.html").write_text(html_doc, encoding="utf-8")


def main():
    data = load_json(DATA / "episodes.json")
    show = data["show"]
    episodes = sorted(data["episodes"], key=lambda e: e["number"])

    build_index(show, episodes)
    build_episodes_catalog(show, episodes)
    for i in range(len(episodes)):
        build_episode_page(show, episodes, i)
    build_maple_grove(show, episodes)
    build_jukebox(show, episodes)
    build_about(show)
    build_subscribe(show)
    build_404(show)

    print(f"Built {2 + len(episodes) + 5} HTML pages.")


if __name__ == "__main__":
    main()
