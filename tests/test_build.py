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


if __name__ == "__main__":
    unittest.main()
