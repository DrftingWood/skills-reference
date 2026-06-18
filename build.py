"""Generate the local skills reference site from data/skills.json."""
import html
import json
import pathlib

CATEGORIES = ("personal", "superpowers", "builtin", "mcp")
USAGE_VALUES = ("often", "sometimes", "rarely", "never-yet", "unrated")
REQUIRED_FIELDS = (
    "name", "category", "tagline", "triggers", "deep_dive",
    "use_when", "not_for", "combos", "overlaps_with", "usage", "source",
)


def slugify(name):
    out = []
    for ch in name.lower():
        out.append(ch if ch.isalnum() else "-")
    slug = "".join(out)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")


def load_skills(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def validate(skills):
    problems = []
    seen = set()
    for i, s in enumerate(skills):
        label = s.get("name", f"<entry {i}>")
        for f in REQUIRED_FIELDS:
            if f not in s:
                problems.append(f"{label}: missing field '{f}'")
        if s.get("category") not in CATEGORIES:
            problems.append(f"{label}: bad category {s.get('category')!r}")
        if s.get("usage") not in USAGE_VALUES:
            problems.append(f"{label}: bad usage {s.get('usage')!r}")
        if s.get("name") in seen:
            problems.append(f"{label}: duplicate name")
        seen.add(s.get("name"))
    if problems:
        raise ValueError("Invalid skills.json:\n" + "\n".join(problems))
