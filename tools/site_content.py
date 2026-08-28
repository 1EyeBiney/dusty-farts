"""Hand-authored page copy for the Meet Maple Grove page and other static
content, kept separate from tools/build_site.py for readability. Portraits
are Hope-voiced, spoiler-light, drawn from the character sheet docx files
in the parent folder where one exists, and from the show notes "Voices
You'll Hear" lines otherwise (see CLAUDE.md / DESIGN.md 5.4).

Note on Grady: DESIGN.md's cast list names a "Grady" alongside the others,
sourced from ../Grady character sheet.docx. That file's actual content is
about an unrelated narration project (a family story about a child's vision
loss, not Maple Grove), and Grady does not appear in any episode's cast in
../Dusty Farts tracker.xlsx. He's omitted here rather than invented -
flag for Brian to confirm whether that file was meant for this show at all.
"""

CAST = [
    {
        "name": "John “Dusty”",
        "first_episode": 1,
        "bio": (
            "The self-appointed brains of the operation — suspicious of squirrels, "
            "suspicious of thermostats, suspicious of anyone who disagrees with him "
            "about the one correct temperature for a diner (74°F, “the gentleman’s "
            "temperature”). Somewhere around Episode 14 he develops a detective alter "
            "ego he calls “Clue-dini,” which nobody encouraged and everybody now has "
            "to live with."
        ),
    },
    {
        "name": "Fred “Farts”",
        "first_episode": 1,
        "bio": (
            "The heart of the two, if you squint. Sentimental about coupons, cookies, "
            "and inventing rating systems for things that do not need rating systems "
            "(nuts, condiments). Complains constantly, means none of it, and has been "
            "known to prove it by giving away his own smart watch."
        ),
    },
    {
        "name": "Hope",
        "first_episode": 1,
        "bio": (
            "I narrate. That’s the job — conspiratorial commentary, half-wisdom, and a "
            "running record of grievances, mostly about two men and a booth. I did not "
            "choose this life. I don’t regret it, either, though you didn’t hear me say "
            "that."
        ),
    },
    {
        "name": "Aria",
        "first_episode": 1,
        "bio": (
            "Waitress and den mother of the Polyester Lounge, armed with sass, coffee, "
            "and zero tolerance for nonsense. Has since been drafted as referee for a "
            "goat-boxing match, Pumpkin-Spice Fairy on Halloween, and Power Compliance "
            "Officer on New Year’s Eve. None of this was in her job description."
        ),
    },
    {
        "name": "Doctor Bobby",
        "first_episode": 5,
        "bio": (
            "Runs the mobile blood-donation bus with the enthusiasm of a man trained "
            "somewhere the line between hospital and farm was blurry. Tells stories "
            "that start with a medical procedure and end with a goat. Wears a cursed "
            "calculator watch that has never once told the correct time."
        ),
    },
    {
        "name": "Doctor Fritz “Freudy”",
        "first_episode": 9,
        "bio": (
            "A therapist who has read exactly enough Freud to be dangerous. Mistakes "
            "sarcasm for progress, doodles for diagnosis, and once ran a therapy booth "
            "in a shopping mall food court until the health department had opinions "
            "about it."
        ),
    },
    {
        "name": "Curtis",
        "first_episode": 8,
        "bio": (
            "A man in his 40s who still lives with his mother and runs the town’s "
            "conspiracy-theory newsletter. Announces himself loudly, tags booths with "
            "Sharpie graffiti, and travels with Nut-Zilla, a homemade contraption of "
            "uncertain purpose and confirmed menace."
        ),
    },
    {
        "name": "Lyle",
        "first_episode": 2,
        "bio": (
            "Keeper of the Jiffy Lube coffee pot and dispenser of reality checks, "
            "delivered flat, dry, and entirely without enthusiasm. Not impressed. "
            "Never has been."
        ),
    },
    {
        "name": "Pearlie Fae",
        "first_episode": 10,
        "bio": (
            "Gravel-voiced frontwoman of The Rusty Hinges, the house band responsible "
            "for every Dusty Farts jingle. Announces her retirement approximately once "
            "a week and shows up to the next gig anyway."
        ),
    },
    {
        "name": "Suzy and Umie",
        "first_episode": 16,
        "bio": (
            "Arrived in a cloud of rhinestones and haven’t left. Sparkle engineers, "
            "vibe managers, and the reason Maple Grove’s New Year’s Eve ball carries "
            "more glitter than any small town’s power grid can safely support."
        ),
    },
]

LANDMARKS = [
    {
        "name": "Polyester Lounge",
        "blurb": (
            "The boys’ home booth. Bottomless coffee, cracked vinyl, and a neon sign "
            "that’s the closest thing this show has to a permanent set."
        ),
    },
    {
        "name": "Jiffy Lube",
        "blurb": (
            "Free coffee, a captive audience, and Lyle’s disapproval, all included "
            "with the oil change nobody’s actually getting."
        ),
    },
    {
        "name": "Doctor Bobby’s Blood Bus",
        "blurb": (
            "A converted RV where donating blood comes with recliners, cookies, and "
            "more medical opinions than are strictly licensed."
        ),
    },
    {
        "name": "Maple Gump Park",
        "blurb": (
            "Home to the Booth of Cherished Chaplain Clarence Booths, a park bench "
            "with more backstory than most people, and a squirrel population John "
            "considers organized labor."
        ),
    },
    {
        "name": "Menards",
        "blurb": (
            "A hardware store that, for one memorable episode, became a two-toilet "
            "diner booth. Ask no further questions."
        ),
    },
    {
        "name": "Maple Grove YMCA",
        "blurb": (
            "Gym, community hall, and — briefly, disastrously — group therapy space."
        ),
    },
]
