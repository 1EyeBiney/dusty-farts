#!/usr/bin/env python3
"""Generate feed.xml (RSS 2.0 + iTunes + Podcasting 2.0 chapters) from
data/episodes.json. See DESIGN.md section 9 / HANDOFF.md Phase 2.

Also (re)writes data/chapters/dfNN.json in the Podcast Namespace JSON
Chapters format (https://github.com/Podcastindex-org/podcast-namespace/
blob/main/chapters/jsonChapters.md), sourced from episodes.json's already
-extracted chapters, for episodes that have any.

Run from the website/ folder: python tools/make_feed.py
"""
import json
import sys
from email.utils import format_datetime
from datetime import datetime, timezone, timedelta
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
FEED_TZ = timezone(timedelta(hours=-5))  # -0500, per DESIGN.md 9


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def rfc2822(iso_date):
    d = datetime.strptime(iso_date, "%Y-%m-%d").replace(hour=12, tzinfo=FEED_TZ)
    return format_datetime(d)


def write_podcast_chapters_json(ep, site_url):
    if not ep["chapters"]:
        return None
    out = {
        "version": "1.2.0",
        "chapters": [
            {"startTime": round(c["start"], 3), "endTime": round(c["end"], 3), "title": c["title"]}
            for c in ep["chapters"]
        ],
    }
    chapters_dir = DATA / "chapters"
    chapters_dir.mkdir(parents=True, exist_ok=True)
    file_slug = ep["webFile"].split("/")[-1].replace(".mp3", "")
    out_path = chapters_dir / f"{file_slug}.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return site_url + f"data/chapters/{file_slug}.json"


def build_item(ep, show, site_url):
    title = f"Episode {ep['number']}: {ep['title']}"
    page_url = site_url + f"episodes/{ep['slug']}.html"
    enclosure_url = site_url + ep["webFile"]
    image_url = site_url + ep["artWeb"]
    duration = int(round(ep["durationSeconds"]))

    chapters_url = write_podcast_chapters_json(ep, site_url)
    chapters_tag = (
        f'      <podcast:chapters url={quoteattr(chapters_url)} type="application/json+chapters"/>\n'
        if chapters_url else ""
    )

    return f"""    <item>
      <title>{escape(title)}</title>
      <link>{escape(page_url)}</link>
      <guid isPermaLink="true">{escape(page_url)}</guid>
      <pubDate>{rfc2822(ep['releaseDate'])}</pubDate>
      <description>{escape(ep['summary'])}</description>
      <enclosure url={quoteattr(enclosure_url)} length="{ep['bytes128k']}" type="audio/mpeg"/>
      <itunes:title>{escape(title)}</itunes:title>
      <itunes:summary>{escape(ep['summary'])}</itunes:summary>
      <itunes:duration>{duration}</itunes:duration>
      <itunes:episode>{ep['number']}</itunes:episode>
      <itunes:episodeType>full</itunes:episodeType>
      <itunes:image href={quoteattr(image_url)}/>
      <itunes:explicit>false</itunes:explicit>
{chapters_tag}    </item>"""


def build_feed(data):
    show = data["show"]
    site_url = show["siteUrl"]
    episodes = sorted(data["episodes"], key=lambda e: e["number"], reverse=True)

    items = "\n".join(build_item(ep, show, site_url) for ep in episodes)
    image_url = site_url + "images/logo.jpg"
    last_build = rfc2822(episodes[0]["releaseDate"])
    categories = show["category"]  # ["Fiction", "Comedy Fiction"]

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"
     xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"
     xmlns:podcast="https://podcastindex.org/namespace/1.0"
     xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>{escape(show['title'])}</title>
    <link>{escape(site_url)}</link>
    <atom:link href={quoteattr(site_url + 'feed.xml')} rel="self" type="application/rss+xml"/>
    <language>{escape(show['language'])}</language>
    <description>{escape(show['description'])}</description>
    <lastBuildDate>{last_build}</lastBuildDate>
    <itunes:author>{escape(show['author'])}</itunes:author>
    <itunes:owner>
      <itunes:name>{escape(show['author'])}</itunes:name>
      <itunes:email>{escape(show['email'])}</itunes:email>
    </itunes:owner>
    <itunes:image href={quoteattr(image_url)}/>
    <image>
      <url>{escape(image_url)}</url>
      <title>{escape(show['title'])}</title>
      <link>{escape(site_url)}</link>
    </image>
    <itunes:category text={quoteattr(categories[0])}>
      <itunes:category text={quoteattr(categories[1])}/>
    </itunes:category>
    <itunes:explicit>false</itunes:explicit>
    <itunes:type>serial</itunes:type>
{items}
  </channel>
</rss>
"""


def main():
    data = load_json(DATA / "episodes.json")
    feed_xml = build_feed(data)
    out_path = ROOT / "feed.xml"
    out_path.write_text(feed_xml, encoding="utf-8")
    print(f"Wrote {out_path.relative_to(ROOT)} ({len(data['episodes'])} episodes)")


if __name__ == "__main__":
    sys.exit(main())
