import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = (ROOT / "skills/evidence-delivery-loop/SKILL.md").read_text(encoding="utf-8")
ROUTING = (ROOT / "skills/evidence-delivery-loop/references/format-routing.md").read_text(encoding="utf-8")
OUTPUT = (ROOT / "skills/evidence-delivery-loop/references/output-contract.md").read_text(encoding="utf-8")
OPENAI_YAML = (ROOT / "skills/evidence-delivery-loop/agents/openai.yaml").read_text(encoding="utf-8")


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
        self.assertRegex(SKILL, r"Do not\s+fabricate\s+findings")
        self.assertIn("untrusted data", SKILL)

    def test_format_contract_covers_requested_routes(self):
        for marker in ("Markdown", "JSON", "YAML", "CSV", "DOCX", "PDF", "PPTX", "XLSX", "IPYNB"):
            self.assertIn(marker, ROUTING)
        self.assertIn("capability_gap", ROUTING)


class EntrypointAndOutputContractTests(unittest.TestCase):
    def test_discovery_description_is_short_and_trigger_focused(self):
        match = re.search(r'(?m)^description: "([^"]+)"$', SKILL)
        self.assertIsNotNone(match)
        description = match.group(1)
        self.assertLessEqual(len(description), 240)
        self.assertEqual(
            description,
            "Use when a multi-material submission, delivery package, or cross-file review "
            "requires a traceable audit and follow-through; not for isolated edits, "
            "explanations, or one-off fixes.",
        )

    def test_entrypoint_is_a_bounded_conditional_router(self):
        body = SKILL.split("---", 2)[2]
        self.assertLessEqual(len(re.findall(r"\b[\w'-]+\b", body)), 1100)
        self.assertLessEqual(len(body.splitlines()), 220)
        for relative in (
            "references/safety-matrix.md",
            "references/format-routing.md",
            "references/output-contract.md",
        ):
            self.assertRegex(SKILL, rf"\[[^\]]+\]\({re.escape(relative)}\)")

    def test_default_prompt_requires_explicit_authorization_before_writes(self):
        self.assertIn(
            "使用 $evidence-delivery-loop 审计我的跨文件交付材料；先给出范围、证据和安全等级，再在我明确授权后创建或修改文件。",
            OPENAI_YAML,
        )

    def test_output_contract_keeps_audit_only_results_in_conversation(self):
        self.assertIn("Without S1 authorization", OUTPUT)
        self.assertIn("conversation", OUTPUT)
        self.assertNotIn("write full evidence to the output directory", OUTPUT)


if __name__ == "__main__":
    unittest.main()
