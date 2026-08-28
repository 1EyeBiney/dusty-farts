#!/usr/bin/env python3
"""Extract chapter markers from episode MP3s via ffprobe and write
data/chapters/dfNN.json (normalized: leading chapter number stripped from
title). Run from the website/ folder. Requires ffprobe on PATH.

Usage: python tools/extract_chapters.py
"""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AUDIO_DIR = ROOT / "audio"
CHAPTERS_DIR = ROOT / "data" / "chapters"

NUM_PREFIX = re.compile(r"^\s*\d+\s+(.*)$")


def extract(mp3_path: Path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_chapters", "-of", "json", str(mp3_path)],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(result.stdout)
    chapters = []
    for c in data.get("chapters", []):
        raw_title = c.get("tags", {}).get("title", "").strip()
        m = NUM_PREFIX.match(raw_title)
        title = m.group(1).strip() if m else raw_title
        chapters.append(
            {
                "title": title,
                "start": round(float(c["start_time"]), 3),
                "end": round(float(c["end_time"]), 3),
            }
        )
    return chapters


def main():
    CHAPTERS_DIR.mkdir(parents=True, exist_ok=True)
    for mp3 in sorted(AUDIO_DIR.glob("df*.mp3")):
        slug = mp3.stem  # e.g. df04, df12-13
        chapters = extract(mp3)
        out_path = CHAPTERS_DIR / f"{slug}.json"
        out_path.write_text(json.dumps(chapters, indent=2) + "\n", encoding="utf-8")
        print(f"{slug}: {len(chapters)} chapters -> {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.exit(main())
