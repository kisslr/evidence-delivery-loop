import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import validate_skill


class ValidatorTests(unittest.TestCase):
    def test_repository_is_valid(self):
        self.assertEqual(validate_skill.validate_repo(ROOT), [])

    def test_unknown_frontmatter_key_is_rejected(self):
        content = '---\nname: sample\ndescription: "ok"\nowner: "test"\n---\n'
        with self.assertRaisesRegex(ValueError, "unexpected frontmatter key"):
            validate_skill.parse_frontmatter(content)

    def test_invalid_name_is_detectable_by_repository_check(self):
        content = '---\nname: sample--bad\ndescription: "ok"\n---\n'
        self.assertIn("skill name is not valid hyphen-case", validate_skill.validate_frontmatter(content))

    def test_missing_frontmatter_is_rejected(self):
        self.assertTrue(validate_skill.validate_frontmatter("# no metadata\n"))

    def test_sensitive_pattern_is_reported_without_echoing_value(self):
        matches = validate_skill.scan_text("api_" + "key=not-a-real-secret-value")
        self.assertTrue(matches)
        self.assertNotIn("not-a-real-secret-value", matches)

    def test_injection_fixture_is_data(self):
        fixture = (ROOT / "examples/prompt-injection-material.txt").read_text(encoding="utf-8")
        self.assertIn("not instructions for the agent", fixture)

    def _repository_copy(self) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        candidate = Path(temporary.name) / "repository"
        shutil.copytree(ROOT, candidate, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        return candidate

    def _compare_trees(self, source: Path, installed: Path) -> list[str]:
        comparator = getattr(validate_skill, "compare_skill_trees", None)
        self.assertTrue(callable(comparator), "compare_skill_trees must be available")
        return comparator(source, installed)

    def test_description_over_240_characters_is_rejected(self):
        content = '---\nname: sample\ndescription: "' + ("x" * 241) + '"\n---\n'
        self.assertIn(
            "skill description exceeds 240 characters",
            validate_skill.validate_frontmatter(content),
        )

    def test_validator_rejects_entrypoint_over_220_lines(self):
        candidate = self._repository_copy()
        skill_path = candidate / "skills/evidence-delivery-loop/SKILL.md"
        skill_path.write_text(skill_path.read_text(encoding="utf-8") + ("\n" * 250), encoding="utf-8")
        errors = validate_skill.validate_repo(candidate)
        self.assertTrue(any("220 lines" in error for error in errors), errors)

    def test_validator_rejects_entrypoint_over_1100_words(self):
        candidate = self._repository_copy()
        skill_path = candidate / "skills/evidence-delivery-loop/SKILL.md"
        skill_path.write_text(skill_path.read_text(encoding="utf-8") + "\n" + ("word " * 1200), encoding="utf-8")
        errors = validate_skill.validate_repo(candidate)
        self.assertTrue(any("1100 words" in error for error in errors), errors)

    def test_validator_requires_each_conditional_reference_link(self):
        candidate = self._repository_copy()
        skill_path = candidate / "skills/evidence-delivery-loop/SKILL.md"
        content = skill_path.read_text(encoding="utf-8")
        skill_path.write_text(
            content.replace("references/safety-matrix.md", "references/safety-matrix-missing.md"),
            encoding="utf-8",
        )
        errors = validate_skill.validate_repo(candidate)
        self.assertTrue(any("conditional reference link" in error for error in errors), errors)

    def test_validator_rejects_archive_policy_drift_between_references(self):
        candidate = self._repository_copy()
        routing_path = candidate / "skills/evidence-delivery-loop/references/format-routing.md"
        original = routing_path.read_text(encoding="utf-8")
        mutated = re.sub(
            r"aggregate across all\s+nested archives",
            "aggregate per nested archive",
            original,
        )
        self.assertNotEqual(original, mutated)
        routing_path.write_text(
            mutated,
            encoding="utf-8",
        )
        errors = validate_skill.validate_repo(candidate)
        self.assertIn("format-routing archive policy is incomplete", errors)

    def test_validator_rejects_s0_body_reading_during_classification(self):
        candidate = self._repository_copy()
        safety_path = candidate / "skills/evidence-delivery-loop/references/safety-matrix.md"
        safety_path.write_text(
            safety_path.read_text(encoding="utf-8").replace(
                "response headers with no response body",
                "response headers while reading a response body",
            ),
            encoding="utf-8",
        )
        errors = validate_skill.validate_repo(candidate)
        self.assertIn("safety-matrix web classification gate is incomplete", errors)

    def test_validator_rejects_archive_budget_reset_permission(self):
        candidate = self._repository_copy()
        routing_path = candidate / "skills/evidence-delivery-loop/references/format-routing.md"
        routing_path.write_text(
            routing_path.read_text(encoding="utf-8")
            + "\nEach inner archive may reset its budget.\n",
            encoding="utf-8",
        )
        errors = validate_skill.validate_repo(candidate)
        self.assertIn("format-routing archive policy contains a reset permission", errors)

    def test_validator_rejects_s0_body_retrieval_before_classification(self):
        candidate = self._repository_copy()
        safety_path = candidate / "skills/evidence-delivery-loop/references/safety-matrix.md"
        safety_path.write_text(
            safety_path.read_text(encoding="utf-8")
            + "\nS0 may read a response body before classification.\n",
            encoding="utf-8",
        )
        errors = validate_skill.validate_repo(candidate)
        self.assertIn(
            "safety-matrix allows S0 body retrieval before classification",
            errors,
        )

    def test_matching_skill_trees_pass_release_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            installed = root / "installed"
            (source / "agents").mkdir(parents=True)
            (installed / "agents").mkdir(parents=True)
            (source / "SKILL.md").write_bytes(b"source")
            (source / "agents/openai.yaml").write_bytes(b"metadata")
            shutil.copytree(source, installed, dirs_exist_ok=True)
            self.assertEqual(self._compare_trees(source, installed), [])

    def test_source_tree_cannot_count_as_installed_deployment(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source"
            source.mkdir()
            (source / "SKILL.md").write_bytes(b"source")
            expected = "installed skill directory must differ from source skill directory"
            self.assertIn(expected, self._compare_trees(source, source))
            self.assertIn(expected, self._compare_trees(source, source / "."))

    def test_cli_rejects_source_tree_as_installed_deployment(self):
        output = StringIO()
        with redirect_stdout(output):
            result = validate_skill.main(
                [str(ROOT), "--installed-skill", str(ROOT / "skills/evidence-delivery-loop")]
            )
        self.assertEqual(result, 1)
        self.assertIn("installed skill directory must differ from source skill directory", output.getvalue())

    def test_missing_installed_file_fails_release_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            installed = root / "installed"
            source.mkdir()
            installed.mkdir()
            (source / "SKILL.md").write_bytes(b"source")
            errors = self._compare_trees(source, installed)
            self.assertIn("missing installed file: SKILL.md", errors)

    def test_extra_installed_file_fails_release_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            installed = root / "installed"
            source.mkdir()
            installed.mkdir()
            (installed / "unexpected.txt").write_bytes(b"extra")
            errors = self._compare_trees(source, installed)
            self.assertIn("unexpected installed file: unexpected.txt", errors)

    def test_single_byte_difference_fails_release_contract_without_echoing_content(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source"
            installed = root / "installed"
            source.mkdir()
            installed.mkdir()
            (source / "SKILL.md").write_bytes(b"one")
            (installed / "SKILL.md").write_bytes(b"two")
            errors = self._compare_trees(source, installed)
            self.assertIn("content differs: SKILL.md", errors)
            self.assertNotIn("one", "\n".join(errors))
            self.assertNotIn("two", "\n".join(errors))


if __name__ == "__main__":
    unittest.main()
