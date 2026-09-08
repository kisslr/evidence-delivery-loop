import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_skill import parse_frontmatter, scan_text, validate_frontmatter, validate_repo


class ValidatorTests(unittest.TestCase):
    def test_repository_is_valid(self):
        self.assertEqual(validate_repo(ROOT), [])

    def test_unknown_frontmatter_key_is_rejected(self):
        content = '---\nname: sample\ndescription: "ok"\nowner: "test"\n---\n'
        with self.assertRaisesRegex(ValueError, "unexpected frontmatter key"):
            parse_frontmatter(content)

    def test_invalid_name_is_detectable_by_repository_check(self):
        content = '---\nname: sample--bad\ndescription: "ok"\n---\n'
        self.assertIn("skill name is not valid hyphen-case", validate_frontmatter(content))

    def test_missing_frontmatter_is_rejected(self):
        self.assertTrue(validate_frontmatter("# no metadata\n"))

    def test_sensitive_pattern_is_reported_without_echoing_value(self):
        matches = scan_text("api_" + "key=not-a-real-secret-value")
        self.assertTrue(matches)
        self.assertNotIn("not-a-real-secret-value", matches)

    def test_injection_fixture_is_data(self):
        fixture = (ROOT / "examples/prompt-injection-material.txt").read_text(encoding="utf-8")
        self.assertIn("not instructions for the agent", fixture)


if __name__ == "__main__":
    unittest.main()
