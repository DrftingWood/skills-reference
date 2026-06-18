"""Generate the local skills reference site from data/skills.json."""
import html
import json
import pathlib
import shutil

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
<h3>{html.escape(skill['name'])} <span class="badge usage-{html.escape(skill['usage'])}">{html.escape(skill['usage'])}</span></h3>
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


def render_index(skills):
    total = len(skills)
    sections = []
    for cat in CATEGORIES:
        rows = []
        for s in skills:
            if s["category"] != cat:
                continue
            slug = slugify(s["name"])
            rows.append(
                f'<li data-usage="{html.escape(s["usage"])}">'
                f'<a href="{cat}.html#{slug}">{html.escape(s["name"])}</a>'
                f' <span class="badge usage-{html.escape(s["usage"])}">{html.escape(s["usage"])}</span>'
                f' — {html.escape(s["tagline"])}</li>'
            )
        if rows:
            sections.append(f'<h2>{cat.title()} ({len(rows)})</h2><ul class="skill-list">' + "".join(rows) + "</ul>")
    controls = (
        '<div class="filter">Filter by usage: '
        + '<button data-filter="all">all</button> '
        + " ".join(f'<button data-filter="{html.escape(u)}">{u}</button>' for u in USAGE_VALUES)
        + "</div>"
    )
    script = """<script>
document.querySelectorAll('.filter button').forEach(function(b){
  b.addEventListener('click', function(){
    var f = b.getAttribute('data-filter');
    document.querySelectorAll('.skill-list li').forEach(function(li){
      li.style.display = (f === 'all' || li.getAttribute('data-usage') === f) ? '' : 'none';
    });
  });
});
</script>"""
    body = f'<p class="summary">{total} skills total.</p>{controls}' + "".join(sections) + script
    return templates.page_shell("Skills Reference", body, render_nav("index.html"))


def load_curated(path):
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8"))


def render_cheatsheet(skills):
    rows = []
    for s in sorted(skills, key=lambda x: x["name"]):
        trig = ", ".join(html.escape(t) for t in s["triggers"]) or "—"
        rows.append(f"<tr><td>{html.escape(s['name'])}</td><td>{trig}</td></tr>")
    body = ('<table class="cheatsheet"><thead><tr><th>Skill</th><th>Triggers</th></tr></thead>'
            '<tbody>' + "".join(rows) + "</tbody></table>")
    return templates.page_shell("Trigger Cheatsheet", body, render_nav("cheatsheet.html"))


def render_combos(skills, curated):
    seen = []
    for chain in curated.get("golden_paths", []):
        if chain not in seen:
            seen.append(chain)
    for s in skills:
        for chain in s["combos"]:
            if chain not in seen:
                seen.append(chain)
    items = "".join(f"<li>{html.escape(c)}</li>" for c in seen)
    body = f'<p>Workflow chains worth reusing.</p><ul class="combos">{items}</ul>'
    return templates.page_shell("Skill Combos", body, render_nav("combos.html"))


def render_overlap(skills):
    blocks = []
    for s in skills:
        if not s["overlaps_with"]:
            continue
        items = "".join(f"<li>{html.escape(o)}</li>" for o in s["overlaps_with"])
        blocks.append(f'<div class="overlap"><h3>{html.escape(s["name"])}</h3><ul>{items}</ul></div>')
    body = '<p>Skills that look similar — when to pick which.</p>' + "".join(blocks)
    return templates.page_shell("Overlap Map", body, render_nav("overlap.html"))


PAGES_REQUIRING_CATEGORY = {c: f"{c}.html" for c in CATEGORIES}


def render_decision_guide(skills, curated):
    by_name = {s["name"]: s for s in skills}
    blocks = []
    for grp in curated.get("decision_groups", []):
        items = []
        for nm in grp["skills"]:
            if nm in by_name:
                cat = by_name[nm]["category"]
                items.append(f'<li><a href="{cat}.html#{slugify(nm)}">{html.escape(nm)}</a></li>')
            else:
                items.append(f"<li>{html.escape(nm)}</li>")
        blocks.append(f'<div class="dg"><h3>{html.escape(grp["situation"])}</h3>'
                      f'<ul>{"".join(items)}</ul></div>')
    body = '<p>Pick the right skill for the situation.</p>' + "".join(blocks)
    return templates.page_shell("Decision Guide", body, render_nav("decision-guide.html"))


def build_site(root):
    root = pathlib.Path(root)
    skills = load_skills(root / "data" / "skills.json")
    validate(skills)
    curated = load_curated(root / "data" / "curated.json")
    out = root / "site"
    (out / "assets").mkdir(parents=True, exist_ok=True)
    pages = {
        "index.html": render_index(skills),
        "decision-guide.html": render_decision_guide(skills, curated),
        "cheatsheet.html": render_cheatsheet(skills),
        "combos.html": render_combos(skills, curated),
        "overlap.html": render_overlap(skills),
    }
    for cat in CATEGORIES:
        pages[f"{cat}.html"] = render_category_page(cat, skills)
    written = []
    for name, content in pages.items():
        (out / name).write_text(content, encoding="utf-8")
        written.append(str(out / name))
    shutil.copyfile(root / "assets" / "style.css", out / "assets" / "style.css")
    return written


def verify_site(root, skills):
    root = pathlib.Path(root)
    out = root / "site"
    problems = []
    for s in skills:
        page = out / f"{s['category']}.html"
        if not page.exists():
            problems.append(f"missing page {page.name}")
            continue
        if f'id="{slugify(s["name"])}"' not in page.read_text(encoding="utf-8"):
            problems.append(f"{s['name']}: anchor missing from {page.name}")
    index = (out / "index.html").read_text(encoding="utf-8")
    import re
    for href in re.findall(r'href="([^"]+\.html(?:#[^"]+)?)"', index):
        file_part, _, anchor = href.partition("#")
        target = out / file_part
        if not target.exists():
            problems.append(f"index links to missing file {file_part}")
        elif anchor and f'id="{anchor}"' not in target.read_text(encoding="utf-8"):
            problems.append(f"index links to missing anchor #{anchor} in {file_part}")
    return problems


def main():
    root = pathlib.Path(__file__).resolve().parent
    skills = load_skills(root / "data" / "skills.json")
    written = build_site(root)
    problems = verify_site(root, skills)
    print(f"Wrote {len(written)} pages to {root / 'site'}")
    if problems:
        print("VERIFY FAILED:")
        for p in problems:
            print("  -", p)
        raise SystemExit(1)
    print("Verify clean.")


if __name__ == "__main__":
    main()
