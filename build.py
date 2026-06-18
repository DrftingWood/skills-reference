"""Generate the local skills reference site from data/skills.json."""
import html
import json
import pathlib

import templates

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


NAV_LINKS = [
    ("index.html", "Home"),
    ("personal.html", "Personal"),
    ("superpowers.html", "Superpowers"),
    ("builtin.html", "Built-in"),
    ("mcp.html", "MCP"),
    ("decision-guide.html", "Decision Guide"),
    ("cheatsheet.html", "Cheatsheet"),
    ("combos.html", "Combos"),
    ("overlap.html", "Overlap"),
]


def render_nav(active_href):
    items = []
    for href, label in NAV_LINKS:
        cls = ' class="active"' if href == active_href else ""
        items.append(f'<a href="{href}"{cls}>{html.escape(label)}</a>')
    return '<nav>' + " ".join(items) + '</nav>'


def _li(items):
    return "".join(f"<li>{html.escape(x)}</li>" for x in items)


def render_skill_card(skill):
    slug = slugify(skill["name"])
    triggers = ", ".join(html.escape(t) for t in skill["triggers"])
    return f"""<article id="{slug}" class="skill">
<h3>{html.escape(skill['name'])} <span class="badge usage-{skill['usage']}">{html.escape(skill['usage'])}</span></h3>
<p class="tagline">{html.escape(skill['tagline'])}</p>
<p class="triggers"><strong>Triggers:</strong> {triggers}</p>
<div class="deep-dive">{html.escape(skill['deep_dive'])}</div>
<div class="cols">
<div><strong>Use when</strong><ul>{_li(skill['use_when'])}</ul></div>
<div><strong>Not for</strong><ul>{_li(skill['not_for'])}</ul></div>
</div>
<p class="source"><small>Source: {html.escape(skill['source'])}</small></p>
</article>"""


def render_category_page(category, skills):
    cards = "\n".join(render_skill_card(s) for s in skills if s["category"] == category)
    body = f'<section class="cards">{cards}</section>'
    return templates.page_shell(f"{category.title()} skills", body, render_nav(f"{category}.html"))
