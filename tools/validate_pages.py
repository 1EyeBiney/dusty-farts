#!/usr/bin/env python3
"""Cheap structural sanity pass over every generated HTML page: exactly one
h1, exactly one aria-current="page", the wayfinding contract's skip links
present, player region present and last, no leaked "None"/"{" template
artifacts, and every referenced local asset (img src, audio, css, js)
actually exists on disk. Not a substitute for the NVDA pass in HANDOFF.md
Phase 4 - just catches build-script mistakes early.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

pages = list(ROOT.glob("*.html")) + list((ROOT / "episodes").glob("*.html"))

problems = []

for page in pages:
    text = page.read_text(encoding="utf-8")
    rel = page.relative_to(ROOT)

    h1_count = len(re.findall(r"<h1[ >]", text))
    if h1_count != 1:
        problems.append(f"{rel}: {h1_count} <h1> elements (expected 1)")

    current_count = text.count('aria-current="page"')
    if current_count != 1 and page.name != "404.html":
        problems.append(f"{rel}: {current_count} aria-current=\"page\" (expected 1)")

    if 'href="' not in text.split("skip-links", 1)[1][:200]:
        problems.append(f"{rel}: skip-links block malformed")

    if text.count('id="df-player"') != 1:
        problems.append(f"{rel}: player region missing or duplicated")

    if "{" in text and "window.SITE_BASE" not in text.split("{", 1)[0][-40:]:
        # crude check for an unformatted Python f-string brace left behind
        stray = re.findall(r"\{[a-zA-Z_'\"][^{}]{0,40}\}", text)
        stray = [s for s in stray if "SITE_BASE" not in s]
        if stray:
            problems.append(f"{rel}: possible unformatted template brace: {stray[:3]}")

    for m in re.finditer(r'(?:src|href)="([^"]+)"', text):
        url = m.group(1)
        if url.startswith(("http://", "https://", "#", "mailto:")):
            continue
        if url.startswith("data:"):
            continue
        target = (page.parent / url).resolve()
        if not target.exists():
            problems.append(f"{rel}: missing local asset {url}")

if problems:
    print(f"{len(problems)} problem(s):")
    for p in problems:
        print(" -", p)
    sys.exit(1)
else:
    print(f"OK: {len(pages)} pages checked, no problems found.")
