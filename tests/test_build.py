import json
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import build  # noqa: E402


def _entry(**over):
    base = {
        "name": "demo-skill",
        "category": "personal",
        "tagline": "Does a demo thing",
        "triggers": ["/demo"],
        "deep_dive": "It demonstrates.",
        "use_when": ["demonstrating"],
        "not_for": ["production"],
        "combos": ["demo-skill → other"],
        "overlaps_with": ["other (different output)"],
        "usage": "unrated",
        "source": "built-in def",
    }
    base.update(over)
    return base


class TestSlugify(unittest.TestCase):
    def test_lowercases_and_dashes(self):
        self.assertEqual(build.slugify("Google Sheets!"), "google-sheets")

    def test_collapses_repeats(self):
        self.assertEqual(build.slugify("a -- b"), "a-b")


class TestValidate(unittest.TestCase):
    def test_accepts_valid(self):
        build.validate([_entry()])  # should not raise

    def test_rejects_missing_field(self):
        bad = _entry()
        del bad["tagline"]
        with self.assertRaises(ValueError):
            build.validate([bad])

    def test_rejects_bad_category(self):
        with self.assertRaises(ValueError):
            build.validate([_entry(category="nope")])

    def test_rejects_bad_usage(self):
        with self.assertRaises(ValueError):
            build.validate([_entry(usage="lots")])


class TestLoadSkills(unittest.TestCase):
    def test_loads_list(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "s.json"
            p.write_text(json.dumps([_entry()]), encoding="utf-8")
            self.assertEqual(len(build.load_skills(p)), 1)


class TestCategoryPage(unittest.TestCase):
    def test_contains_each_skill_anchor(self):
        skills = [_entry(name="alpha"), _entry(name="beta")]
        page = build.render_category_page("personal", skills)
        self.assertIn('id="alpha"', page)
        self.assertIn('id="beta"', page)

    def test_only_includes_matching_category(self):
        skills = [_entry(name="alpha", category="personal"),
                  _entry(name="beta", category="mcp")]
        page = build.render_category_page("personal", skills)
        self.assertIn('id="alpha"', page)
        self.assertNotIn('id="beta"', page)

    def test_escapes_html_in_content(self):
        page = build.render_category_page("personal", [_entry(tagline="a < b & c")])
        self.assertIn("a &lt; b &amp; c", page)
        self.assertNotIn("a < b & c", page)

    def test_shows_usage_badge(self):
        page = build.render_category_page("personal", [_entry(usage="often")])
        self.assertIn("often", page)


class TestIndex(unittest.TestCase):
    def test_links_to_category_anchor(self):
        page = build.render_index([_entry(name="alpha", category="mcp")])
        self.assertIn('href="mcp.html#alpha"', page)

    def test_marks_usage_for_filtering(self):
        page = build.render_index([_entry(name="alpha", usage="never-yet")])
        self.assertIn('data-usage="never-yet"', page)

    def test_shows_total_count(self):
        page = build.render_index([_entry(name="a"), _entry(name="b")])
        self.assertIn("2 skills total", page)


class TestEfficiencyPages(unittest.TestCase):
    def test_cheatsheet_lists_triggers(self):
        page = build.render_cheatsheet([_entry(name="alpha", triggers=["/alpha", "do alpha"])])
        self.assertIn("alpha", page)
        self.assertIn("/alpha", page)
        self.assertIn("do alpha", page)

    def test_combos_includes_golden_paths_and_entry_combos(self):
        curated = {"golden_paths": ["brainstorming → writing-plans → TDD"], "decision_groups": []}
        page = build.render_combos([_entry(combos=["alpha → beta"])], curated)
        self.assertIn("brainstorming → writing-plans → TDD", page)
        self.assertIn("alpha → beta", page)

    def test_combos_dedupes(self):
        curated = {"golden_paths": [], "decision_groups": []}
        page = build.render_combos(
            [_entry(name="a", combos=["x → y"]), _entry(name="b", combos=["x → y"])], curated)
        self.assertEqual(page.count("x → y"), 1)

    def test_overlap_only_lists_entries_with_overlaps(self):
        page = build.render_overlap([_entry(name="alpha", overlaps_with=["beta (different)"]),
                                     _entry(name="lonely", overlaps_with=[])])
        self.assertIn("alpha", page)
        self.assertIn("beta (different)", page)
        self.assertNotIn(">lonely<", page)


if __name__ == "__main__":
    unittest.main()
