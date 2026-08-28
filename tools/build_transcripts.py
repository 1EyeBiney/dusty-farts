#!/usr/bin/env python3
"""Draft per-episode transcripts from ../Scripts/*.docx into
data/transcripts/dfNN.html fragments, per DESIGN.md 5.3 / 8.3:

- Speaker names become <strong> labels.
- Bracketed stage/sound directions ("[The Jiffy Lube door jingles]") are kept.
- Parenthetical performance notes on speaker cues ("John (grumbling):") are
  production metadata for the voice actor, not transcript text - dropped,
  keeping just the normalized speaker name.
- Anything before the first speaker cue or bracketed cue (episode titles,
  freeform production notes like "Harmonica Transition") is dropped.
- Chapter titles (from data/chapters/dfNN.json) are inserted as <h3>
  subheadings at a proportional position (dialogue-paragraph fraction ~=
  audio-time fraction). This is a best-effort estimate, not a real
  alignment - flagged with an HTML comment for spot-checking.

THESE ARE DRAFTS. Per DESIGN.md 8.3 they are hand-reviewed content:
Brian must spot-listen and correct before publishing, especially around
the dropped freeform cues and the estimated chapter placements.

Run from the website/ folder. Requires python-docx.
"""
import html
import json
import re
import sys
from pathlib import Path

import docx

ROOT = Path(__file__).resolve().parent.parent
PARENT = ROOT.parent
SCRIPTS_DIR = PARENT / "Scripts"
CHAPTERS_DIR = ROOT / "data" / "chapters"
OUT_DIR = ROOT / "data" / "transcripts"

FILES = {
    "df01": "01 DF  Pilot.docx",
    "df02": "02 Grease Trap Gospel.docx",
    "df03": "03 Lounge Lizards.docx",
    "df04": "04 Nut Jobs 1.4a.docx",
    "df05": "05 Blood Brothers 1.4.docx",
    "df06": "06 Nuts and Dolts .script 1.3 .docx",
    "df07": "07 Fight Club.docx",
    "df08": "08 Jiffy Part Deaux.docx",
    "df09": "09 Freudean Fouls.docx1.docx",
    "df10": "10 Jingle Jamboree script.docx",
    "df11": "11 Condiments Clash script.docx",
    "df12-13": "12 and 13 Booth or Treat - A Maple Grove Spooktacular Special Script.docx",
    "df14": "14 Drip, Drip, Horray! script.docx",
    "df16": "16 Murder in the park script.docx",
    "df17": "17 All Power to the Ball script.docx",
}

NAME_MAP = {
    "john": "John",
    "fred": "Fred",
    "hope": "Hope",
    "hope intro": "Hope",
    "aria": "Aria",
    "curtis": "Curtis",
    "dr. bobby": "Dr. Bobby",
    "doctor bobby": "Dr. Bobby",
    "suzy": "Suzy",
    "lyle": "Lyle",
    "dr. fritz": "Dr. Fritz",
    "fritz": "Dr. Fritz",
    "dr. freudy": "Dr. Fritz",
    "umie": "Umie",
    "gigi": "Gigi",
    "clifford": "Clifford",
    "steve": "Steve",
    "pearlie fae": "Pearlie Fae",
    "scotty": "Scotty",
    "together": "Together",
    "clarence": "Clarence",
    "kids": "Kids",
    "grady": "Grady",
}

CUE_RE = re.compile(r"^(?P<name>[A-Za-z][A-Za-z .]*?)\s*(?:\([^)]*\))?\s*:+\s*$")
BRACKET_RE = re.compile(r"^\[.*\]$")
QUOTE_CHARS = "\"'‘’“” "


def normalize_name(raw: str):
    key = raw.strip().lower().rstrip(".").strip()
    key = re.sub(r"\s+", " ", key)
    # allow "dr. bobby" whether or not trailing period was stripped
    for candidate in (key, key + "."):
        if candidate in NAME_MAP:
            return NAME_MAP[candidate]
    return NAME_MAP.get(key)


PAREN_RE = re.compile(r"\([^)]*\)")
LEADING_STRAY_RE = re.compile(r"^[A-Za-z](?=[\"'‘“])")


def clean_line(t: str) -> str:
    """Per-line cleanup, applied before lines are joined into a speech block
    so edge quote marks and inline performance directions don't end up
    stranded mid-sentence."""
    t = t.strip()
    t = LEADING_STRAY_RE.sub("", t)  # drop a stray single char glued to an opening quote
    t = t.strip(QUOTE_CHARS)
    t = PAREN_RE.sub(" ", t)  # inline performance/action directions, e.g. "(musing, taking a seat)"
    t = t.strip(QUOTE_CHARS)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def clean_dialogue_text(lines) -> str:
    cleaned = [clean_line(l) for l in lines]
    cleaned = [c for c in cleaned if c]
    text = " ".join(cleaned)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_script(path: Path):
    d = docx.Document(str(path))
    paragraphs = [p.text.strip() for p in d.paragraphs]

    blocks = []  # list of ("speech", speaker, [lines]) or ("cue", text)
    current_speaker = None
    current_lines = []

    def flush():
        nonlocal current_speaker, current_lines
        if current_speaker and current_lines:
            text = clean_dialogue_text(current_lines)
            if text:
                blocks.append(("speech", current_speaker, text))
        current_lines = []

    for raw in paragraphs:
        t = raw.strip()
        if not t:
            continue
        m = CUE_RE.match(t)
        if m:
            flush()
            name = normalize_name(m.group("name"))
            current_speaker = name  # None if unrecognized -> drops following lines
            continue
        if BRACKET_RE.match(t):
            flush()
            blocks.append(("cue", t))
            current_speaker = None
            continue
        if current_speaker:
            current_lines.append(t)
        # else: freeform production text before any recognized speaker - dropped
    flush()
    return blocks


def load_chapters(slug: str):
    p = CHAPTERS_DIR / f"{slug}.json"
    if not p.exists():
        return []
    return json.loads(p.read_text(encoding="utf-8"))


def render_html(slug: str, blocks, chapters):
    speech_count = sum(1 for b in blocks if b[0] == "speech")
    total_duration = chapters[-1]["end"] if chapters else 0

    # map: after which speech index to insert which chapter heading
    insertions = {}
    if chapters and speech_count:
        for ch in chapters:
            frac = ch["start"] / total_duration if total_duration else 0
            idx = round(frac * speech_count)
            insertions.setdefault(idx, []).append(ch["title"])

    out = []
    out.append(
        "<!-- Draft transcript, auto-extracted from the script. Hand-review "
        "against the final audio before publishing: freeform production/"
        "transition notes that weren't in brackets (e.g. \"Harmonica "
        "Transition\") may still be stuck inline in a speech paragraph and "
        "need deleting; chapter placements below are a proportional "
        "estimate, not time-aligned; and check for any script/audio "
        "divergence. See DESIGN.md 5.3 / 8.3. -->"
    )
    speech_i = 0
    if 0 in insertions:
        for title in insertions[0]:
            out.append(f"<h3>{html.escape(title)}</h3>")
    for kind, *rest in blocks:
        if kind == "cue":
            text = rest[0]
            out.append(f"<p class=\"cue\">{html.escape(text)}</p>")
        else:
            speaker, text = rest
            speech_i += 1
            out.append(f"<p><strong>{html.escape(speaker)}:</strong> {html.escape(text)}</p>")
            if speech_i in insertions:
                for title in insertions[speech_i]:
                    out.append(f"<h3>{html.escape(title)}</h3>")
    return "\n".join(out) + "\n"


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for slug, fname in FILES.items():
        src = SCRIPTS_DIR / fname
        if not src.exists():
            print(f"MISSING: {src}")
            continue
        blocks = parse_script(src)
        chapters = load_chapters(slug)
        html_out = render_html(slug, blocks, chapters)
        out_path = OUT_DIR / f"{slug}.html"
        out_path.write_text(html_out, encoding="utf-8")
        n_speech = sum(1 for b in blocks if b[0] == "speech")
        n_cues = sum(1 for b in blocks if b[0] == "cue")
        print(f"{slug}: {n_speech} lines, {n_cues} cues -> {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
