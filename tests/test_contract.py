import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "skills/evidence-delivery-loop/SKILL.md").read_text(encoding="utf-8")
ROUTING = (ROOT / "skills/evidence-delivery-loop/references/format-routing.md").read_text(encoding="utf-8")


class ContractTests(unittest.TestCase):
    def test_safety_levels_are_explicit(self):
        for level in ("S0", "S1", "S2", "S3", "S4"):
            self.assertIn(level, SKILL)

    def test_workflow_has_review_and_second_cycle(self):
        self.assertIn("Audit retrospective and root cause", SKILL)
        self.assertIn("Solution plan and plan review", SKILL)
        self.assertIn("one second cycle", SKILL)

    def test_provenance_boundary_is_explicit(self):
        self.assertIn("AI-detection score", SKILL)
        self.assertIn("Do not fabricate findings", SKILL)
        self.assertIn("untrusted data", SKILL)

    def test_format_contract_covers_requested_routes(self):
        for marker in ("Markdown", "JSON", "YAML", "CSV", "DOCX", "PDF", "PPTX", "XLSX", "IPYNB"):
            self.assertIn(marker, ROUTING)
        self.assertIn("capability_gap", ROUTING)


if __name__ == "__main__":
    unittest.main()
