#!/usr/bin/env python3
"""Extract show notes text from the per-episode docx files in
../Podcast work/Show Notes/ into data/shownotes/dfNN.json.

Sections extracted (consistent template across all episodes): Episode
Summary, Voices You'll Hear, Sound Stage, Sound & Style, For New
Listeners, Credits. Bullet-list sections (Voices, Sound Stage) become
JSON arrays; prose sections become arrays of paragraph strings.

Run from the website/ folder. Requires python-docx (pip install python-docx).
"""
import json
import re
import sys
from pathlib import Path

import docx

ROOT = Path(__file__).resolve().parent.parent
PARENT = ROOT.parent
NOTES_DIR = PARENT / "Podcast work" / "Show Notes"
OUT_DIR = ROOT / "data" / "shownotes"

SECTION_HEADERS = [
    "Episode Summary",
    "Voices You’ll Hear",
    "Sound Stage",
    "Sound & Style",
    "For New Listeners",
    "Credits",
]
BULLET_SECTIONS = {"Voices You’ll Hear", "Sound Stage"}
BULLET_RE = re.compile(r"^[•●‣\-\*]\s*")

# episode slug -> docx filename (relative to NOTES_DIR)
FILES = {
    "df01": "Show Notes DF01 Pilot.docx",
    "df02": "Show Notes DF02 Grease Trap Gospel.docx",
    "df03": "Show Notes DF03 Lounge Lizards.docx",
    "df04": "Show Notes DF04 Nut Jobs.docx",
    "df05": "Show Notes DF05 Blood Brothers.docx",
    "df06": "Show Notes DF06 Nuts and Dolts.docx",
    "df07": "Show Notes DF07 Fight Club.docx",
    "df08": "Show Notes DF08 Jiffy Part Deaux.docx",
    "df09": "Show Notes DF09 Freudean Fouls.docx",
    "df10": "Show Notes DF10 Jingle Jamboree.docx",
    "df11": "Show Notes DF11 Condiment Clash.docx",
    "df12-13": "Show Notes DF12 and 13 Booth or Treat - A Maple Grove Spooktacular Special.docx",
    "df14": "Show Notes DF14 Drip, Drip, Horray!.docx",
    "df16": "Show Notes DF16 Murder in the Park.docx",
    "df17": "Show Notes DF17 All Power to the Ball.docx",
}


def extract_one(path: Path) -> dict:
    d = docx.Document(str(path))
    paras = [p.text.strip() for p in d.paragraphs]
    paras = [p for p in paras if p]

    title_line = paras[0] if paras else ""

    # find indices of section headers in order
    idxs = []
    for i, p in enumerate(paras):
        if p in SECTION_HEADERS:
            idxs.append((i, p))
    idxs.append((len(paras), None))

    sections = {}
    for (start, name), (end, _) in zip(idxs, idxs[1:]):
        if name is None:
            continue
        body = paras[start + 1 : end]
        body = [b for b in body if not BULLET_RE.match(b) or len(BULLET_RE.sub("", b)) > 0]
        body = [BULLET_RE.sub("", b).strip() for b in body]
        body = [b for b in body if b and b != "•"]
        sections[name] = body

    return {
        "titleLine": title_line,
        "summary": sections.get("Episode Summary", []),
        "voices": sections.get("Voices You’ll Hear", []),
        "soundStage": sections.get("Sound Stage", []),
        "soundAndStyle": sections.get("Sound & Style", []),
        "forNewListeners": sections.get("For New Listeners", []),
        "credits": sections.get("Credits", []),
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for slug, fname in FILES.items():
        src = NOTES_DIR / fname
        if not src.exists():
            print(f"MISSING: {src}")
            continue
        data = extract_one(src)
        out_path = OUT_DIR / f"{slug}.json"
        out_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{slug}: summary={len(data['summary'])}p voices={len(data['voices'])} soundStage={len(data['soundStage'])} -> {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
