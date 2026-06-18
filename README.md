# Skills Reference

A local static site that documents all Claude Code skills available in this environment — what each skill does, when to trigger it, how it compares to overlapping skills, and common workflow chains.

## What it is

61 skills across four categories (Personal, Superpowers, Built-in, MCP) are stored as structured JSON in `data/skills.json`. The build script reads that data, validates it, and renders a set of nine interlinked HTML pages to `site/`. No server is needed — open the HTML files directly in any browser.

## Viewing the site

Open `site/index.html` in your browser. From there you can:

- Filter skills by usage frequency using the filter buttons at the top.
- Navigate to category pages (Personal, Superpowers, Built-in, MCP) for full skill cards.
- Use the Decision Guide to find the right skill for a given situation.
- Use the Cheatsheet for a compact trigger-word reference.
- Use the Combos page for recommended workflow chains.
- Use the Overlap page to distinguish skills that look similar.

## Regenerating the site

```
python build.py
```

This validates `data/skills.json`, wipes the existing `site/` directory, writes all nine pages plus `site/assets/style.css`, and runs a link/anchor verification pass. The final line is `Verify clean.` on success.

## Adding a skill

1. Append an entry to `data/skills.json` with all 11 required fields:

   | Field | Type | Notes |
   |---|---|---|
   | `name` | string | Unique, matches the skill's invoke name |
   | `category` | string | One of: `personal`, `superpowers`, `builtin`, `mcp` |
   | `tagline` | string | One-line summary (shown in index list) |
   | `triggers` | array of strings | Phrases/commands that invoke this skill |
   | `deep_dive` | string | Detailed explanation of how the skill works internally |
   | `use_when` | array of strings | Bullet list of when to reach for this skill |
   | `not_for` | array of strings | Bullet list of what this skill does NOT cover |
   | `combos` | array of strings | Suggested chains, e.g. `"foo → bar"` |
   | `overlaps_with` | array of strings | Skills that look similar and how they differ |
   | `usage` | string | See rating convention below |
   | `source` | string | Where the skill lives (path or `"built-in def"`) |

2. Optionally add the skill to a `decision_groups` entry in `data/curated.json`, or reference it in a `golden_paths` chain.

3. Re-run `python build.py`.

## Usage rating convention

The `usage` field is one of five values:

| Value | Meaning |
|---|---|
| `often` | Used frequently — multiple times per week |
| `sometimes` | Used occasionally — a few times per month |
| `rarely` | Used infrequently — a few times total |
| `never-yet` | Skill is installed but has not been used yet |
| `unrated` | No estimate available |

**Note:** The current values in `data/skills.json` are seeded best-guesses based on skill type and expected frequency. They should be updated as actual usage patterns become clear.

## Running tests

```
python -m unittest discover -s tests -v
```

Expected: all tests pass (currently 24 tests).

## Notes

- `site/` is generated output and is listed in `.gitignore`. Do not commit it.
- `data/skills.json` and `data/curated.json` are the source of truth — edit those, then rebuild.
- `build.py` and `templates.py` contain the full rendering logic; no external dependencies beyond the Python standard library.
