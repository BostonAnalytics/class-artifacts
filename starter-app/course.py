"""
Edit this file to make the app yours. Everything a student sees comes from here.

COURSE_NAME   shown in the header
ACTIVITIES    one entry per module activity

Each activity:
    slug        short id used in the URL, e.g. "m1" -> /a/m1
    module      module number (for ordering and labels)
    title       activity name
    objective   the existing learning objective it practices (copy from your syllabus)
    discussion  the discussion it feeds, shown on the artifact card
    intro       one or two sentences of instructions (also put these on your activity slide)
    variants    optional list of inputs; each student gets one, chosen from their username,
                so the same student always sees the same input (live or from the recording)
    fields      what students fill in. Types:
                  "short"   one line of text
                  "text"    a paragraph
                  "choice"  pick one of "options"
                  "checks"  tick any of "options"
"""

COURSE_NAME = "Your Course 101 · Sample"

ACTIVITIES = [
    {
        "slug": "m1",
        "module": 1,
        "title": "Think, pair, share",
        "objective": "Explain the module's core concept in your own words.",
        "discussion": "Discussion 1",
        "intro": "Answer the question alone first. Then compare with a partner (or with the sample partner "
                 "answer if you are watching the recording) and write what changed.",
        "variants": [],
        "fields": [
            {"name": "my_answer", "type": "text", "label": "1. My answer, before talking to anyone"},
            {"name": "partner_difference", "type": "text", "label": "2. What my partner saw differently"},
            {"name": "final_answer", "type": "short", "label": "3. My answer now, in one sentence"},
        ],
    },
    {
        "slug": "m2",
        "module": 2,
        "title": "Make the call",
        "objective": "Apply the module's decision criteria to a realistic case.",
        "discussion": "Discussion 2",
        "intro": "Read your case. Decide what the organization should do, tick the reasons that drove "
                 "your decision, and name the one piece of evidence you relied on most.",
        "variants": [
            "A regional bakery chain is deciding whether to open a fourth store or add delivery to its three stores.",
            "A hospital clinic is deciding whether to extend evening hours or add a second morning shift.",
            "A software startup is deciding whether to hire a support lead now or after the next funding round.",
            "A city library is deciding whether to replace printed newspapers with digital subscriptions.",
            "A nonprofit is deciding whether to run one large fundraiser or four smaller ones.",
            "A campus cafe is deciding whether to launch a loyalty program or lower prices.",
        ],
        "fields": [
            {"name": "decision", "type": "choice", "label": "1. My decision",
             "options": ["Do it now", "Do it later", "Do not do it", "Do something else"]},
            {"name": "reasons", "type": "checks", "label": "2. What drove the decision (tick any)",
             "options": ["Cost", "Risk", "Customer or user impact", "Staff capacity", "Timing", "Evidence from data"]},
            {"name": "evidence", "type": "text", "label": "3. The evidence I relied on most, and why"},
        ],
    },
    {
        "slug": "m3",
        "module": 3,
        "title": "The shape of the question",
        "objective": "Describe a real question in terms of the inputs it needs and the outputs it produces.",
        "discussion": "Discussion 3",
        "intro": "Write a question from your own work or life. Name what goes in and what comes out, then "
                 "decide whether a spreadsheet is enough or whether it needs code, and why.",
        "variants": [],
        "fields": [
            {"name": "question", "type": "short", "label": "1. My question"},
            {"name": "inputs", "type": "text", "label": "2. Inputs: what data comes in (one per line, with an example)"},
            {"name": "outputs", "type": "text", "label": "3. Outputs: what I would hand back (one per line)"},
            {"name": "tool", "type": "choice", "label": "4. Which tool?",
             "options": ["A spreadsheet is fine", "This needs code", "Either: depends on scale"]},
            {"name": "why", "type": "checks", "label": "5. Where a spreadsheet would break (tick any)",
             "options": ["Too many rows", "Has to run every week", "Needs several tables joined",
                         "Needs cleaning first", "Someone else must re-run it exactly"]},
        ],
    },
]
