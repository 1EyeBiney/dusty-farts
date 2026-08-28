#!/usr/bin/env python3
"""Assemble the final data/episodes.json from:
- the existing episodes.json (base metadata: dates, locations, etc.)
- measured audio duration/bytes (data/audio_measurements.json, from ffprobe)
- extracted chapters (data/chapters/dfNN.json)
- extracted show notes (data/shownotes/dfNN.json)
- hand-authored slugs, one-liner summaries, and alt text (below)

Run from the website/ folder: python tools/build_episodes_json.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# slug (pattern: df + zero-padded number(s) + title-slug, matching audio/image filenames)
SLUGS = {
    1: "df01-pilot",
    2: "df02-grease-trap-gospel",
    3: "df03-lounge-lizards",
    4: "df04-nut-jobs",
    5: "df05-blood-brothers",
    6: "df06-nuts-and-dolts",
    7: "df07-fight-club",
    8: "df08-jiffy-part-deaux",
    9: "df09-freudean-fouls",
    10: "df10-jingle-jamboree",
    11: "df11-condiment-clash",
    12: "df12-13-booth-or-treat",
    14: "df14-drip-drip-horray",
    16: "df16-murder-in-the-park",
    17: "df17-all-power-to-the-ball",
}

# audio/image file slug (matches SLUGS prefix before the title)
FILE_SLUG = {
    1: "df01", 2: "df02", 3: "df03", 4: "df04", 5: "df05", 6: "df06",
    7: "df07", 8: "df08", 9: "df09", 10: "df10", 11: "df11", 12: "df12-13",
    14: "df14", 16: "df16", 17: "df17",
}

# Hope-voiced one-line summaries for the catalog/RSS (dry, warm, absurd)
SUMMARIES = {
    1: "Two forty-year friends claim a booth at the Polyester Lounge and redefine friendship as sarcasm, side orders, and one more refill of regret.",
    2: "The boys make their weekly pilgrimage to the Jiffy Lube — not for oil changes, but for the free coffee and a front-row seat to the greasy ballet.",
    3: "A hijacked prayer-request group chat becomes a coffee-rating scandal, and it turns out not all biscotti comes from a bakery.",
    4: "John declares the park's squirrels a covert operation; Fred invents a rating scale for nuts, because if coffee gets one, so should pecans.",
    5: "The boys discover the blood donor bus has free cookies and recliners that basically count as a booth — Dr. Bobby's medical wisdom optional.",
    6: "Dusty and Farts set up camp on two toilets in a hardware store, taste-test espresso from a gnome, and turn plumbing into prophecy.",
    7: "A thermostat argument escalates into a full goat-boxing pageant in the parking lot, refereed by actual goats.",
    8: "Sharpie graffiti on the booth starts a turf war, and somewhere between torque angles and postal-carrier betting, Fred gives away his smart watch.",
    9: "The boys wander into the wrong therapy circle at the YMCA and come out with ink blots, doodles, and opinions about their own subconscious.",
    10: "Aria hijacks the show for a jingle retrospective — every Dusty Farts earworm ever recorded, replayed, and lightly regretted.",
    11: "A missed blood-bus appointment turns hangry, and one wrong squirt of ketchup ignites a full tabletop condiment war.",
    12: "The boys build the Booth of Doom out of a borrowed hearse and two discount coffins for Maple Grove's Trunk or Treat contest.",
    14: "John unlocks a self-diagnosed detective talent he calls Clue-dini, and the blood bus never fully recovers.",
    16: "Clue-dini returns for his toughest case yet: a dead squirrel, on the table, in the booth.",
    17: "Maple Grove unplugs itself fridge by fridge in pursuit of one clean New Year's countdown for the Ball.",
}

# Scene-first, descriptive alt text for the cover art (funny second, per CLAUDE.md/DESIGN.md 3)
ART_ALT = {
    1: "Two older men sit in a red vinyl diner booth, coffee mugs and condiment bottles between them, a glowing neon “Polyester Lounge — Bottomless Coffee” sign in the window behind. A handwritten caption below reads “Dusty” with an arrow to the man on the left and “Farts” with an arrow to the man on the right: don’t feed them after noon.",
    2: "An empty red, cream, and teal diner booth sits in a garage bay: two steaming coffee mugs on the table beside an old drip coffeemaker, a car up on a lift, and a framed roadside-mascot photo on the wall behind.",
    3: "Two bearded dragon lizards, one wearing sunglasses, perch on the back of booth number three in front of a glowing “Polyester Lounge” neon sign, while two cups of coffee and two plates of buttered toast sit on the table below.",
    4: "Two squirrels perch on the back of a red diner booth beside a small orange cooler, eyeing a ham sandwich, a dish of shredded nuts, and a bowl of little hot dogs set out on the table.",
    5: "Two matching recliners sit in a blood-donation room, IV poles and bags on either side, a plate of chocolate chip cookies on the table between them, medical supplies lined up on the counter above.",
    6: "A bearded garden gnome in a red coat stands on an end table between two toilets in a warehouse aisle, holding a length of hose, with a potted plant, a lit taper candle, and a pink flamingo nearby.",
    7: "Two goats wearing red boxing gloves stand in a parking lot in front of the glowing Polyester Lounge sign and a “Marquis of Sheepsberrie” delivery truck, a microphone and speaker set up between them like a weigh-in.",
    8: "An empty diner booth scrawled with doodled stars and stick figures in marker, a lone coffee mug and two pens on the table, a car-repair garage visible through the doorway behind.",
    9: "An empty YMCA gymnasium with a scoreboard reading “Maple Grove” on the wall and basketballs scattered across the floor, two worn diner-style booth benches pulled up to a folding table set with mismatched mugs and a pitcher.",
    10: "A swirling, psychedelic poster in reds, teals, and purples: a steaming mug of coffee and a harmonica flank two squirrels holding coffee beans, above a curved diner booth, under lettering that reads “Jingle Jamboree.”",
    11: "A map split down the middle like warring nations: ketchup, relish, and mayonnaise on the red side, sriracha, mustard, and rice on the blue side, titled “Condiment Clash.”",
    12: "The open tailgate of a hearse at dusk: two small wooden coffins nested in cobwebs, a bubbling cauldron, a sheeted ghost, and piles of Halloween candy laid out like trick-or-treat loot, titled “Booth or Treat: Booth of Doom.”",
    14: "A converted mobile blood-drive bus painted with a garish banner reading “Doctor Bobby’s Rolling Vein Drain Extravaganza,” donor recliners and IV equipment visible through its windows, titled “Drip, Drip, Horray!”",
    16: "A comic-style park scene: two older men in trench coats sit at a picnic table under a “Maple Gump Park” sign examining evidence with a magnifying glass, surrounded by inset panels of muddy sandal prints, a syringe and gloves, a bench with a dropped hot dog, and scattered gems, titled “Murder in the Park.”",
    17: "A glittering, multicolored New Year’s Eve ball atop a wooden rigging tower wired to a control panel, fireworks and balloons overhead, a banner reading “All Power to the Ball — Happy New Year 2026.”",
}

LOGO_ALT = ART_ALT[1]

# Measured durations for episodes whose durationSeconds was null in the source file
MEASURED_DURATIONS = {
    1: 739.328957,
    2: 917.397619,
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    base = load_json(DATA / "episodes.json")

    for ep in base["episodes"]:
        n = ep["number"]
        slug = SLUGS[n]
        file_slug = FILE_SLUG[n]

        if ep.get("durationSeconds") is None:
            ep["durationSeconds"] = round(MEASURED_DURATIONS[n], 3)
        ep.pop("note", None)

        ep["slug"] = slug
        ep["webFile"] = f"audio/{file_slug}.mp3"
        ep["artWeb"] = f"images/{file_slug}.jpg"
        ep["artAlt"] = ART_ALT[n]
        ep["summary"] = SUMMARIES[n]

        chapters_path = DATA / "chapters" / f"{file_slug}.json"
        ep["chapters"] = load_json(chapters_path) if chapters_path.exists() else []

        shownotes_path = DATA / "shownotes" / f"{file_slug}.json"
        ep["showNotesData"] = f"data/shownotes/{file_slug}.json" if shownotes_path.exists() else None

        ep["transcript"] = f"data/transcripts/{file_slug}.html"

    base["show"]["hopeWelcome"] = "audio/hope-welcome.mp3"
    base["show"]["logoAlt"] = LOGO_ALT

    out_path = DATA / "episodes.json"
    out_path.write_text(json.dumps(base, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
